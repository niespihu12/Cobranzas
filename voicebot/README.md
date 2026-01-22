# 📞 Voicebot Cobranzas - Asterisk + Eleven Labs

Sistema de llamadas automáticas de cobranza con inteligencia artificial.

---

## 🏗 Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   MARCADOR  │────▶│  ASTERISK   │────▶│   CLIENTE   │
│  (Python)   │     │    (PBX)    │◀────│  (Teléfono) │
└──────┬──────┘     └──────┬──────┘     └─────────────┘
       │                   │
       │           ┌───────┴───────┐
       │           │   AGI BRIDGE  │
       │           │   (Python)    │
       │           └───────┬───────┘
       │                   │
       │    ┌──────────────┼──────────────┐
       │    │              │              │
       ▼    ▼              ▼              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    CTI      │     │   WHISPER   │     │ ELEVEN LABS │
│  (Clientes) │     │    (STT)    │     │    (TTS)    │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 📁 Estructura

```
voicebot/
├── motor_conversacion.py    # Lógica de conversación
├── elevenlabs_tts.py        # Text-to-Speech
├── whisper_stt.py           # Speech-to-Text
├── voicebot_agi.py          # Puente AGI ↔ Asterisk
├── marcador.py              # Marcador automático
├── config/
│   ├── asterisk_config.conf # Dialplan Asterisk
│   └── .env.example         # Variables de entorno
└── README.md
```

---

## 🚀 Instalación

### 1. Requisitos

```bash
# Sistema
sudo apt update
sudo apt install asterisk ffmpeg python3-pip

# Python
pip3 install aiohttp pandas openpyxl
```

### 2. Configurar APIs

```bash
# Copiar y editar variables
cp config/.env.example .env
nano .env

# Configurar:
# - ELEVENLABS_API_KEY
# - OPENAI_API_KEY
# - ASTERISK_*
```

### 3. Configurar Asterisk

```bash
# Copiar dialplan
sudo cp config/asterisk_config.conf /etc/asterisk/extensions_voicebot.conf

# Editar extensions.conf
sudo nano /etc/asterisk/extensions.conf
# Agregar: #include extensions_voicebot.conf

# Configurar AMI
sudo nano /etc/asterisk/manager.conf
# Agregar usuario voicebot (ver asterisk_config.conf)

# Recargar
sudo asterisk -rx "dialplan reload"
sudo asterisk -rx "manager reload"
```

### 4. Instalar Voicebot

```bash
# Crear directorio
sudo mkdir -p /opt/voicebot
sudo cp *.py /opt/voicebot/
sudo chmod +x /opt/voicebot/voicebot_agi.py

# Crear directorio de audios
sudo mkdir -p /var/lib/asterisk/sounds/voicebot
sudo chown asterisk:asterisk /var/lib/asterisk/sounds/voicebot
```

---

## ⚡ Uso

### Ejecutar Marcador

```bash
# Cargar variables de entorno
source .env

# Ejecutar con CTI
python3 marcador.py --cti CTI_ENRIQUECIDO.xlsx --max-calls 100

# Modo prueba (sin llamadas reales)
python3 marcador.py --cti CTI_ENRIQUECIDO.xlsx --dry-run
```

### Opciones del Marcador

| Opción | Descripción | Default |
|--------|-------------|---------|
| `--cti` | Ruta al CTI enriquecido | Requerido |
| `--max-calls` | Máximo de llamadas | Sin límite |
| `--concurrent` | Llamadas simultáneas | 5 |
| `--dry-run` | Solo simular | False |

### Prueba Manual en Asterisk

```bash
# Llamada de prueba
asterisk -rx "channel originate PJSIP/trunk/3001234567 extension s@voicebot-cobranzas"

# Ver logs
tail -f /var/log/asterisk/voicebot.log
```

---

## 🔄 Flujo de Conversación

```
1. SALUDO
   Bot: "Buenos días, le habla el asistente virtual del Banco de Bogotá.
         ¿Me comunico con Juan Pérez?"
   
2. IDENTIFICACIÓN
   Bot: "Para continuar, confirme los últimos 4 dígitos de su cédula."
   Cliente: "7890"
   
3. OFERTA PRINCIPAL
   Bot: "Su tarjeta presenta un saldo en mora de 1 millón 500 mil pesos
         con 45 días de atraso. El valor total a pagar es 1 millón 600 mil.
         ¿Puede realizar este pago hoy?"
   
4A. SI ACEPTA → CIERRE EXITOSO
    Bot: "Excelente. Queda registrado su compromiso de pago..."
    
4B. SI RECHAZA → NEGOCIACIÓN ABONO
    Bot: "Entiendo. Como alternativa, puede hacer un abono mínimo de
          160 mil pesos. ¿Le interesa esta opción?"
    
5. CIERRE
   Bot: "Gracias por su atención. Que tenga un excelente día."
```

---

## 📊 Resultados

Los resultados se guardan en `resultados_llamadas.csv`:

| Campo | Descripción |
|-------|-------------|
| fecha | Timestamp de la llamada |
| cedula | Documento del cliente |
| nombre | Nombre del cliente |
| celular | Teléfono |
| resultado | EXITOSO, SIN_ACUERDO, SIN_CONTESTAR, ERROR |
| monto_acordado | Monto del compromiso |
| duracion_seg | Duración en segundos |

---

## ⚙️ Configuración Avanzada

### Cambiar Voz

```python
# En elevenlabs_tts.py
VOCES = {
    'bella': 'EXAVITQu4vr4xnSDxMaL',      # Mujer, clara (default)
    'rachel': '21m00Tcm4TlvDq8ikWAM',      # Mujer, profesional
    'adam': 'pNInz6obpgDQGcFmaJgB',        # Hombre, confiable
}
```

### Ajustar Tiempos

```python
# En voicebot_agi.py
self.timeout_respuesta = 7000  # 7 segundos para responder
self.silencio_fin = 2          # 2 segundos de silencio = fin de habla
self.max_duracion = 300        # 5 minutos máximo por llamada
```

### Modificar Scripts

Editar `motor_conversacion.py`, métodos `_estado_*()`:

```python
def _estado_saludo(self):
    mensaje = """
    Buenos días, le habla [TU TEXTO AQUÍ]...
    """
```

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| "Error conectando a AMI" | Verificar manager.conf y puerto 5038 |
| "Error TTS" | Verificar ELEVENLABS_API_KEY |
| "Error STT" | Verificar OPENAI_API_KEY |
| Audio no se reproduce | Verificar permisos en /var/lib/asterisk/sounds |
| Llamadas no salen | Verificar trunk SIP y dialplan |

### Logs

```bash
# Log del voicebot
tail -f /var/log/asterisk/voicebot.log

# Log de Asterisk
tail -f /var/log/asterisk/full

# Consola Asterisk en vivo
asterisk -rvvvv
```

---

## 📈 Métricas Recomendadas

| Métrica | Objetivo |
|---------|----------|
| Tasa de contacto | > 50% |
| Tasa de conversión | > 15% |
| Duración promedio | 2-3 min |
| Llamadas/hora | ~100 |

---

## 🔐 Seguridad

- Las API keys deben estar en variables de entorno, nunca en código
- El AMI solo debe escuchar en localhost (127.0.0.1)
- Usar firewall para proteger puerto SIP (5060)
- Logs no deben contener datos sensibles completos

---

## 📄 Licencia

Proyecto privado - Banco de Bogotá © 2026
