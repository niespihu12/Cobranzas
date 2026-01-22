"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VOICEBOT COBRANZAS - BANCO DE BOGOTÁ                                         ║
║  Motor Principal de Conversación                                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Integración: Asterisk + Whisper (STT) + Eleven Labs (TTS)                    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

@dataclass
class Config:
    """Configuración del Voicebot."""
    
    # APIs
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    ELEVENLABS_API_KEY: str = os.getenv('ELEVENLABS_API_KEY', '')
    
    # Eleven Labs
    ELEVENLABS_VOICE_ID: str = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')  # Bella (español)
    ELEVENLABS_MODEL: str = 'eleven_multilingual_v2'
    
    # Asterisk
    ASTERISK_HOST: str = os.getenv('ASTERISK_HOST', 'localhost')
    ASTERISK_AMI_PORT: int = int(os.getenv('ASTERISK_AMI_PORT', '5038'))
    ASTERISK_AMI_USER: str = os.getenv('ASTERISK_AMI_USER', 'voicebot')
    ASTERISK_AMI_SECRET: str = os.getenv('ASTERISK_AMI_SECRET', 'voicebot123')
    
    # Rutas
    AUDIO_PATH: str = '/var/lib/asterisk/sounds/voicebot/'
    CTI_PATH: str = './02_datos/salida/CTI_ENRIQUECIDO_COMPLETO.xlsx'
    
    # Tiempos
    SILENCE_TIMEOUT: int = 3  # Segundos de silencio antes de continuar
    MAX_CALL_DURATION: int = 300  # 5 minutos máximo
    WAIT_AFTER_SPEAK: float = 0.5  # Pausa después de hablar

config = Config()

# ============================================================================
# ESTADOS DE LA CONVERSACIÓN
# ============================================================================

class EstadoConversacion(Enum):
    """Estados posibles de la conversación."""
    INICIO = "inicio"
    SALUDO = "saludo"
    IDENTIFICACION = "identificacion"
    VALIDACION_IDENTIDAD = "validacion_identidad"
    OFERTA_PRINCIPAL = "oferta_principal"
    ESPERA_RESPUESTA_OFERTA = "espera_respuesta_oferta"
    NEGOCIACION_ABONO = "negociacion_abono"
    ESPERA_RESPUESTA_ABONO = "espera_respuesta_abono"
    CIERRE_EXITOSO = "cierre_exitoso"
    CIERRE_SIN_ACUERDO = "cierre_sin_acuerdo"
    FIN = "fin"
    ERROR = "error"

# ============================================================================
# DATOS DEL CLIENTE
# ============================================================================

@dataclass
class DatosCliente:
    """Información del cliente para la llamada."""
    cedula: str
    nombre: str
    celular: str
    producto: str
    tipo_producto: str
    dias_mora: int
    saldo_mora: float
    pago_minimo: float
    gac: float
    total_a_pagar: float
    tiene_campana: bool
    mecanismo: Optional[str] = None
    descuento_intereses: int = 0
    descuento_capital: int = 0
    tasa_nueva: Optional[float] = None
    requiere_pago: bool = False
    probabilidad_pago: float = 0.0
    segmento: str = 'D'
    
    # Scripts
    script_apertura: str = ''
    script_identificacion: str = ''
    script_oferta: str = ''
    script_abono: str = ''
    script_cierre_exitoso: str = ''
    script_cierre_sin_acuerdo: str = ''

# ============================================================================
# SESIÓN DE LLAMADA
# ============================================================================

@dataclass
class SesionLlamada:
    """Estado de una llamada en curso."""
    call_id: str
    cliente: DatosCliente
    estado: EstadoConversacion = EstadoConversacion.INICIO
    inicio: datetime = field(default_factory=datetime.now)
    
    # Historial
    historial: list = field(default_factory=list)
    
    # Resultados
    identidad_confirmada: bool = False
    acepto_oferta: bool = False
    acepto_abono: bool = False
    monto_acordado: float = 0.0
    fecha_pago_acordada: Optional[str] = None
    
    # Métricas
    duracion_segundos: int = 0
    turnos_conversacion: int = 0
    
    def agregar_turno(self, rol: str, texto: str):
        """Agrega un turno al historial."""
        self.historial.append({
            'timestamp': datetime.now().isoformat(),
            'rol': rol,  # 'bot' o 'cliente'
            'texto': texto
        })
        self.turnos_conversacion += 1

