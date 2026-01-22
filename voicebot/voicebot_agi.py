"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VOICEBOT COBRANZAS - ASTERISK AGI BRIDGE                                     ║
║  Puente entre Asterisk y el Motor de Conversación                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Este script se ejecuta como un AGI (Asterisk Gateway Interface) para manejar
las llamadas entrantes/salientes y coordinar STT/TTS.

Uso en dialplan:
    exten => s,1,AGI(voicebot_agi.py)
"""

import sys
import os
import asyncio
import logging
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Agregar directorio al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor_conversacion import MotorConversacion, DatosCliente, EstadoConversacion
from elevenlabs_tts import ElevenLabsTTS
from whisper_stt import WhisperSTT

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('/var/log/asterisk/voicebot.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CLASE AGI
# ============================================================================

class AsteriskAGI:
    """
    Interfaz para comunicación con Asterisk via AGI.
    """
    
    def __init__(self):
        self.env: Dict[str, str] = {}
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
        # Leer variables de entorno AGI
        self._leer_variables()
    
    def _leer_variables(self):
        """Lee las variables de entorno AGI de stdin."""
        while True:
            line = self.stdin.readline().strip()
            if not line:
                break
            
            if ': ' in line:
                key, value = line.split(': ', 1)
                key = key.replace('agi_', '')
                self.env[key] = value
                logger.debug(f"AGI var: {key} = {value}")
    
    def execute(self, command: str) -> tuple[int, str]:
        """
        Ejecuta un comando AGI.
        
        Args:
            command: Comando AGI a ejecutar
            
        Returns:
            (código_resultado, texto_resultado)
        """
        self.stdout.write(f"{command}\n")
        self.stdout.flush()
        
        response = self.stdin.readline().strip()
        logger.debug(f"AGI response: {response}")
        
        # Parsear respuesta: "200 result=X"
        if response.startswith('200'):
            parts = response.split('=')
            if len(parts) >= 2:
                result = parts[1].split(' ')[0]
                return int(result) if result.lstrip('-').isdigit() else 0, response
        
        return -1, response
    
    def answer(self) -> bool:
        """Contesta la llamada."""
        result, _ = self.execute("ANSWER")
        return result == 0
    
    def hangup(self) -> bool:
        """Cuelga la llamada."""
        result, _ = self.execute("HANGUP")
        return result == 1
    
    def stream_file(self, filename: str, escape_digits: str = "") -> str:
        """
        Reproduce un archivo de audio.
        
        Args:
            filename: Nombre del archivo (sin extensión)
            escape_digits: Dígitos que interrumpen la reproducción
            
        Returns:
            Dígito presionado o cadena vacía
        """
        result, response = self.execute(f'STREAM FILE "{filename}" "{escape_digits}"')
        if result > 0:
            return chr(result)
        return ""
    
    def record_file(
        self,
        filename: str,
        format: str = "wav",
        escape_digits: str = "#",
        timeout: int = 5000,
        silence: int = 3
    ) -> tuple[bool, int]:
        """
        Graba audio del usuario.
        
        Args:
            filename: Nombre del archivo (sin extensión)
            format: Formato de audio (wav, gsm, etc.)
            escape_digits: Dígitos que detienen la grabación
            timeout: Tiempo máximo de grabación (ms)
            silence: Segundos de silencio para detener
            
        Returns:
            (éxito, duración_frames)
        """
        cmd = f'RECORD FILE "{filename}" "{format}" "{escape_digits}" {timeout} BEEP s={silence}'
        result, response = self.execute(cmd)
        
        # Extraer duración si está disponible
        duration = 0
        if 'endpos=' in response:
            try:
                duration = int(response.split('endpos=')[1].split(')')[0])
            except:
                pass
        
        return result >= 0, duration
    
    def set_variable(self, name: str, value: str):
        """Establece una variable de canal."""
        self.execute(f'SET VARIABLE {name} "{value}"')
    
    def get_variable(self, name: str) -> Optional[str]:
        """Obtiene una variable de canal."""
        result, response = self.execute(f'GET VARIABLE {name}')
        if '(' in response and ')' in response:
            return response.split('(')[1].split(')')[0]
        return None
    
    def verbose(self, message: str, level: int = 1):
        """Escribe mensaje en el log de Asterisk."""
        self.execute(f'VERBOSE "{message}" {level}')
    
    def say_digits(self, digits: str, escape_digits: str = "") -> str:
        """Dice dígitos."""
        result, _ = self.execute(f'SAY DIGITS {digits} "{escape_digits}"')
        if result > 0:
            return chr(result)
        return ""
    
    def wait(self, seconds: int) -> str:
        """Espera N segundos."""
        result, _ = self.execute(f'WAIT FOR DIGIT {seconds * 1000}')
        if result > 0:
            return chr(result)
        return ""


# ============================================================================
# VOICEBOT AGI
# ============================================================================

class VoicebotAGI:
    """
    Manejador principal del Voicebot usando AGI.
    """
    
    def __init__(self):
        self.agi = AsteriskAGI()
        self.tts = ElevenLabsTTS()
        self.stt = WhisperSTT()
        self.motor: Optional[MotorConversacion] = None
        
        # Configuración
        self.audio_path = Path('/var/lib/asterisk/sounds/voicebot')
        self.audio_path.mkdir(parents=True, exist_ok=True)
        
        self.temp_path = Path(tempfile.gettempdir()) / 'voicebot'
        self.temp_path.mkdir(parents=True, exist_ok=True)
        
        # Tiempos
        self.timeout_respuesta = 7000  # 7 segundos para responder
        self.silencio_fin = 2  # 2 segundos de silencio = fin de habla
        self.max_duracion = 300  # 5 minutos máximo
    
    async def iniciar(self):
        """Inicia la sesión del voicebot."""
        logger.info("="*60)
        logger.info("🚀 VOICEBOT AGI INICIADO")
        logger.info("="*60)
        
        # Obtener datos del cliente desde variables de canal
        cliente = self._cargar_datos_cliente()
        
        if not cliente:
            logger.error("❌ No se pudieron cargar datos del cliente")
            self.agi.hangup()
            return
        
        # Crear motor de conversación
        self.motor = MotorConversacion(cliente)
        
        # Contestar llamada
        self.agi.answer()
        logger.info(f"📞 Llamada contestada: {cliente.celular}")
        
        # Ejecutar flujo de conversación
        try:
            await self._ejecutar_conversacion()
        except Exception as e:
            logger.error(f"❌ Error en conversación: {e}")
        finally:
            # Guardar resultado
            self._guardar_resultado()
            
            # Cerrar conexiones
            await self.tts.close()
            await self.stt.close()
            
            # Colgar
            self.agi.hangup()
    
    def _cargar_datos_cliente(self) -> Optional[DatosCliente]:
        """Carga los datos del cliente desde variables de canal."""
        try:
            # Variables esperadas del dialplan
            cedula = self.agi.get_variable('CLIENTE_CEDULA') or ''
            nombre = self.agi.get_variable('CLIENTE_NOMBRE') or ''
            celular = self.agi.get_variable('CLIENTE_CELULAR') or self.agi.env.get('callerid', '')
            producto = self.agi.get_variable('CLIENTE_PRODUCTO') or ''
            tipo_producto = self.agi.get_variable('CLIENTE_TIPO_PRODUCTO') or ''
            dias_mora = int(self.agi.get_variable('CLIENTE_DIAS_MORA') or '0')
            saldo_mora = float(self.agi.get_variable('CLIENTE_SALDO_MORA') or '0')
            pago_minimo = float(self.agi.get_variable('CLIENTE_PAGO_MINIMO') or '0')
            gac = float(self.agi.get_variable('CLIENTE_GAC') or '0')
            total_a_pagar = float(self.agi.get_variable('CLIENTE_TOTAL_PAGAR') or '0')
            tiene_campana = self.agi.get_variable('CLIENTE_TIENE_CAMPANA') == 'true'
            mecanismo = self.agi.get_variable('CLIENTE_MECANISMO')
            probabilidad = float(self.agi.get_variable('CLIENTE_PROBABILIDAD') or '0')
            segmento = self.agi.get_variable('CLIENTE_SEGMENTO') or 'D'
            
            # Scripts
            script_oferta = self.agi.get_variable('CLIENTE_SCRIPT_OFERTA') or ''
            script_abono = self.agi.get_variable('CLIENTE_SCRIPT_ABONO') or ''
            
            return DatosCliente(
                cedula=cedula,
                nombre=nombre,
                celular=celular,
                producto=producto,
                tipo_producto=tipo_producto,
                dias_mora=dias_mora,
                saldo_mora=saldo_mora,
                pago_minimo=pago_minimo,
                gac=gac,
                total_a_pagar=total_a_pagar,
                tiene_campana=tiene_campana,
                mecanismo=mecanismo,
                probabilidad_pago=probabilidad,
                segmento=segmento,
                script_oferta=script_oferta,
                script_abono=script_abono
            )
            
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            return None
    
    async def _ejecutar_conversacion(self):
        """Ejecuta el flujo principal de conversación."""
        inicio = time.time()
        
        while True:
            # Verificar tiempo máximo
            if time.time() - inicio > self.max_duracion:
                logger.warning("⏰ Tiempo máximo alcanzado")
                break
            
            # Obtener siguiente mensaje del bot
            mensaje, estado = self.motor.obtener_siguiente_mensaje()
            
            # Si hay mensaje, reproducirlo
            if mensaje:
                await self._hablar(mensaje)
            
            # Si llegamos al fin, salir
            if estado == EstadoConversacion.FIN:
                break
            
            # Estados que esperan respuesta del cliente
            estados_espera = [
                EstadoConversacion.SALUDO,
                EstadoConversacion.IDENTIFICACION,
                EstadoConversacion.ESPERA_RESPUESTA_OFERTA,
                EstadoConversacion.ESPERA_RESPUESTA_ABONO
            ]
            
            if estado in estados_espera:
                # Escuchar respuesta
                respuesta = await self._escuchar()
                
                if respuesta is None:
                    # No hubo respuesta, puede ser que colgaron
                    logger.warning("⚠️ Sin respuesta del cliente")
                    break
                
                # Procesar respuesta
                mensaje, estado = self.motor.obtener_siguiente_mensaje(respuesta)
                
                if mensaje:
                    await self._hablar(mensaje)
                
                if estado == EstadoConversacion.FIN:
                    break
    
    async def _hablar(self, texto: str):
        """
        Convierte texto a voz y lo reproduce.
        
        Args:
            texto: Texto a hablar
        """
        logger.info(f"🤖 Bot dice: {texto[:50]}...")
        
        try:
            # Generar audio con Eleven Labs
            audio_file = self.temp_path / f"tts_{int(time.time()*1000)}.mp3"
            await self.tts.texto_a_audio(texto, str(audio_file))
            
            # Convertir a formato Asterisk (WAV 8kHz mono)
            wav_file = audio_file.with_suffix('.wav')
            os.system(f'ffmpeg -y -i "{audio_file}" -ar 8000 -ac 1 "{wav_file}" 2>/dev/null')
            
            # Copiar a directorio de Asterisk
            asterisk_file = self.audio_path / wav_file.name
            os.system(f'cp "{wav_file}" "{asterisk_file}"')
            
            # Reproducir (sin extensión)
            filename = str(asterisk_file).replace('.wav', '')
            self.agi.stream_file(filename)
            
            # Limpiar archivos temporales
            audio_file.unlink(missing_ok=True)
            wav_file.unlink(missing_ok=True)
            
        except Exception as e:
            logger.error(f"❌ Error en TTS: {e}")
            self.agi.verbose(f"Error TTS: {e}", 1)
    
    async def _escuchar(self) -> Optional[str]:
        """
        Graba y transcribe la respuesta del cliente.
        
        Returns:
            Transcripción o None si no hubo audio
        """
        logger.info("🎤 Escuchando...")
        
        try:
            # Grabar audio
            record_file = self.temp_path / f"record_{int(time.time()*1000)}"
            
            success, duration = self.agi.record_file(
                str(record_file),
                format="wav",
                escape_digits="#",
                timeout=self.timeout_respuesta,
                silence=self.silencio_fin
            )
            
            wav_file = Path(f"{record_file}.wav")
            
            if not success or not wav_file.exists():
                logger.warning("⚠️ No se grabó audio")
                return None
            
            # Verificar que hay audio
            file_size = wav_file.stat().st_size
            if file_size < 1000:  # Menos de 1KB = probablemente silencio
                logger.warning("⚠️ Audio muy corto, ignorando")
                wav_file.unlink(missing_ok=True)
                return None
            
            # Transcribir con Whisper
            transcripcion = await self.stt.audio_a_texto(wav_file, language='es')
            
            # Limpiar
            wav_file.unlink(missing_ok=True)
            
            logger.info(f"📝 Cliente dice: {transcripcion}")
            return transcripcion
            
        except Exception as e:
            logger.error(f"❌ Error en STT: {e}")
            return None
    
    def _guardar_resultado(self):
        """Guarda el resultado de la llamada."""
        if not self.motor:
            return
        
        resultado = self.motor.obtener_resultado()
        
        # Guardar en variable de canal
        self.agi.set_variable('VOICEBOT_RESULTADO', resultado['resultado'])
        self.agi.set_variable('VOICEBOT_MONTO', str(resultado['monto_acordado']))
        self.agi.set_variable('VOICEBOT_DURACION', str(resultado['duracion_segundos']))
        
        # Log del resultado
        logger.info("="*60)
        logger.info(f"📊 RESULTADO: {resultado['resultado']}")
        logger.info(f"   Cédula: {resultado['cedula']}")
        logger.info(f"   Monto acordado: ${resultado['monto_acordado']:,.0f}")
        logger.info(f"   Duración: {resultado['duracion_segundos']}s")
        logger.info("="*60)


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Punto de entrada principal."""
    voicebot = VoicebotAGI()
    await voicebot.iniciar()

if __name__ == "__main__":
    asyncio.run(main())
