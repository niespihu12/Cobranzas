"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VOICEBOT COBRANZAS - MARCADOR AUTOMÁTICO                                     ║
║  Lee el CTI y ejecuta llamadas de forma automática                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Uso:
    python3 marcador.py --cti CTI_ENRIQUECIDO.xlsx --max-calls 100

"""

import os
import sys
import asyncio
import argparse
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import socket
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

@dataclass
class ConfigMarcador:
    """Configuración del marcador."""
    
    # Asterisk AMI
    AMI_HOST: str = os.getenv('ASTERISK_HOST', 'localhost')
    AMI_PORT: int = int(os.getenv('ASTERISK_AMI_PORT', '5038'))
    AMI_USER: str = os.getenv('ASTERISK_AMI_USER', 'voicebot')
    AMI_SECRET: str = os.getenv('ASTERISK_AMI_SECRET', 'voicebot123')
    
    # Troncal
    TRUNK: str = os.getenv('ASTERISK_TRUNK', 'PJSIP/trunk-salida')
    CONTEXT: str = 'voicebot-cobranzas'
    EXTENSION: str = 's'
    PRIORITY: int = 1
    
    # Límites
    MAX_CONCURRENT_CALLS: int = 5  # Llamadas simultáneas
    CALL_TIMEOUT: int = 30  # Segundos para que contesten
    RETRY_DELAY: int = 300  # 5 minutos entre reintentos
    MAX_RETRIES: int = 3  # Máximo de intentos por cliente
    
    # Horarios (hora local)
    HORA_INICIO: int = 8  # 8 AM
    HORA_FIN: int = 20  # 8 PM
    
    # Archivos
    RESULTADOS_PATH: str = './resultados_llamadas.csv'


config = ConfigMarcador()

# ============================================================================
# CLIENTE AMI (Asterisk Manager Interface)
# ============================================================================

class AsteriskAMI:
    """
    Cliente para Asterisk Manager Interface.
    """
    
    def __init__(
        self,
        host: str = config.AMI_HOST,
        port: int = config.AMI_PORT,
        username: str = config.AMI_USER,
        secret: str = config.AMI_SECRET
    ):
        self.host = host
        self.port = port
        self.username = username
        self.secret = secret
        
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.action_id = 0
    
    def connect(self) -> bool:
        """Conecta al AMI."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Leer banner
            response = self._read_response()
            logger.debug(f"AMI Banner: {response}")
            
            # Login
            login_response = self._send_action({
                'Action': 'Login',
                'Username': self.username,
                'Secret': self.secret
            })
            
            if 'Success' in login_response:
                self.connected = True
                logger.info(f"✅ Conectado a AMI: {self.host}:{self.port}")
                return True
            else:
                logger.error(f"❌ Login fallido: {login_response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error conectando a AMI: {e}")
            return False
    
    def disconnect(self):
        """Desconecta del AMI."""
        if self.socket:
            try:
                self._send_action({'Action': 'Logoff'})
            except:
                pass
            self.socket.close()
            self.connected = False
            logger.info("🔌 Desconectado de AMI")
    
    def _send_action(self, action: Dict[str, Any]) -> str:
        """Envía una acción al AMI."""
        if not self.socket:
            raise ConnectionError("No conectado a AMI")
        
        # Agregar ActionID
        self.action_id += 1
        action['ActionID'] = str(self.action_id)
        
        # Formatear mensaje
        message = '\r\n'.join(f"{k}: {v}" for k, v in action.items())
        message += '\r\n\r\n'
        
        # Enviar
        self.socket.send(message.encode())
        
        # Leer respuesta
        return self._read_response()
    
    def _read_response(self) -> str:
        """Lee respuesta del AMI."""
        response = b''
        while True:
            chunk = self.socket.recv(4096)
            response += chunk
            if b'\r\n\r\n' in response:
                break
        return response.decode('utf-8', errors='ignore')
    
    def originate(
        self,
        channel: str,
        context: str,
        exten: str,
        priority: int,
        caller_id: str,
        timeout: int,
        variables: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Origina una llamada.
        
        Args:
            channel: Canal de destino (ej: PJSIP/trunk/3001234567)
            context: Contexto del dialplan
            exten: Extensión
            priority: Prioridad
            caller_id: Caller ID
            timeout: Timeout en milisegundos
            variables: Variables de canal
            
        Returns:
            Respuesta del AMI
        """
        action = {
            'Action': 'Originate',
            'Channel': channel,
            'Context': context,
            'Exten': exten,
            'Priority': priority,
            'CallerID': caller_id,
            'Timeout': timeout,
            'Async': 'true'  # No bloquear
        }
        
        # Agregar variables
        if variables:
            var_str = ','.join(f"{k}={v}" for k, v in variables.items())
            action['Variable'] = var_str
        
        response = self._send_action(action)
        
        return {
            'success': 'Success' in response,
            'response': response,
            'action_id': self.action_id
        }
    
    def get_channels(self) -> List[str]:
        """Obtiene lista de canales activos."""
        response = self._send_action({'Action': 'CoreShowChannels'})
        
        channels = []
        for line in response.split('\r\n'):
            if 'Channel:' in line:
                channel = line.split(': ')[1]
                channels.append(channel)
        
        return channels


# ============================================================================
# MARCADOR AUTOMÁTICO
# ============================================================================

class Marcador:
    """
    Marcador automático que procesa el CTI y hace llamadas.
    """
    
    def __init__(self, config: ConfigMarcador = config):
        self.config = config
        self.ami = AsteriskAMI()
        
        # Estado
        self.llamadas_activas: Dict[str, Dict] = {}
        self.cola_llamadas: List[Dict] = []
        self.resultados: List[Dict] = []
        
        # Contadores
        self.total_llamadas = 0
        self.llamadas_exitosas = 0
        self.llamadas_fallidas = 0
        self.sin_contestar = 0
    
    def cargar_cti(self, cti_path: str, max_calls: int = None) -> int:
        """
        Carga el CTI y prepara la cola de llamadas.
        
        Args:
            cti_path: Ruta al CTI enriquecido
            max_calls: Número máximo de llamadas (opcional)
            
        Returns:
            Número de clientes en cola
        """
        logger.info(f"📂 Cargando CTI: {cti_path}")
        
        df = pd.read_excel(cti_path)
        
        # Ordenar por probabilidad de pago (mayor primero)
        prob_col = 'probabilidad_pago_ML' if 'probabilidad_pago_ML' in df.columns else 'probabilidad_pago_SIMULADA'
        if prob_col in df.columns:
            df = df.sort_values(prob_col, ascending=False)
        
        # Limitar si es necesario
        if max_calls:
            df = df.head(max_calls)
        
        # Crear cola de llamadas
        for _, row in df.iterrows():
            cliente = {
                'cedula': str(row.get('cedula', '')),
                'nombre': str(row.get('name', '')),
                'celular': self._normalizar_telefono(str(row.get('celular', ''))),
                'producto': str(row.get('producto', '')),
                'tipo_producto': str(row.get('Tipo Producto', '')),
                'dias_mora': int(row.get('dias mora', 0)),
                'saldo_mora': float(row.get('Saldo en mora', 0)),
                'pago_minimo': float(row.get('Pago Minimo', 0)),
                'gac': float(row.get('GAC_proyectado', 0)),
                'total_a_pagar': float(row.get('total_a_pagar', 0)),
                'tiene_campana': row.get('campaign', False),
                'mecanismo': str(row.get('mecanismo_detectado', '')),
                'probabilidad': float(row.get(prob_col, 0)),
                'segmento': str(row.get('segmento_ML', row.get('segmento_SIMULADO', 'D'))),
                
                # Scripts
                'script_oferta': str(row.get('oferta_principal', '')),
                'script_abono': str(row.get('negociacion_abono', '')),
                
                # Control
                'intentos': 0,
                'ultimo_intento': None
            }
            
            if cliente['celular']:
                self.cola_llamadas.append(cliente)
        
        logger.info(f"✅ {len(self.cola_llamadas)} clientes en cola")
        return len(self.cola_llamadas)
    
    def _normalizar_telefono(self, telefono: str) -> str:
        """Normaliza número de teléfono."""
        # Quitar caracteres no numéricos
        telefono = ''.join(filter(str.isdigit, telefono))
        
        # Agregar código de país si es necesario (Colombia)
        if len(telefono) == 10 and telefono.startswith('3'):
            telefono = '57' + telefono
        
        return telefono
    
    def _en_horario(self) -> bool:
        """Verifica si estamos en horario de llamadas."""
        hora_actual = datetime.now().hour
        return self.config.HORA_INICIO <= hora_actual < self.config.HORA_FIN
    
    def _puede_llamar(self, cliente: Dict) -> bool:
        """Verifica si se puede llamar a un cliente."""
        # Máximo de reintentos
        if cliente['intentos'] >= self.config.MAX_RETRIES:
            return False
        
        # Delay entre reintentos
        if cliente['ultimo_intento']:
            desde_ultimo = datetime.now() - cliente['ultimo_intento']
            if desde_ultimo.total_seconds() < self.config.RETRY_DELAY:
                return False
        
        return True
    
    async def iniciar(self, cti_path: str, max_calls: int = None):
        """
        Inicia el proceso de marcación.
        
        Args:
            cti_path: Ruta al CTI
            max_calls: Número máximo de llamadas
        """
        logger.info("="*60)
        logger.info("🚀 MARCADOR AUTOMÁTICO INICIADO")
        logger.info("="*60)
        
        # Cargar CTI
        total = self.cargar_cti(cti_path, max_calls)
        
        if total == 0:
            logger.warning("⚠️ No hay clientes para llamar")
            return
        
        # Conectar a AMI
        if not self.ami.connect():
            logger.error("❌ No se pudo conectar a Asterisk")
            return
        
        try:
            await self._loop_marcacion()
        finally:
            self.ami.disconnect()
            self._guardar_resultados()
            self._mostrar_resumen()
    
    async def _loop_marcacion(self):
        """Loop principal de marcación."""
        while self.cola_llamadas or self.llamadas_activas:
            # Verificar horario
            if not self._en_horario():
                logger.info("⏰ Fuera de horario, esperando...")
                await asyncio.sleep(60)
                continue
            
            # Lanzar llamadas si hay espacio
            while (
                len(self.llamadas_activas) < self.config.MAX_CONCURRENT_CALLS
                and self.cola_llamadas
            ):
                # Buscar siguiente cliente válido
                cliente = self._obtener_siguiente_cliente()
                if not cliente:
                    break
                
                # Hacer llamada
                await self._hacer_llamada(cliente)
            
            # Actualizar estado de llamadas
            await self._actualizar_estado_llamadas()
            
            # Pequeña pausa
            await asyncio.sleep(1)
    
    def _obtener_siguiente_cliente(self) -> Optional[Dict]:
        """Obtiene el siguiente cliente válido para llamar."""
        for i, cliente in enumerate(self.cola_llamadas):
            if self._puede_llamar(cliente):
                return self.cola_llamadas.pop(i)
        return None
    
    async def _hacer_llamada(self, cliente: Dict):
        """Hace una llamada a un cliente."""
        telefono = cliente['celular']
        
        logger.info(f"📞 Llamando a {cliente['nombre']} ({telefono})")
        
        # Canal de salida
        channel = f"{self.config.TRUNK}/{telefono}"
        
        # Variables de canal
        variables = {
            'CLIENTE_CEDULA': cliente['cedula'],
            'CLIENTE_NOMBRE': cliente['nombre'],
            'CLIENTE_CELULAR': telefono,
            'CLIENTE_PRODUCTO': cliente['producto'],
            'CLIENTE_TIPO_PRODUCTO': cliente['tipo_producto'],
            'CLIENTE_DIAS_MORA': str(cliente['dias_mora']),
            'CLIENTE_SALDO_MORA': str(cliente['saldo_mora']),
            'CLIENTE_PAGO_MINIMO': str(cliente['pago_minimo']),
            'CLIENTE_GAC': str(cliente['gac']),
            'CLIENTE_TOTAL_PAGAR': str(cliente['total_a_pagar']),
            'CLIENTE_TIENE_CAMPANA': 'true' if cliente['tiene_campana'] else 'false',
            'CLIENTE_MECANISMO': cliente['mecanismo'],
            'CLIENTE_PROBABILIDAD': str(cliente['probabilidad']),
            'CLIENTE_SEGMENTO': cliente['segmento'],
            'CLIENTE_SCRIPT_OFERTA': cliente['script_oferta'][:200],  # Limitar
            'CLIENTE_SCRIPT_ABONO': cliente['script_abono'][:200]
        }
        
        # Originar llamada
        result = self.ami.originate(
            channel=channel,
            context=self.config.CONTEXT,
            exten=self.config.EXTENSION,
            priority=self.config.PRIORITY,
            caller_id=f"Banco de Bogotá <{telefono}>",
            timeout=self.config.CALL_TIMEOUT * 1000,
            variables=variables
        )
        
        if result['success']:
            # Registrar llamada activa
            call_id = f"call_{datetime.now().strftime('%Y%m%d%H%M%S')}_{cliente['cedula']}"
            self.llamadas_activas[call_id] = {
                'cliente': cliente,
                'inicio': datetime.now(),
                'action_id': result['action_id'],
                'estado': 'LLAMANDO'
            }
            cliente['intentos'] += 1
            cliente['ultimo_intento'] = datetime.now()
            self.total_llamadas += 1
        else:
            logger.error(f"❌ Error originando llamada: {result['response']}")
            # Volver a poner en cola
            self.cola_llamadas.append(cliente)
    
    async def _actualizar_estado_llamadas(self):
        """Actualiza el estado de las llamadas activas."""
        # Obtener canales activos
        canales_activos = self.ami.get_channels()
        
        terminadas = []
        
        for call_id, llamada in self.llamadas_activas.items():
            # Verificar timeout
            duracion = (datetime.now() - llamada['inicio']).total_seconds()
            
            # Si lleva más de 5 minutos, dar por terminada
            if duracion > 300:
                terminadas.append(call_id)
                self._registrar_resultado(llamada, 'TIMEOUT')
                continue
            
            # TODO: Verificar estado real en AMI events
    
        # Limpiar terminadas
        for call_id in terminadas:
            del self.llamadas_activas[call_id]
    
    def _registrar_resultado(self, llamada: Dict, resultado: str, monto: float = 0):
        """Registra el resultado de una llamada."""
        cliente = llamada['cliente']
        
        registro = {
            'fecha': datetime.now().isoformat(),
            'cedula': cliente['cedula'],
            'nombre': cliente['nombre'],
            'celular': cliente['celular'],
            'producto': cliente['producto'],
            'dias_mora': cliente['dias_mora'],
            'saldo_mora': cliente['saldo_mora'],
            'probabilidad': cliente['probabilidad'],
            'segmento': cliente['segmento'],
            'resultado': resultado,
            'monto_acordado': monto,
            'duracion_seg': (datetime.now() - llamada['inicio']).total_seconds()
        }
        
        self.resultados.append(registro)
        
        # Contadores
        if resultado == 'EXITOSO':
            self.llamadas_exitosas += 1
        elif resultado == 'SIN_CONTESTAR':
            self.sin_contestar += 1
        else:
            self.llamadas_fallidas += 1
        
        logger.info(f"📊 Resultado: {cliente['nombre']} → {resultado}")
    
    def _guardar_resultados(self):
        """Guarda los resultados en CSV."""
        if not self.resultados:
            return
        
        df = pd.DataFrame(self.resultados)
        
        # Agregar a archivo existente o crear nuevo
        output_path = self.config.RESULTADOS_PATH
        
        if os.path.exists(output_path):
            df_existente = pd.read_csv(output_path)
            df = pd.concat([df_existente, df], ignore_index=True)
        
        df.to_csv(output_path, index=False)
        logger.info(f"💾 Resultados guardados: {output_path}")
    
    def _mostrar_resumen(self):
        """Muestra resumen de la sesión."""
        logger.info("")
        logger.info("="*60)
        logger.info("📊 RESUMEN DE SESIÓN")
        logger.info("="*60)
        logger.info(f"   Total llamadas: {self.total_llamadas}")
        logger.info(f"   ✅ Exitosas: {self.llamadas_exitosas}")
        logger.info(f"   ❌ Fallidas: {self.llamadas_fallidas}")
        logger.info(f"   📵 Sin contestar: {self.sin_contestar}")
        
        if self.total_llamadas > 0:
            tasa_exito = self.llamadas_exitosas / self.total_llamadas * 100
            logger.info(f"   📈 Tasa de éxito: {tasa_exito:.1f}%")
        
        logger.info("="*60)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Marcador automático Voicebot Cobranzas'
    )
    
    parser.add_argument(
        '--cti',
        type=str,
        required=True,
        help='Ruta al archivo CTI enriquecido (Excel)'
    )
    
    parser.add_argument(
        '--max-calls',
        type=int,
        default=None,
        help='Número máximo de llamadas'
    )
    
    parser.add_argument(
        '--concurrent',
        type=int,
        default=5,
        help='Llamadas concurrentes (default: 5)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo simular, no hacer llamadas reales'
    )
    
    args = parser.parse_args()
    
    # Actualizar config
    config.MAX_CONCURRENT_CALLS = args.concurrent
    
    # Crear marcador
    marcador = Marcador(config)
    
    if args.dry_run:
        logger.info("🧪 MODO DRY-RUN (sin llamadas reales)")
        marcador.cargar_cti(args.cti, args.max_calls)
        return
    
    # Iniciar
    asyncio.run(marcador.iniciar(args.cti, args.max_calls))


if __name__ == "__main__":
    main()
