"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VOICEBOT COBRANZAS - WHISPER STT                                             ║
║  Conversión de Voz a Texto                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import Optional, Union
import time

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = "https://api.openai.com/v1"

# Modelos disponibles
WHISPER_MODELS = {
    'whisper-1': 'whisper-1',  # Modelo principal de OpenAI
}

DEFAULT_MODEL = 'whisper-1'

# ============================================================================
# CLIENTE WHISPER
# ============================================================================

class WhisperSTT:
    """
    Cliente para OpenAI Whisper Speech-to-Text.
    """
    
    def __init__(
        self,
        api_key: str = OPENAI_API_KEY,
        model: str = DEFAULT_MODEL
    ):
        self.api_key = api_key
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY no configurada")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea la sesión HTTP."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
        return self.session
    
    async def close(self):
        """Cierra la sesión HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def audio_a_texto(
        self,
        audio_path: Union[str, Path],
        language: str = 'es',
        prompt: Optional[str] = None
    ) -> str:
        """
        Convierte audio a texto usando Whisper.
        
        Args:
            audio_path: Ruta al archivo de audio
            language: Código de idioma (es = español)
            prompt: Texto de contexto para mejorar la transcripción
            
        Returns:
            Transcripción del audio
        """
        session = await self._get_session()
        
        url = f"{OPENAI_BASE_URL}/audio/transcriptions"
        
        # Preparar datos del formulario
        data = aiohttp.FormData()
        data.add_field('model', self.model)
        data.add_field('language', language)
        
        if prompt:
            data.add_field('prompt', prompt)
        
        # Agregar archivo de audio
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio no encontrado: {audio_path}")
        
        with open(audio_path, 'rb') as audio_file:
            data.add_field(
                'file',
                audio_file,
                filename=audio_path.name,
                content_type='audio/wav'
            )
            
            try:
                start_time = time.time()
                
                async with session.post(url, data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ Error Whisper: {response.status} - {error_text}")
                        raise Exception(f"Error STT: {response.status}")
                    
                    result = await response.json()
                    transcripcion = result.get('text', '')
                    
                    elapsed = time.time() - start_time
                    logger.info(f"🎤 Transcripción: {len(transcripcion)} chars en {elapsed:.2f}s")
                    
                    return transcripcion
                    
            except aiohttp.ClientError as e:
                logger.error(f"❌ Error de conexión: {e}")
                raise
    
    async def audio_bytes_a_texto(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str = 'es',
        prompt: Optional[str] = None
    ) -> str:
        """
        Convierte bytes de audio a texto.
        
        Args:
            audio_bytes: Datos de audio en bytes
            filename: Nombre del archivo (para determinar formato)
            language: Código de idioma
            prompt: Texto de contexto
            
        Returns:
            Transcripción del audio
        """
        session = await self._get_session()
        
        url = f"{OPENAI_BASE_URL}/audio/transcriptions"
        
        data = aiohttp.FormData()
        data.add_field('model', self.model)
        data.add_field('language', language)
        
        if prompt:
            data.add_field('prompt', prompt)
        
        # Determinar content type
        if filename.endswith('.wav'):
            content_type = 'audio/wav'
        elif filename.endswith('.mp3'):
            content_type = 'audio/mpeg'
        elif filename.endswith('.ogg'):
            content_type = 'audio/ogg'
        else:
            content_type = 'audio/wav'
        
        data.add_field(
            'file',
            audio_bytes,
            filename=filename,
            content_type=content_type
        )
        
        try:
            start_time = time.time()
            
            async with session.post(url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"❌ Error Whisper: {response.status} - {error_text}")
                    raise Exception(f"Error STT: {response.status}")
                
                result = await response.json()
                transcripcion = result.get('text', '')
                
                elapsed = time.time() - start_time
                logger.info(f"🎤 Transcripción (bytes): {len(transcripcion)} chars en {elapsed:.2f}s")
                
                return transcripcion
                
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión: {e}")
            raise


# ============================================================================
# DETECCIÓN DE VOZ (VAD - Voice Activity Detection)
# ============================================================================

class DetectorVoz:
    """
    Detector de actividad de voz simple basado en energía.
    """
    
    def __init__(
        self,
        umbral_energia: float = 0.01,
        duracion_silencio: float = 1.5,
        duracion_minima: float = 0.5
    ):
        """
        Args:
            umbral_energia: Umbral de energía para detectar voz
            duracion_silencio: Segundos de silencio para considerar fin de habla
            duracion_minima: Duración mínima de audio para procesar
        """
        self.umbral_energia = umbral_energia
        self.duracion_silencio = duracion_silencio
        self.duracion_minima = duracion_minima
    
    def detectar_fin_habla(
        self,
        audio_samples: list,
        sample_rate: int = 8000
    ) -> bool:
        """
        Detecta si el usuario terminó de hablar.
        
        Args:
            audio_samples: Lista de muestras de audio
            sample_rate: Tasa de muestreo
            
        Returns:
            True si se detectó fin de habla
        """
        if not audio_samples:
            return False
        
        # Calcular energía de las últimas muestras
        muestras_silencio = int(self.duracion_silencio * sample_rate)
        ultimas_muestras = audio_samples[-muestras_silencio:]
        
        if len(ultimas_muestras) < muestras_silencio:
            return False
        
        # Calcular RMS (Root Mean Square) como medida de energía
        import math
        suma_cuadrados = sum(x * x for x in ultimas_muestras)
        rms = math.sqrt(suma_cuadrados / len(ultimas_muestras))
        
        return rms < self.umbral_energia
    
    def tiene_suficiente_audio(
        self,
        audio_samples: list,
        sample_rate: int = 8000
    ) -> bool:
        """Verifica si hay suficiente audio para procesar."""
        duracion = len(audio_samples) / sample_rate
        return duracion >= self.duracion_minima


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

# Cliente global
_stt_client: Optional[WhisperSTT] = None

def get_stt_client() -> WhisperSTT:
    """Obtiene el cliente STT global."""
    global _stt_client
    if _stt_client is None:
        _stt_client = WhisperSTT()
    return _stt_client

async def audio_a_texto(audio_path: Union[str, Path], language: str = 'es') -> str:
    """
    Función de conveniencia para transcribir audio.
    
    Args:
        audio_path: Ruta al archivo de audio
        language: Código de idioma
        
    Returns:
        Transcripción
    """
    client = get_stt_client()
    
    # Prompt de contexto para mejorar transcripción
    prompt = """
    Conversación telefónica de cobranzas bancarias en español colombiano.
    Términos comunes: sí, no, cuota, pago, banco, tarjeta, crédito, mora, 
    pesos, plata, mañana, hoy, acuerdo, abono.
    """
    
    return await client.audio_a_texto(audio_path, language, prompt)

def audio_a_texto_sync(audio_path: Union[str, Path], language: str = 'es') -> str:
    """Versión síncrona de audio_a_texto."""
    return asyncio.run(audio_a_texto(audio_path, language))


# ============================================================================
# PRUEBA
# ============================================================================

if __name__ == "__main__":
    async def test():
        print("\n" + "="*60)
        print("🎤 TEST WHISPER STT")
        print("="*60 + "\n")
        
        # Verificar API key
        if not OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY no configurada")
            print("   Ejecuta: export OPENAI_API_KEY='tu-api-key'")
            return
        
        client = WhisperSTT()
        
        try:
            # Crear audio de prueba (requiere un archivo de audio real)
            test_audio = Path("test_audio.wav")
            
            if test_audio.exists():
                print(f"📁 Procesando: {test_audio}")
                
                transcripcion = await client.audio_a_texto(
                    test_audio,
                    language='es',
                    prompt="Conversación de cobranzas bancarias"
                )
                
                print(f"\n📝 Transcripción:")
                print(f"   {transcripcion}")
            else:
                print(f"⚠️ No se encontró archivo de prueba: {test_audio}")
                print("   Crea un archivo de audio WAV para probar")
                
                # Test con información de la API
                print("\n📊 Verificando conexión con OpenAI...")
                session = await client._get_session()
                async with session.get(f"{OPENAI_BASE_URL}/models") as response:
                    if response.status == 200:
                        print("   ✅ Conexión exitosa")
                    else:
                        print(f"   ❌ Error: {response.status}")
        
        finally:
            await client.close()
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETADO")
        print("="*60)
    
    asyncio.run(test())
