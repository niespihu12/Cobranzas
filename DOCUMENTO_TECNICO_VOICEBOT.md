# 📞 VOICEBOT COBRANZAS - DOCUMENTO TÉCNICO
## Banco de Bogotá | Sistema de Cobranza Automatizada con IA

---

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Proyecto:** Voicebot Cobranzas  
**Cliente:** Banco de Bogotá

---

## 📋 TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Componentes del Sistema](#3-componentes-del-sistema)
4. [Requisitos de Infraestructura](#4-requisitos-de-infraestructura)
5. [Guía de Instalación](#5-guía-de-instalación)
6. [Configuración](#6-configuración)
7. [Flujo de Conversación](#7-flujo-de-conversación)
8. [APIs Externas](#8-apis-externas)
9. [Base de Datos y Archivos](#9-base-de-datos-y-archivos)
10. [Operación Diaria](#10-operación-diaria)
11. [Monitoreo y Logs](#11-monitoreo-y-logs)
12. [Troubleshooting](#12-troubleshooting)
13. [Seguridad](#13-seguridad)
14. [Costos Operativos](#14-costos-operativos)
15. [Roadmap y Mejoras Futuras](#15-roadmap-y-mejoras-futuras)
16. [Anexos](#16-anexos)

---

## 1. RESUMEN EJECUTIVO

### 1.1 Descripción del Sistema

El **Voicebot Cobranzas** es un sistema automatizado de llamadas telefónicas para gestión de cobranza del Banco de Bogotá. Utiliza inteligencia artificial para:

- **Realizar llamadas automáticas** a clientes en mora
- **Conversar naturalmente** usando voz sintetizada de alta calidad
- **Entender respuestas** del cliente mediante reconocimiento de voz
- **Negociar acuerdos de pago** siguiendo scripts dinámicos
- **Priorizar clientes** usando modelo de Machine Learning

### 1.2 Stack Tecnológico

| Componente | Tecnología | Función |
|------------|------------|---------|
| PBX | Asterisk 18+ | Central telefónica |
| TTS | Eleven Labs | Texto a voz (español natural) |
| STT | OpenAI Whisper | Voz a texto |
| Backend | Python 3.8+ | Lógica de negocio |
| ML | XGBoost | Predicción de pago |
| Troncal | SIP (proveedor telco) | Conexión PSTN |

### 1.3 Capacidades

| Métrica | Valor |
|---------|-------|
| Llamadas simultáneas | 5-50 (configurable) |
| Llamadas por hora | ~100-500 |
| Duración promedio | 2-3 minutos |
| Disponibilidad | 24/7 (horarios configurables) |
| Idioma | Español (Colombia) |

### 1.4 Beneficios Esperados

- **Reducción de costos**: 70-80% vs call center humano
- **Escalabilidad**: Sin límite de agentes
- **Consistencia**: Mismo script, misma calidad siempre
- **Cobertura**: Llamadas en horarios extendidos
- **Datos**: Grabación y análisis de todas las conversaciones

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Diagrama General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VOICEBOT COBRANZAS                                │
│                         Arquitectura de Alto Nivel                          │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   CLIENTE   │
                              │  (Teléfono) │
                              └──────┬──────┘
                                     │
                                     │ PSTN/VoIP
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CAPA DE TELEFONÍA                                │
│  ┌─────────────────┐              ┌─────────────────┐                       │
│  │  TRONCAL SIP    │◄────────────▶│    ASTERISK     │                       │
│  │ (Proveedor)     │              │    (PBX)        │                       │
│  └─────────────────┘              └────────┬────────┘                       │
│                                            │ AGI                            │
└────────────────────────────────────────────┼────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE APLICACIÓN                                │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   VOICEBOT AGI  │───▶│     MOTOR       │───▶│    MARCADOR     │         │
│  │   (Puente)      │    │  CONVERSACIÓN   │    │   AUTOMÁTICO    │         │
│  └────────┬────────┘    └─────────────────┘    └────────┬────────┘         │
│           │                                             │                   │
│           │         ┌───────────────────────┐           │                   │
│           │         │    SCRIPTS CTI        │◀──────────┘                   │
│           │         │  (Datos Clientes)     │                               │
│           │         └───────────────────────┘                               │
│           │                                                                 │
└───────────┼─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CAPA DE IA                                       │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   ELEVEN LABS   │    │     WHISPER     │    │     XGBOOST     │         │
│  │   (TTS)         │    │     (STT)       │    │   (Predicción)  │         │
│  │                 │    │                 │    │                 │         │
│  │  Texto → Voz    │    │  Voz → Texto    │    │  Probabilidad   │         │
│  │  Español LatAm  │    │  Español        │    │  de Pago        │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de Datos

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   CTI    │───▶│ ENRIQUE- │───▶│ MARCADOR │───▶│ ASTERISK │───▶│ CLIENTE  │
│  BANCO   │    │   CER    │    │          │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │                               │
                     ▼                               ▼
              ┌──────────┐                    ┌──────────┐
              │ XGBOOST  │                    │   AGI    │
              │ Predic.  │                    │ Python   │
              └──────────┘                    └────┬─────┘
                                                   │
                                        ┌──────────┼──────────┐
                                        ▼          ▼          ▼
                                  ┌──────────┐ ┌──────────┐ ┌──────────┐
                                  │  ELEVEN  │ │ WHISPER  │ │  MOTOR   │
                                  │  LABS    │ │  STT     │ │ CONVERS. │
                                  └──────────┘ └──────────┘ └──────────┘
```

### 2.3 Componentes por Servidor

**Opción 1: Servidor Único (Desarrollo/Pruebas)**

```
┌─────────────────────────────────────────┐
│           SERVIDOR VOICEBOT             │
│                                         │
│  • Asterisk                             │
│  • Python + Scripts                     │
│  • Base de datos (SQLite/PostgreSQL)    │
│                                         │
│  RAM: 8GB | CPU: 4 cores | Disco: 50GB  │
└─────────────────────────────────────────┘
```

**Opción 2: Servidores Separados (Producción)**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ASTERISK      │    │   APLICACIÓN    │    │   BASE DATOS    │
│                 │    │                 │    │                 │
│  • PBX          │◄──▶│  • Python       │◄──▶│  • PostgreSQL   │
│  • Troncal SIP  │    │  • Marcador     │    │  • Resultados   │
│  • AGI          │    │  • APIs         │    │  • Histórico    │
│                 │    │                 │    │                 │
│  4GB | 2 cores  │    │  8GB | 4 cores  │    │  4GB | 2 cores  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 3. COMPONENTES DEL SISTEMA

### 3.1 Inventario de Archivos

```
voicebot/
│
├── motor_conversacion.py      # Lógica de conversación
│   └── Clases: MotorConversacion, DatosCliente, SesionLlamada
│   └── Estados: SALUDO → IDENTIFICACION → OFERTA → CIERRE
│   └── ~550 líneas
│
├── elevenlabs_tts.py          # Text-to-Speech
│   └── Clase: ElevenLabsTTS
│   └── Métodos: texto_a_audio(), texto_a_audio_stream()
│   └── ~280 líneas
│
├── whisper_stt.py             # Speech-to-Text
│   └── Clase: WhisperSTT
│   └── Métodos: audio_a_texto(), audio_bytes_a_texto()
│   └── ~320 líneas
│
├── voicebot_agi.py            # Puente Asterisk
│   └── Clases: AsteriskAGI, VoicebotAGI
│   └── Métodos: stream_file(), record_file(), _hablar(), _escuchar()
│   └── ~430 líneas
│
├── marcador.py                # Marcador automático
│   └── Clases: AsteriskAMI, Marcador
│   └── Métodos: cargar_cti(), originate(), _hacer_llamada()
│   └── ~530 líneas
│
├── requirements.txt           # Dependencias Python
│
├── config/
│   ├── asterisk_config.conf   # Dialplan Asterisk
│   └── .env.example           # Variables de entorno
│
└── README.md                  # Documentación rápida
```

### 3.2 motor_conversacion.py

**Propósito:** Maneja la lógica de la conversación, estados y respuestas.

**Clases principales:**

```python
class EstadoConversacion(Enum):
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

@dataclass
class DatosCliente:
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
    mecanismo: Optional[str]
    probabilidad_pago: float
    segmento: str
    # Scripts personalizados
    script_oferta: str
    script_abono: str

class MotorConversacion:
    def obtener_siguiente_mensaje(self, respuesta_cliente: str) -> tuple[str, EstadoConversacion]:
        """Retorna (mensaje_bot, nuevo_estado)"""
```

**Métodos de detección:**

```python
def _es_confirmacion(self, texto: str) -> bool:
    """Detecta: sí, claro, correcto, de acuerdo, etc."""

def _es_negacion(self, texto: str) -> bool:
    """Detecta: no, imposible, no puedo, etc."""

def _formatear_moneda(self, valor: float) -> str:
    """1500000 → 'un millón quinientos mil pesos'"""
```

### 3.3 elevenlabs_tts.py

**Propósito:** Convierte texto a voz usando Eleven Labs API.

**Configuración:**

```python
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

VOCES = {
    'bella': 'EXAVITQu4vr4xnSDxMaL',      # Mujer, clara (RECOMENDADA)
    'rachel': '21m00Tcm4TlvDq8ikWAM',      # Mujer, profesional
    'adam': 'pNInz6obpgDQGcFmaJgB',        # Hombre, confiable
    'josh': 'TxGEqnHWrfWFTfGW9XjX',        # Hombre, amigable
}

DEFAULT_MODEL = 'eleven_multilingual_v2'  # Mejor para español
```

**Uso:**

```python
from elevenlabs_tts import ElevenLabsTTS

tts = ElevenLabsTTS(api_key="...", voice_id="EXAVITQu4vr4xnSDxMaL")

# Generar audio
audio_path = await tts.texto_a_audio(
    "Buenos días, le habla el Banco de Bogotá",
    output_path="saludo.mp3"
)

# Streaming (menor latencia)
async for chunk in tts.texto_a_audio_stream(texto):
    # Procesar chunk de audio
```

**Caché:** Los audios se cachean por hash del texto para evitar regenerar.

### 3.4 whisper_stt.py

**Propósito:** Convierte voz a texto usando OpenAI Whisper.

**Configuración:**

```python
OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = 'whisper-1'
```

**Uso:**

```python
from whisper_stt import WhisperSTT

stt = WhisperSTT(api_key="...")

# Desde archivo
texto = await stt.audio_a_texto(
    "grabacion.wav",
    language='es',
    prompt="Conversación de cobranzas bancarias"
)

# Desde bytes
texto = await stt.audio_bytes_a_texto(
    audio_bytes,
    filename="audio.wav",
    language='es'
)
```

**Prompt de contexto:** Mejora precisión con vocabulario específico:

```python
prompt = """
Conversación telefónica de cobranzas bancarias en español colombiano.
Términos comunes: sí, no, cuota, pago, banco, tarjeta, crédito, mora, 
pesos, plata, mañana, hoy, acuerdo, abono.
"""
```

### 3.5 voicebot_agi.py

**Propósito:** Puente entre Asterisk y el motor de conversación.

**Protocolo AGI:**

```
Asterisk → stdin → voicebot_agi.py → stdout → Asterisk
```

**Comandos AGI usados:**

| Comando | Función |
|---------|---------|
| `ANSWER` | Contestar llamada |
| `HANGUP` | Colgar |
| `STREAM FILE` | Reproducir audio |
| `RECORD FILE` | Grabar audio del cliente |
| `SET VARIABLE` | Establecer variable de canal |
| `GET VARIABLE` | Leer variable de canal |

**Flujo principal:**

```python
async def iniciar(self):
    # 1. Cargar datos del cliente desde variables de canal
    cliente = self._cargar_datos_cliente()
    
    # 2. Crear motor de conversación
    self.motor = MotorConversacion(cliente)
    
    # 3. Contestar llamada
    self.agi.answer()
    
    # 4. Loop de conversación
    await self._ejecutar_conversacion()
    
    # 5. Guardar resultado y colgar
    self._guardar_resultado()
    self.agi.hangup()
```

### 3.6 marcador.py

**Propósito:** Lee el CTI y origina llamadas automáticamente.

**Protocolo AMI (Asterisk Manager Interface):**

```
Puerto: 5038
Protocolo: TCP texto plano
Autenticación: Usuario/Contraseña
```

**Flujo:**

```python
# 1. Conectar a AMI
ami = AsteriskAMI()
ami.connect()

# 2. Cargar CTI
marcador.cargar_cti("CTI_ENRIQUECIDO.xlsx")

# 3. Loop de marcación
while cola_llamadas:
    if llamadas_activas < MAX_CONCURRENT:
        cliente = obtener_siguiente()
        ami.originate(
            channel=f"PJSIP/trunk/{cliente['celular']}",
            context="voicebot-cobranzas",
            exten="s",
            variables={
                'CLIENTE_CEDULA': cliente['cedula'],
                'CLIENTE_NOMBRE': cliente['nombre'],
                # ...
            }
        )
```

**CLI:**

```bash
python3 marcador.py --cti CTI.xlsx --max-calls 100 --concurrent 10
```

---

## 4. REQUISITOS DE INFRAESTRUCTURA

### 4.1 Hardware Mínimo

| Recurso | Desarrollo | Producción |
|---------|------------|------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disco | 50 GB SSD | 100+ GB SSD |
| Red | 10 Mbps | 100+ Mbps |

### 4.2 Software

| Software | Versión | Función |
|----------|---------|---------|
| Ubuntu Server | 22.04 LTS | Sistema operativo |
| Asterisk | 18+ | PBX |
| Python | 3.8+ | Backend |
| FFmpeg | 4+ | Conversión de audio |
| PostgreSQL | 14+ | Base de datos (opcional) |

### 4.3 Conectividad

| Servicio | Puerto | Protocolo |
|----------|--------|-----------|
| Asterisk SIP | 5060 | UDP |
| Asterisk RTP | 10000-20000 | UDP |
| Asterisk AMI | 5038 | TCP |
| SSH | 22 | TCP |
| APIs externas | 443 | HTTPS |

### 4.4 APIs Externas

| API | Uso | Latencia |
|-----|-----|----------|
| Eleven Labs | TTS | ~500ms |
| OpenAI Whisper | STT | ~1-2s |

---

## 5. GUÍA DE INSTALACIÓN

### 5.1 Paso 1: Preparar Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias base
sudo apt install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    git \
    wget \
    curl
```

### 5.2 Paso 2: Instalar Asterisk

```bash
# Instalar Asterisk desde repositorios
sudo apt install -y asterisk

# O compilar desde fuente (recomendado para producción)
cd /usr/src
sudo wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-18-current.tar.gz
sudo tar xvf asterisk-18-current.tar.gz
cd asterisk-18*/
sudo contrib/scripts/install_prereq install
sudo ./configure
sudo make menuselect  # Seleccionar codecs y módulos
sudo make
sudo make install
sudo make samples
sudo make config

# Iniciar servicio
sudo systemctl enable asterisk
sudo systemctl start asterisk
```

### 5.3 Paso 3: Configurar Asterisk

```bash
# Crear directorios
sudo mkdir -p /var/lib/asterisk/sounds/voicebot
sudo mkdir -p /opt/voicebot
sudo chown -R asterisk:asterisk /var/lib/asterisk/sounds/voicebot
```

**Editar /etc/asterisk/extensions.conf:**

```ini
; Al final del archivo, agregar:
#include extensions_voicebot.conf
```

**Crear /etc/asterisk/extensions_voicebot.conf:**

```ini
[voicebot-cobranzas]
exten => s,1,NoOp(=== VOICEBOT COBRANZAS ===)
 same => n,NoOp(Cliente: ${CLIENTE_NOMBRE})
 same => n,Answer()
 same => n,Wait(1)
 same => n,AGI(/opt/voicebot/voicebot_agi.py)
 same => n,NoOp(Resultado: ${VOICEBOT_RESULTADO})
 same => n,Hangup()

exten => h,1,NoOp(=== HANGUP ===)
```

**Editar /etc/asterisk/manager.conf:**

```ini
[general]
enabled = yes
port = 5038
bindaddr = 127.0.0.1

[voicebot]
secret = CAMBIAR_POR_PASSWORD_SEGURO
deny = 0.0.0.0/0.0.0.0
permit = 127.0.0.1/255.255.255.0
read = system,call,log,verbose,command,agent,user,originate
write = system,call,log,verbose,command,agent,user,originate
```

**Recargar Asterisk:**

```bash
sudo asterisk -rx "dialplan reload"
sudo asterisk -rx "manager reload"
```

### 5.4 Paso 4: Instalar Voicebot

```bash
# Clonar repositorio
cd /opt
sudo git clone https://github.com/giohua0817/voicebot-cobranzas.git voicebot
cd voicebot/voicebot

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Hacer ejecutable el AGI
chmod +x voicebot_agi.py
```

### 5.5 Paso 5: Configurar Variables de Entorno

```bash
# Copiar plantilla
cp config/.env.example .env

# Editar con tus API keys
nano .env
```

**Contenido de .env:**

```bash
# Eleven Labs
export ELEVENLABS_API_KEY="tu-api-key-eleven-labs"
export ELEVENLABS_VOICE_ID="EXAVITQu4vr4xnSDxMaL"

# OpenAI
export OPENAI_API_KEY="tu-api-key-openai"

# Asterisk
export ASTERISK_HOST="localhost"
export ASTERISK_AMI_PORT="5038"
export ASTERISK_AMI_USER="voicebot"
export ASTERISK_AMI_SECRET="tu-password-ami"
export ASTERISK_TRUNK="PJSIP/trunk-salida"
```

### 5.6 Paso 6: Configurar Troncal SIP

Editar /etc/asterisk/pjsip.conf según tu proveedor SIP.

**Ejemplo genérico:**

```ini
[trunk-salida]
type = endpoint
transport = transport-udp
context = from-trunk
disallow = all
allow = ulaw,alaw
outbound_auth = trunk-auth
aors = trunk-aor

[trunk-auth]
type = auth
auth_type = userpass
username = TU_USUARIO_SIP
password = TU_PASSWORD_SIP

[trunk-aor]
type = aor
contact = sip:TU_PROVEEDOR_SIP:5060

[trunk-identify]
type = identify
endpoint = trunk-salida
match = IP_DEL_PROVEEDOR
```

### 5.7 Paso 7: Verificar Instalación

```bash
# Verificar Asterisk
sudo asterisk -rx "core show version"
sudo asterisk -rx "dialplan show voicebot-cobranzas"
sudo asterisk -rx "manager show users"
sudo asterisk -rx "pjsip show endpoints"

# Verificar Python
cd /opt/voicebot/voicebot
source venv/bin/activate
python3 -c "import aiohttp; print('OK')"

# Test del motor
python3 motor_conversacion.py
```

---

## 6. CONFIGURACIÓN

### 6.1 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `ELEVENLABS_API_KEY` | API key de Eleven Labs | `sk-...` |
| `ELEVENLABS_VOICE_ID` | ID de la voz a usar | `EXAVITQu4vr4xnSDxMaL` |
| `OPENAI_API_KEY` | API key de OpenAI | `sk-...` |
| `ASTERISK_HOST` | IP del servidor Asterisk | `localhost` |
| `ASTERISK_AMI_PORT` | Puerto AMI | `5038` |
| `ASTERISK_AMI_USER` | Usuario AMI | `voicebot` |
| `ASTERISK_AMI_SECRET` | Password AMI | `...` |
| `ASTERISK_TRUNK` | Nombre del trunk SIP | `PJSIP/trunk-salida` |

### 6.2 Parámetros del Marcador

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `MAX_CONCURRENT_CALLS` | Llamadas simultáneas | 5 |
| `CALL_TIMEOUT` | Segundos para contestar | 30 |
| `MAX_RETRIES` | Reintentos por cliente | 3 |
| `RETRY_DELAY` | Segundos entre reintentos | 300 |
| `HORA_INICIO` | Hora inicio (24h) | 8 |
| `HORA_FIN` | Hora fin (24h) | 20 |

### 6.3 Parámetros del Voicebot

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `timeout_respuesta` | ms para responder | 7000 |
| `silencio_fin` | Segundos silencio = fin | 2 |
| `max_duracion` | Segundos máximo llamada | 300 |

### 6.4 Voces Disponibles (Eleven Labs)

| ID | Nombre | Género | Estilo |
|----|--------|--------|--------|
| `EXAVITQu4vr4xnSDxMaL` | Bella | Mujer | Clara, natural |
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Mujer | Profesional |
| `pNInz6obpgDQGcFmaJgB` | Adam | Hombre | Confiable |
| `TxGEqnHWrfWFTfGW9XjX` | Josh | Hombre | Amigable |
| `VR6AewLTigWG4xSOukaG` | Arnold | Hombre | Autoritario |

**Recomendación:** Usar **Bella** para cobranzas (clara, amigable pero profesional).

---

## 7. FLUJO DE CONVERSACIÓN

### 7.1 Diagrama de Estados

```
                              ┌───────────┐
                              │  INICIO   │
                              └─────┬─────┘
                                    │
                                    ▼
                              ┌───────────┐
                              │  SALUDO   │
                              │           │
                              │ "Buenos   │
                              │  días..." │
                              └─────┬─────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   IDENTIFICACIÓN    │
                         │                     │
                         │ "Confirme últimos   │
                         │  4 dígitos cédula"  │
                         └──────────┬──────────┘
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                     CORRECTO              INCORRECTO
                          │                   │
                          ▼                   ▼
                   ┌────────────┐       ┌───────────┐
                   │  VALIDADO  │       │    FIN    │
                   └──────┬─────┘       │ (colgar)  │
                          │             └───────────┘
                          ▼
                   ┌─────────────────┐
                   │ OFERTA PRINCIPAL│
                   │                 │
                   │ "Su saldo es    │
                   │  $X con Y días" │
                   └────────┬────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                ACEPTA            RECHAZA
                   │                 │
                   ▼                 ▼
            ┌────────────┐    ┌────────────────┐
            │   CIERRE   │    │ NEGOCIACIÓN    │
            │  EXITOSO   │    │    ABONO       │
            └────────────┘    └───────┬────────┘
                                      │
                             ┌────────┴────────┐
                             │                 │
                          ACEPTA            RECHAZA
                             │                 │
                             ▼                 ▼
                      ┌────────────┐    ┌────────────┐
                      │   CIERRE   │    │   CIERRE   │
                      │  EXITOSO   │    │ SIN ACUERDO│
                      └────────────┘    └────────────┘
```

### 7.2 Scripts de Conversación

**SALUDO:**
```
Buenos días, le habla el asistente virtual del Banco de Bogotá.
¿Me comunico con [NOMBRE_CLIENTE]?
```

**IDENTIFICACIÓN:**
```
Para continuar, por favor confirme los últimos cuatro dígitos 
de su número de cédula.
```

**VALIDACIÓN OK:**
```
Perfecto, gracias por confirmar su identidad.
```

**VALIDACIÓN FALLIDA:**
```
Lo siento, no pudimos confirmar su identidad.
Por favor comuníquese con nuestra línea de atención. Hasta luego.
```

**OFERTA PRINCIPAL (sin campaña):**
```
Le informamos que su producto [TIPO_PRODUCTO] presenta un saldo 
en mora de [SALDO_MORA] con [DIAS_MORA] días de atraso.

El valor total a pagar hoy para normalizar su obligación es de 
[TOTAL_A_PAGAR], que incluye su cuota y los gastos de cobranza.

¿Puede realizar este pago el día de hoy?
```

**OFERTA PRINCIPAL (con campaña):**
```
[SCRIPT PERSONALIZADO SEGÚN CAMPAÑA DEL CTI]
```

**NEGOCIACIÓN ABONO:**
```
Entiendo. Como alternativa, puede realizar un abono mínimo de 
[ABONO_MINIMO] para demostrar su voluntad de pago y evitar que 
su obligación pase a cobro jurídico.

¿Le interesa esta opción?
```

**CIERRE EXITOSO:**
```
Excelente. Queda registrado su compromiso de pago por [MONTO_ACORDADO].

Recuerde que puede realizar el pago a través de nuestra aplicación móvil, 
en cualquier oficina del banco, o en puntos de pago autorizados.

Gracias por su atención. Que tenga un excelente día.
```

**CIERRE SIN ACUERDO:**
```
Entendemos su situación. Le recordamos que es importante normalizar 
su obligación para evitar reportes a centrales de riesgo y procesos 
de cobro adicionales.

Si tiene alguna duda, puede comunicarse con nuestra línea de atención.
Gracias por su tiempo. Hasta luego.
```

### 7.3 Detección de Intenciones

**Confirmaciones detectadas:**

```python
confirmaciones = [
    'sí', 'si', 'claro', 'por supuesto', 'correcto', 'exacto',
    'afirmativo', 'ok', 'okay', 'dale', 'bueno', 'está bien',
    'de acuerdo', 'acepto', 'confirmo', 'yes', 'eso es',
    'así es', 'efectivamente', 'positivo'
]
```

**Negaciones detectadas:**

```python
negaciones = [
    'no', 'nop', 'negativo', 'para nada', 'imposible',
    'no puedo', 'no tengo', 'no me es posible', 'difícil',
    'complicado', 'ahora no', 'en este momento no'
]
```

---

## 8. APIS EXTERNAS

### 8.1 Eleven Labs

**Endpoint:** `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`

**Request:**
```json
{
  "text": "Buenos días, le habla el Banco de Bogotá",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.8,
    "style": 0.0,
    "use_speaker_boost": true
  }
}
```

**Response:** Audio MP3 en bytes

**Límites:**
- Free: 10,000 caracteres/mes
- Starter ($5/mes): 30,000 caracteres/mes
- Creator ($22/mes): 100,000 caracteres/mes
- Pro ($99/mes): 500,000 caracteres/mes

**Cálculo de uso:**
- Mensaje promedio: ~200 caracteres
- Llamada promedio: ~1,000 caracteres
- 1,000 llamadas/día: ~1M caracteres/mes → Plan Pro

### 8.2 OpenAI Whisper

**Endpoint:** `https://api.openai.com/v1/audio/transcriptions`

**Request:** Multipart form-data
```
file: audio.wav
model: whisper-1
language: es
prompt: "Conversación de cobranzas bancarias"
```

**Response:**
```json
{
  "text": "Sí, puedo hacer el pago mañana"
}
```

**Precio:** $0.006 / minuto de audio

**Cálculo de uso:**
- Escucha promedio: ~10 segundos
- Llamada promedio: ~5 escuchas = 50 segundos
- 1,000 llamadas/día: ~833 minutos/día = $5/día

### 8.3 Resumen de Costos APIs

| Servicio | Uso Mensual | Costo |
|----------|-------------|-------|
| Eleven Labs (Pro) | 1M caracteres | $99/mes |
| OpenAI Whisper | 25,000 min | $150/mes |
| **Total APIs** | - | **~$250/mes** |

---

## 9. BASE DE DATOS Y ARCHIVOS

### 9.1 Archivos de Entrada

**CTI Enriquecido (Excel):**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| cedula | string | Documento cliente |
| name | string | Nombre |
| celular | string | Teléfono |
| producto | string | Código producto |
| Tipo Producto | string | TARJETA/CARTERA/SOBREGIRO |
| dias mora | int | Días en mora |
| Saldo en mora | float | Monto vencido |
| Pago Minimo | float | Pago mínimo |
| GAC_proyectado | float | Gastos cobranza |
| total_a_pagar | float | Total a cobrar |
| campaign | bool | Tiene campaña |
| mecanismo_detectado | string | Tipo de campaña |
| probabilidad_pago_ML | float | Predicción (0-1) |
| segmento_ML | string | A, B, C, D |
| oferta_principal | string | Script de oferta |
| negociacion_abono | string | Script de abono |

### 9.2 Archivos de Salida

**Resultados de llamadas (CSV):**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| fecha | datetime | Timestamp |
| cedula | string | Documento |
| nombre | string | Nombre |
| celular | string | Teléfono |
| producto | string | Producto |
| dias_mora | int | Días mora |
| saldo_mora | float | Saldo |
| probabilidad | float | Prob. predicha |
| segmento | string | Segmento |
| resultado | string | EXITOSO/SIN_ACUERDO/SIN_CONTESTAR/ERROR |
| monto_acordado | float | Compromiso de pago |
| duracion_seg | int | Duración llamada |

### 9.3 Logs

**Ubicaciones:**

| Log | Ruta | Contenido |
|-----|------|-----------|
| Voicebot | /var/log/asterisk/voicebot.log | Conversaciones |
| Asterisk | /var/log/asterisk/full | Llamadas SIP |
| Marcador | ./marcador.log | Actividad marcador |

**Formato de log voicebot:**

```
2026-01-20 10:15:32 | INFO | Nueva sesión: call_20260120101532_1234567890
2026-01-20 10:15:33 | INFO | 🤖 Bot dice: Buenos días, le habla...
2026-01-20 10:15:40 | INFO | 📝 Cliente dice: Sí, soy yo
2026-01-20 10:15:41 | INFO | 🤖 Bot dice: Para continuar...
2026-01-20 10:16:15 | INFO | ✅ Llamada exitosa: call_... - Monto: 498000
```

---

## 10. OPERACIÓN DIARIA

### 10.1 Flujo de Operación

```
06:00  Recibir CTI del banco (automático o manual)
         ↓
06:30  Ejecutar enriquecimiento
         python3 enriquecer_cti.py CTI_DIARIO.xlsx CTI_ENRIQUECIDO.xlsx
         ↓
07:00  Generar scripts
         python3 generador_scripts.py CTI_ENRIQUECIDO.xlsx scripts.xlsx
         ↓
07:30  Revisar métricas en dashboard
         streamlit run dashboard.py
         ↓
08:00  Iniciar marcador
         python3 marcador.py --cti CTI_ENRIQUECIDO.xlsx
         ↓
08:00-20:00  Llamadas automáticas
         ↓
20:00  Marcador se detiene automáticamente
         ↓
20:30  Exportar resultados
         Revisar resultados_llamadas.csv
         ↓
21:00  Generar reporte del día
```

### 10.2 Comandos del Operador

```bash
# Iniciar marcador
source /opt/voicebot/voicebot/venv/bin/activate
source /opt/voicebot/voicebot/.env
cd /opt/voicebot/voicebot
python3 marcador.py --cti ../02_datos/salida/CTI_ENRIQUECIDO.xlsx

# Ver logs en tiempo real
tail -f /var/log/asterisk/voicebot.log

# Ver llamadas activas en Asterisk
sudo asterisk -rx "core show channels"

# Pausar marcador
Ctrl+C  (el marcador guarda resultados antes de salir)

# Ver estadísticas Asterisk
sudo asterisk -rx "core show calls"
```

### 10.3 Cron Jobs Sugeridos

```bash
# /etc/crontab

# Limpiar audios temporales cada hora
0 * * * * root find /var/lib/asterisk/sounds/voicebot -mmin +60 -delete

# Rotar logs diariamente
0 0 * * * root logrotate /etc/logrotate.d/voicebot

# Backup de resultados diario
0 21 * * * root cp /opt/voicebot/voicebot/resultados_llamadas.csv /backup/resultados_$(date +\%Y\%m\%d).csv
```

---

## 11. MONITOREO Y LOGS

### 11.1 Métricas Clave

| Métrica | Cálculo | Objetivo |
|---------|---------|----------|
| Tasa de contacto | Contestadas / Intentadas | > 50% |
| Tasa de conversión | Exitosas / Contestadas | > 15% |
| Duración promedio | Suma(duraciones) / Total | 2-3 min |
| Llamadas/hora | Total / Horas | > 100 |
| Monto comprometido | Suma(montos_acordados) | Variable |

### 11.2 Dashboard de Monitoreo

El dashboard Streamlit incluye:

- KPIs en tiempo real
- Distribución por segmento
- Resultados por hora
- Comparativo diario/semanal

```bash
streamlit run dashboard.py --server.port 8501
```

### 11.3 Alertas Sugeridas

| Condición | Acción |
|-----------|--------|
| Tasa contacto < 30% | Verificar troncal SIP |
| Errores TTS > 5/hora | Verificar API Eleven Labs |
| Errores STT > 5/hora | Verificar API OpenAI |
| Asterisk no responde | Reiniciar servicio |
| CPU > 90% | Reducir llamadas concurrentes |

---

## 12. TROUBLESHOOTING

### 12.1 Problemas Comunes

| Problema | Causa | Solución |
|----------|-------|----------|
| "Connection refused AMI" | AMI no habilitado | Verificar manager.conf |
| "Error TTS: 401" | API key inválida | Verificar ELEVENLABS_API_KEY |
| "Error STT: 401" | API key inválida | Verificar OPENAI_API_KEY |
| Audio no se reproduce | Permisos | chmod asterisk:asterisk |
| Llamadas no salen | Trunk caído | Verificar pjsip show endpoints |
| "File not found: AGI" | Ruta incorrecta | Verificar path en dialplan |

### 12.2 Comandos de Diagnóstico

```bash
# Verificar Asterisk
sudo systemctl status asterisk
sudo asterisk -rx "core show version"
sudo asterisk -rx "pjsip show endpoints"
sudo asterisk -rx "manager show users"

# Verificar conectividad APIs
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/voices
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Verificar Python
python3 -c "import aiohttp; print('OK')"
python3 motor_conversacion.py

# Logs
tail -f /var/log/asterisk/full
tail -f /var/log/asterisk/voicebot.log
```

### 12.3 Reinicio de Servicios

```bash
# Reiniciar Asterisk
sudo systemctl restart asterisk

# Reiniciar marcador
pkill -f "python3 marcador.py"
cd /opt/voicebot/voicebot
source venv/bin/activate
source .env
python3 marcador.py --cti CTI.xlsx &
```

---

## 13. SEGURIDAD

### 13.1 Credenciales

| Credencial | Almacenamiento | Acceso |
|------------|----------------|--------|
| API Keys | Variables de entorno (.env) | Solo root/voicebot |
| AMI Password | manager.conf | Solo root |
| SIP Password | pjsip.conf | Solo root |

### 13.2 Permisos de Archivos

```bash
# Scripts
chmod 750 /opt/voicebot/voicebot/*.py
chown root:asterisk /opt/voicebot/voicebot/*.py

# Configuración
chmod 600 /opt/voicebot/voicebot/.env
chown root:root /opt/voicebot/voicebot/.env

# Audios
chmod 770 /var/lib/asterisk/sounds/voicebot
chown asterisk:asterisk /var/lib/asterisk/sounds/voicebot
```

### 13.3 Firewall

```bash
# Solo permitir SIP desde proveedor
sudo ufw allow from IP_PROVEEDOR to any port 5060 proto udp

# Bloquear AMI desde internet
sudo ufw deny 5038

# Permitir RTP
sudo ufw allow 10000:20000/udp
```

### 13.4 Datos Sensibles

- Los logs NO deben contener cédulas completas
- Las grabaciones deben cifrarse o eliminarse después de X días
- Cumplir con Ley 1581 de 2012 (Habeas Data Colombia)

---

## 14. COSTOS OPERATIVOS

### 14.1 Desglose Mensual (1,000 llamadas/día)

| Concepto | Costo/mes |
|----------|-----------|
| Eleven Labs (Pro) | $99 |
| OpenAI Whisper | $150 |
| Servidor (8GB/4CPU) | $40-80 |
| Troncal SIP (~15,000 min) | $150-300 |
| **Total** | **$440-630/mes** |

### 14.2 Comparativo vs Call Center

| Concepto | Voicebot | Call Center |
|----------|----------|-------------|
| Costo por llamada | ~$0.015 | ~$0.50-1.00 |
| Llamadas/día (10 agentes) | 1,000+ | ~500 |
| Horario | 24/7 | 8h/día |
| Escalabilidad | Inmediata | Contratación |
| Consistencia | 100% | Variable |

**Ahorro estimado:** 70-85% vs call center tradicional

---

## 15. ROADMAP Y MEJORAS FUTURAS

### 15.1 Corto Plazo (1-3 meses)

- [ ] Reentrenar modelo XGBoost con datos reales
- [ ] Implementar grabación de llamadas
- [ ] Dashboard de monitoreo en tiempo real
- [ ] Alertas por email/Slack

### 15.2 Mediano Plazo (3-6 meses)

- [ ] Integración con CRM del banco
- [ ] Detección de emociones en voz
- [ ] A/B testing de scripts
- [ ] Reportes automáticos diarios

### 15.3 Largo Plazo (6-12 meses)

- [ ] Soporte multiidioma
- [ ] Bot de WhatsApp integrado
- [ ] Predicción de mejor hora para llamar
- [ ] Agente IA más conversacional (LLM)

---

## 16. ANEXOS

### 16.1 Glosario

| Término | Definición |
|---------|------------|
| AGI | Asterisk Gateway Interface - protocolo para scripts externos |
| AMI | Asterisk Manager Interface - API de control de Asterisk |
| CTI | Computer Telephony Integration - archivo de clientes |
| GAC | Gastos de Cobranza |
| IVR | Interactive Voice Response |
| PBX | Private Branch Exchange - central telefónica |
| PSTN | Public Switched Telephone Network - red telefónica |
| SIP | Session Initiation Protocol - protocolo VoIP |
| STT | Speech-to-Text - voz a texto |
| TTS | Text-to-Speech - texto a voz |

### 16.2 Referencias

- [Asterisk Documentation](https://wiki.asterisk.org/)
- [Eleven Labs API](https://docs.elevenlabs.io/)
- [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text)
- [PJSIP Configuration](https://wiki.asterisk.org/wiki/display/AST/PJSIP)

### 16.3 Contactos

| Rol | Contacto |
|-----|----------|
| Desarrollo | [Equipo de desarrollo] |
| Infraestructura | [Equipo de infra] |
| Proveedor SIP | [Contacto proveedor] |

---

**Documento preparado por:** Equipo de Desarrollo Voicebot  
**Fecha:** Enero 2026  
**Versión:** 1.0

---

*Este documento es confidencial y propiedad del Banco de Bogotá.*
