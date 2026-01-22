"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VOICEBOT COBRANZAS - ELEVEN LABS TTS                                         ║
║  Conversión de Texto a Voz                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import Optional
import hashlib
import time

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

# Voces recomendadas para español
VOCES = {
    'bella': 'EXAVITQu4vr4xnSDxMaL',      # Mujer, clara
    'rachel': '21m00Tcm4TlvDq8ikWAM',      # Mujer, profesional
    'adam': 'pNInz6obpgDQGcFmaJgB',        # Hombre, confiable
    'josh': 'TxGEqnHWrfWFTfGW9XjX',        # Hombre, amigable
    'arnold': 'VR6AewLTigWG4xSOukaG',      # Hombre, autoritario
}

# Configuración por defecto
DEFAULT_VOICE_ID = VOCES['bella']  # Voz femenina clara para cobranzas
DEFAULT_MODEL = 'eleven_multilingual_v2'

# Caché de audio
AUDIO_CACHE_PATH = Path('./audio_cache')
AUDIO_CACHE_PATH.mkdir(exist_ok=True)

# ============================================================================
# CLIENTE ELEVEN LABS
# ============================================================================

class ElevenLabsTTS:
    """
    Cliente para Eleven Labs Text-to-Speech.
    """
    
    def __init__(
        self,
        api_key: str = ELEVENLABS_API_KEY,
        voice_id: str = DEFAULT_VOICE_ID,
        model: str = DEFAULT_MODEL
    ):
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("⚠️ ELEVENLABS_API_KEY no configurada")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea la sesión HTTP."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    'xi-api-key': self.api_key,
                    'Content-Type': 'application/json'
                }
            )
        return self.session
    
    async def close(self):
        """Cierra la sesión HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _get_cache_path(self, texto: str) -> Path:
        """Genera ruta de caché basada en hash del texto."""
        text_hash = hashlib.md5(f"{texto}_{self.voice_id}".encode()).hexdigest()
        return AUDIO_CACHE_PATH / f"{text_hash}.mp3"
    
    async def texto_a_audio(
        self,
        texto: str,
        output_path: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """
        Convierte texto a audio usando Eleven Labs.
        
        Args:
            texto: Texto a convertir
            output_path: Ruta donde guardar el audio (opcional)
            use_cache: Si usar caché de audio
            
        Returns:
            Ruta al archivo de audio generado
        """
        # Verificar caché
        cache_path = self._get_cache_path(texto)
        if use_cache and cache_path.exists():
            logger.debug(f"🎵 Audio desde caché: {cache_path}")
            if output_path:
                import shutil
                shutil.copy(cache_path, output_path)
                return output_path
            return str(cache_path)
        
        # Llamar a la API
        session = await self._get_session()
        
        url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{self.voice_id}"
        
        payload = {
            "text": texto,
            "model_id": self.model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        try:
            start_time = time.time()
            
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"❌ Error Eleven Labs: {response.status} - {error_text}")
                    raise Exception(f"Error TTS: {response.status}")
                
                audio_data = await response.read()
                
                # Guardar en caché
                with open(cache_path, 'wb') as f:
                    f.write(audio_data)
                
                # Guardar en ruta especificada si existe
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(audio_data)
                    final_path = output_path
                else:
                    final_path = str(cache_path)
                
                elapsed = time.time() - start_time
                logger.info(f"🎵 Audio generado: {len(audio_data)} bytes en {elapsed:.2f}s")
                
                return final_path
                
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión: {e}")
            raise
    
    async def texto_a_audio_stream(self, texto: str):
        """
        Genera audio en streaming (para baja latencia).
        
        Yields:
            Chunks de audio en formato MP3
        """
        session = await self._get_session()
        
        url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{self.voice_id}/stream"
        
        payload = {
            "text": texto,
            "model_id": self.model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
        
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Error TTS stream: {response.status} - {error_text}")
            
            async for chunk in response.content.iter_chunked(1024):
                yield chunk
    
    async def listar_voces(self) -> list:
        """Lista todas las voces disponibles."""
        session = await self._get_session()
        
        url = f"{ELEVENLABS_BASE_URL}/voices"
        
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Error listando voces: {response.status}")
            
            data = await response.json()
            return data.get('voices', [])
    
    async def obtener_cuota(self) -> dict:
        """Obtiene información de cuota/uso."""
        session = await self._get_session()
        
        url = f"{ELEVENLABS_BASE_URL}/user/subscription"
        
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Error obteniendo cuota: {response.status}")
            
            return await response.json()


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

# Cliente global
_tts_client: Optional[ElevenLabsTTS] = None

def get_tts_client() -> ElevenLabsTTS:
    """Obtiene el cliente TTS global."""
    global _tts_client
    if _tts_client is None:
        _tts_client = ElevenLabsTTS()
    return _tts_client

async def texto_a_audio(texto: str, output_path: Optional[str] = None) -> str:
    """
    Función de conveniencia para convertir texto a audio.
    
    Args:
        texto: Texto a convertir
        output_path: Ruta de salida (opcional)
        
    Returns:
        Ruta al archivo de audio
    """
    client = get_tts_client()
    return await client.texto_a_audio(texto, output_path)

def texto_a_audio_sync(texto: str, output_path: Optional[str] = None) -> str:
    """Versión síncrona de texto_a_audio."""
    return asyncio.run(texto_a_audio(texto, output_path))


# ============================================================================
# PRUEBA
# ============================================================================

if __name__ == "__main__":
    async def test():
        print("\n" + "="*60)
        print("🎤 TEST ELEVEN LABS TTS")
        print("="*60 + "\n")
        
        # Verificar API key
        if not ELEVENLABS_API_KEY:
            print("❌ ELEVENLABS_API_KEY no configurada")
            print("   Ejecuta: export ELEVENLABS_API_KEY='tu-api-key'")
            return
        
        client = ElevenLabsTTS()
        
        try:
            # Test 1: Obtener cuota
            print("📊 Obteniendo información de cuenta...")
            cuota = await client.obtener_cuota()
            print(f"   Caracteres usados: {cuota.get('character_count', 'N/A')}")
            print(f"   Límite: {cuota.get('character_limit', 'N/A')}")
            
            # Test 2: Generar audio
            print("\n🎵 Generando audio de prueba...")
            texto = """
            Buenos días, le habla el asistente virtual del Banco de Bogotá.
            El motivo de nuestra llamada es informarle sobre su obligación pendiente.
            """
            
            audio_path = await client.texto_a_audio(texto, "test_audio.mp3")
            print(f"   ✅ Audio guardado en: {audio_path}")
            
            # Test 3: Listar voces
            print("\n🗣️ Voces disponibles:")
            voces = await client.listar_voces()
            for voz in voces[:5]:
                print(f"   - {voz['name']} ({voz['voice_id']})")
            
        finally:
            await client.close()
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETADO")
        print("="*60)
    
    asyncio.run(test())