# ============================================================================
# MOTOR DE CONVERSACIÓN
# ============================================================================

class MotorConversacion:
    """
    Motor principal que maneja el flujo de la conversación.
    """
    
    def __init__(self, cliente: DatosCliente):
        self.sesion = SesionLlamada(
            call_id=f"call_{datetime.now().strftime('%Y%m%d%H%M%S')}_{cliente.cedula}",
            cliente=cliente
        )
        logger.info(f"Nueva sesión: {self.sesion.call_id}")
    
    def obtener_siguiente_mensaje(self, respuesta_cliente: Optional[str] = None) -> tuple[str, EstadoConversacion]:
        """
        Determina el siguiente mensaje del bot basado en el estado actual.
        
        Args:
            respuesta_cliente: Transcripción de lo que dijo el cliente
            
        Returns:
            (mensaje_bot, nuevo_estado)
        """
        estado_actual = self.sesion.estado
        cliente = self.sesion.cliente
        
        # Registrar respuesta del cliente si existe
        if respuesta_cliente:
            self.sesion.agregar_turno('cliente', respuesta_cliente)
            logger.info(f"Cliente dice: {respuesta_cliente[:50]}...")
        
        # Máquina de estados
        if estado_actual == EstadoConversacion.INICIO:
            return self._estado_saludo()
        
        elif estado_actual == EstadoConversacion.SALUDO:
            return self._estado_identificacion()
        
        elif estado_actual == EstadoConversacion.IDENTIFICACION:
            return self._estado_validar_identidad(respuesta_cliente)
        
        elif estado_actual == EstadoConversacion.VALIDACION_IDENTIDAD:
            return self._estado_oferta_principal()
        
        elif estado_actual == EstadoConversacion.OFERTA_PRINCIPAL:
            return self._estado_espera_respuesta_oferta()
        
        elif estado_actual == EstadoConversacion.ESPERA_RESPUESTA_OFERTA:
            return self._procesar_respuesta_oferta(respuesta_cliente)
        
        elif estado_actual == EstadoConversacion.NEGOCIACION_ABONO:
            return self._estado_espera_respuesta_abono()
        
        elif estado_actual == EstadoConversacion.ESPERA_RESPUESTA_ABONO:
            return self._procesar_respuesta_abono(respuesta_cliente)
        
        elif estado_actual == EstadoConversacion.CIERRE_EXITOSO:
            return self._estado_fin_exitoso()
        
        elif estado_actual == EstadoConversacion.CIERRE_SIN_ACUERDO:
            return self._estado_fin_sin_acuerdo()
        
        else:
            return self._estado_error()
    
    # ========================================================================
    # ESTADOS
    # ========================================================================
    
    def _estado_saludo(self) -> tuple[str, EstadoConversacion]:
        """Estado inicial: Saludo."""
        mensaje = f"""
        Buenos días, le habla el asistente virtual del Banco de Bogotá.
        ¿Me comunico con {self.sesion.cliente.nombre}?
        """
        mensaje = self._limpiar_texto(mensaje)
        self.sesion.agregar_turno('bot', mensaje)
        self.sesion.estado = EstadoConversacion.SALUDO
        return mensaje, EstadoConversacion.SALUDO
    
    def _estado_identificacion(self) -> tuple[str, EstadoConversacion]:
        """Solicitar identificación."""
        mensaje = """
        Para continuar, por favor confirme los últimos cuatro dígitos de su número de cédula.
        """
        mensaje = self._limpiar_texto(mensaje)
        self.sesion.agregar_turno('bot', mensaje)
        self.sesion.estado = EstadoConversacion.IDENTIFICACION
        return mensaje, EstadoConversacion.IDENTIFICACION
    
    def _estado_validar_identidad(self, respuesta: str) -> tuple[str, EstadoConversacion]:
        """Validar la identidad del cliente."""
        cedula = self.sesion.cliente.cedula
        ultimos_4 = cedula[-4:] if len(cedula) >= 4 else cedula
        
        # Extraer números de la respuesta
        numeros = ''.join(filter(str.isdigit, respuesta or ''))
        
        if ultimos_4 in numeros or self._es_confirmacion(respuesta):
            self.sesion.identidad_confirmada = True
            mensaje = """
            Perfecto, gracias por confirmar su identidad.
            """
            mensaje = self._limpiar_texto(mensaje)
            self.sesion.agregar_turno('bot', mensaje)
            self.sesion.estado = EstadoConversacion.VALIDACION_IDENTIDAD
            return mensaje, EstadoConversacion.VALIDACION_IDENTIDAD
        else:
            # No se pudo validar
            mensaje = """
            Lo siento, no pudimos confirmar su identidad. 
            Por favor comuníquese con nuestra línea de atención. Hasta luego.
            """
            mensaje = self._limpiar_texto(mensaje)
            self.sesion.agregar_turno('bot', mensaje)
            self.sesion.estado = EstadoConversacion.FIN
            return mensaje, EstadoConversacion.FIN
    
    def _estado_oferta_principal(self) -> tuple[str, EstadoConversacion]:
        """Presentar la oferta principal."""
        cliente = self.sesion.cliente
        
        if cliente.tiene_campana and cliente.script_oferta:
            mensaje = cliente.script_oferta
        else:
            # Oferta estándar
            mensaje = f"""
            Le informamos que su producto {cliente.tipo_producto} presenta un saldo en mora 
            de {self._formatear_moneda(cliente.saldo_mora)} con {cliente.dias_mora} días de atraso.
            
            El valor total a pagar hoy para normalizar su obligación es de 
            {self._formatear_moneda(cliente.total_a_pagar)}, que incluye su cuota y los gastos de cobranza.
            
            ¿Puede realizar este pago el día de hoy?
            """
        
        mensaje = self._limpiar_texto(mensaje)
        self.sesion.agregar_turno('bot', mensaje)
        self.sesion.estado = EstadoConversacion.OFERTA_PRINCIPAL
        return mensaje, EstadoConversacion.OFERTA_PRINCIPAL
    
    def _estado_espera_respuesta_oferta(self) -> tuple[str, EstadoConversacion]:
        """Esperar respuesta a la oferta."""
        self.sesion.estado = EstadoConversacion.ESPERA_RESPUESTA_OFERTA
        return "", EstadoConversacion.ESPERA_RESPUESTA_OFERTA
    
    def _procesar_respuesta_oferta(self, respuesta: str) -> tuple[str, EstadoConversacion]:
        """Procesar la respuesta a la oferta principal."""
        if self._es_confirmacion(respuesta):
            # Aceptó la oferta
            self.sesion.acepto_oferta = True
            self.sesion.monto_acordado = self.sesion.cliente.total_a_pagar
            return self._estado_cierre_exitoso()
        
        elif self._es_negacion(respuesta):
            # Rechazó, ofrecer abono
            return self._estado_negociacion_abono()
        
        else:
            # No entendió, repetir
            mensaje = """
            Disculpe, no entendí su respuesta. 
            ¿Puede realizar el pago completo el día de hoy? Por favor responda sí o no.
            """
            mensaje = self._limpiar_texto(mensaje)
            self.sesion.agregar_turno('bot', mensaje)
            return mensaje, EstadoConversacion.ESPERA_RESPUESTA_OFERTA
    
    def _estado_negociacion_abono(self) -> tuple[str, EstadoConversacion]:
        """Ofrecer alternativa de abono."""
        cliente = self.sesion.cliente
        
        # Calcular abono mínimo (10% del total o cuota mensual)
        abono_minimo = max(cliente.total_a_pagar * 0.1, 50000)
        
        if cliente.script_abono:
            mensaje = cliente.script_abono
        else:
            mensaje = f"""
            Entiendo. Como alternativa, puede realizar un abono mínimo de 
            {self._formatear_moneda(abono_minimo)} para demostrar su voluntad de pago 
            y evitar que su obligación pase a cobro jurídico.
            
            ¿Le interesa esta opción?
            """
        
        mensaje = self._limpiar_texto(mensaje)
        self.sesion.agregar_turno('bot', mensaje)
        self.sesion.estado = EstadoConversacion.NEGOCIACION_ABONO
        return mensaje, EstadoConversacion.NEGOCIACION_ABONO
    
    def _estado_espera_respuesta_abono(self) -> tuple[str, EstadoConversacion]:
        """Esperar respuesta al abono."""
        self.sesion.estado = EstadoConversacion.ESPERA_RESPUESTA_ABONO
        return "", EstadoConversacion.ESPERA_RESPUESTA_ABONO
    
    def _procesar_respuesta_abono(self, respuesta: str) -> tuple[str, EstadoConversacion]:
        """Procesar respuesta al abono."""
        if self._es_confirmacion(respuesta):
            self.sesion.acepto_abono = True
            abono_minimo = max(self.sesion.cliente.total_a_pagar * 0.1, 50000)
            self.sesion.monto_acordado = abono_minimo
            return self._estado_cierre_exitoso()
        else:
            return self._estado_cierre_sin_acuerdo()
    
    def _estado_cierre_exitoso(self) -> tuple[str, EstadoConversacion]:
        """Cierre con acuerdo de pago."""
        cliente = self.sesion.cliente
        
        mensaje = f"""
        Excelente. Queda registrado su compromiso de pago por {self._formatear_moneda(self.sesion.monto_acordado)}.
        
        Recuerde que puede realizar el pago a través de nuestra aplicación móvil, 
        en cualquier oficina del banco, o en puntos de pago autorizados.
        
        Gracias por su atención. Que tenga un excelente día.
        """
        
        mensaje = self._limpiar_texto(mensaje)
        self.sesion.agregar_turno('bot', mensaje)
        self.sesion.estado = EstadoConversacion.FIN
        
        logger.info(f"✅ Llamada exitosa: {self.sesion.call_id} - Monto: {self.sesion.monto_acordado}")
        return mensaje, EstadoConversacion.FIN
    
    def _estado_cierre_sin_acuerdo(self) -> tuple[str, EstadoConversacion]:
        """Cierre sin acuerdo."""
        mensaje = """
        Entendemos su situación. Le recordamos que es importante normalizar su obligación 
        para evitar reportes a centrales de riesgo y procesos de cobro adicionales.
        
        Si tiene alguna duda, puede comunicarse con nuestra línea de atención al cliente.
        Gracias por su tiempo. Hasta luego.
        """
        
        mensaje = self._limpiar_texto(mensaje)
        self.sesion.agregar_turno('bot', mensaje)
        self.sesion.estado = EstadoConversacion.FIN
        
        logger.info(f"❌ Llamada sin acuerdo: {self.sesion.call_id}")
        return mensaje, EstadoConversacion.FIN
    
    def _estado_error(self) -> tuple[str, EstadoConversacion]:
        """Estado de error."""
        mensaje = """
        Disculpe, hemos tenido un problema técnico. 
        Por favor comuníquese con nuestra línea de atención. Hasta luego.
        """
        mensaje = self._limpiar_texto(mensaje)
        self.sesion.estado = EstadoConversacion.FIN
        return mensaje, EstadoConversacion.FIN
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def _es_confirmacion(self, texto: str) -> bool:
        """Detecta si el texto es una confirmación."""
        if not texto:
            return False
        texto = texto.lower().strip()
        confirmaciones = [
            'sí', 'si', 'claro', 'por supuesto', 'correcto', 'exacto',
            'afirmativo', 'ok', 'okay', 'dale', 'bueno', 'está bien',
            'de acuerdo', 'acepto', 'confirmo', 'yes', 'eso es',
            'así es', 'efectivamente', 'positivo'
        ]
        return any(c in texto for c in confirmaciones)
    
    def _es_negacion(self, texto: str) -> bool:
        """Detecta si el texto es una negación."""
        if not texto:
            return False
        texto = texto.lower().strip()
        negaciones = [
            'no', 'nop', 'negativo', 'para nada', 'imposible',
            'no puedo', 'no tengo', 'no me es posible', 'difícil',
            'complicado', 'ahora no', 'en este momento no'
        ]
        return any(n in texto for n in negaciones)
    
    def _limpiar_texto(self, texto: str) -> str:
        """Limpia y formatea el texto para TTS."""
        import re
        texto = texto.strip()
        texto = re.sub(r'\s+', ' ', texto)
        texto = texto.replace('\n', ' ')
        return texto
    
    def _formatear_moneda(self, valor: float) -> str:
        """Formatea un valor como moneda colombiana para TTS."""
        valor_int = int(valor)
        if valor_int >= 1000000:
            millones = valor_int // 1000000
            resto = (valor_int % 1000000) // 1000
            if resto > 0:
                return f"{millones} millones {resto} mil pesos"
            return f"{millones} millones de pesos"
        elif valor_int >= 1000:
            miles = valor_int // 1000
            return f"{miles} mil pesos"
        else:
            return f"{valor_int} pesos"
    
    def obtener_resultado(self) -> Dict[str, Any]:
        """Retorna el resultado de la llamada."""
        return {
            'call_id': self.sesion.call_id,
            'cedula': self.sesion.cliente.cedula,
            'nombre': self.sesion.cliente.nombre,
            'inicio': self.sesion.inicio.isoformat(),
            'duracion_segundos': self.sesion.duracion_segundos,
            'turnos': self.sesion.turnos_conversacion,
            'identidad_confirmada': self.sesion.identidad_confirmada,
            'acepto_oferta': self.sesion.acepto_oferta,
            'acepto_abono': self.sesion.acepto_abono,
            'monto_acordado': self.sesion.monto_acordado,
            'resultado': 'EXITOSO' if (self.sesion.acepto_oferta or self.sesion.acepto_abono) else 'SIN_ACUERDO',
            'historial': self.sesion.historial
        }


# ============================================================================
# PRUEBA LOCAL
# ============================================================================

if __name__ == "__main__":
    # Cliente de prueba
    cliente_prueba = DatosCliente(
        cedula="1234567890",
        nombre="Juan Pérez",
        celular="3001234567",
        producto="4532",
        tipo_producto="TARJETA",
        dias_mora=45,
        saldo_mora=1500000,
        pago_minimo=450000,
        gac=48000,
        total_a_pagar=498000,
        tiene_campana=False,
        probabilidad_pago=0.35,
        segmento='C'
    )
    
    # Crear motor
    motor = MotorConversacion(cliente_prueba)
    
    # Simular conversación
    print("\n" + "="*60)
    print("🎯 SIMULACIÓN DE CONVERSACIÓN")
    print("="*60 + "\n")
    
    # Turno 1: Saludo
    mensaje, estado = motor.obtener_siguiente_mensaje()
    print(f"🤖 BOT: {mensaje}\n")
    
    # Turno 2: Cliente confirma identidad
    mensaje, estado = motor.obtener_siguiente_mensaje("Sí, soy yo")
    print(f"🤖 BOT: {mensaje}\n")
    
    # Turno 3: Bot pide validación
    mensaje, estado = motor.obtener_siguiente_mensaje("7890")
    print(f"🤖 BOT: {mensaje}\n")
    
    # Turno 4: Oferta
    mensaje, estado = motor.obtener_siguiente_mensaje()
    print(f"🤖 BOT: {mensaje}\n")
    
    # Turno 5: Cliente rechaza
    mensaje, estado = motor.obtener_siguiente_mensaje("No puedo pagar todo")
    print(f"🤖 BOT: {mensaje}\n")
    
    # Turno 6: Cliente acepta abono
    mensaje, estado = motor.obtener_siguiente_mensaje("Sí, puedo hacer un abono")
    print(f"🤖 BOT: {mensaje}\n")
    
    # Resultado
    print("\n" + "="*60)
    print("📊 RESULTADO DE LA LLAMADA")
    print("="*60)
    resultado = motor.obtener_resultado()
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))
