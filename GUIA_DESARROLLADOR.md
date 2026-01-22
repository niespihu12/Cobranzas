# 📘 Guía del Desarrollador - Voicebot Cobranzas

Documentación técnica completa para el equipo de desarrollo.

---

## 📋 Índice

1. [Contexto del Negocio](#1-contexto-del-negocio)
2. [Arquitectura Técnica](#2-arquitectura-técnica)
3. [Componentes Detallados](#3-componentes-detallados)
4. [Reglas de Negocio](#4-reglas-de-negocio)
5. [API de Funciones](#5-api-de-funciones)
6. [Base de Datos / Archivos](#6-base-de-datos--archivos)
7. [Despliegue](#7-despliegue)
8. [Monitoreo](#8-monitoreo)
9. [Guía de Contribución](#9-guía-de-contribución)

---

## 1. Contexto del Negocio

### 1.1 Problema

El Banco de Bogotá tiene miles de clientes en mora diariamente. El Voicebot necesita:
- Saber a quién llamar primero
- Qué oferta hacer a cada cliente
- Calcular correctamente los gastos de cobranza

### 1.2 Solución

Este sistema:
1. Recibe el CTI diario (lista de clientes en mora)
2. Calcula GAC según tabla oficial
3. Detecta campañas especiales del campo POPUP_CAMP
4. Predice probabilidad de pago con ML
5. Genera scripts personalizados

### 1.3 Métricas de Éxito

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Tasa de Contacto | >50% | 50% (estimado) |
| Tasa de Pago | >15% | 14.9% (simulado) |
| AUC-ROC Modelo | >70% | 66.26% (simulado) |

---

## 2. Arquitectura Técnica

### 2.1 Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Lenguaje | Python | 3.8+ |
| ML | XGBoost | 1.7+ |
| Data | Pandas, NumPy | 1.5+, 1.21+ |
| Dashboard | Streamlit, Plotly | 1.28+, 5.15+ |
| Archivos | openpyxl | 3.0+ |

### 2.2 Diagrama de Componentes

```
┌──────────────────────────────────────────────────────────────┐
│                      CAPA DE ENTRADA                         │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                  │
│  │   CTI BANCO     │    │   MODELO ML     │                  │
│  │   (Excel)       │    │   (.pkl)        │                  │
│  └────────┬────────┘    └────────┬────────┘                  │
│           │                      │                           │
└───────────┼──────────────────────┼───────────────────────────┘
            │                      │
            ▼                      ▼
┌──────────────────────────────────────────────────────────────┐
│                   CAPA DE PROCESAMIENTO                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  enriquecer_cti.py                     │  │
│  │                                                        │  │
│  │  Funciones:                                            │  │
│  │  • calcular_gac(dias_mora, pago_minimo)               │  │
│  │  • parsear_popup_camp(popup_camp)                      │  │
│  │  • predecir_probabilidad_xgboost(row)                  │  │
│  │  • enriquecer_cti(df, modelo_path)                     │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │               generador_scripts.py                     │  │
│  │                                                        │  │
│  │  Funciones:                                            │  │
│  │  • generar_script_sin_campana(row)                     │  │
│  │  • generar_script_con_campana(row)                     │  │
│  │  • generar_oferta_campana(row)                         │  │
│  │  • generar_script_abono(row)                           │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│                      CAPA DE SALIDA                          │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                  │
│  │ CTI ENRIQUECIDO │    │    SCRIPTS      │                  │
│  │   (Excel)       │    │   (Excel)       │                  │
│  └─────────────────┘    └─────────────────┘                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    dashboard.py                         │ │
│  │                                                         │ │
│  │  • Streamlit + Plotly                                   │ │
│  │  • Filtros interactivos                                 │ │
│  │  • Gráficos en tiempo real                              │ │
│  │                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Componentes Detallados

### 3.1 enriquecer_cti.py

**Ubicación:** `03_scripts/enriquecer_cti.py`

**Propósito:** Script principal que procesa el CTI diario.

**Uso desde línea de comandos:**

```bash
python3 enriquecer_cti.py <CTI_entrada> <CTI_salida> [modelo.pkl]
```

**Uso como módulo:**

```python
from enriquecer_cti import calcular_gac, parsear_popup_camp, enriquecer_cti
import pandas as pd

# Cargar datos
df = pd.read_excel('CTI.xlsx')

# Enriquecer
df_enriquecido = enriquecer_cti(df, 'modelo_xgboost.pkl')

# Guardar
df_enriquecido.to_excel('CTI_ENRIQUECIDO.xlsx', index=False)
```

**Funciones principales:**

| Función | Parámetros | Retorno |
|---------|------------|---------|
| `calcular_gac(dias_mora, pago_minimo)` | int, float | float (GAC con IVA) |
| `parsear_popup_camp(popup_camp)` | str | dict |
| `predecir_probabilidad_xgboost(row)` | pd.Series | float (0-1) |
| `enriquecer_cti(df, modelo_path)` | DataFrame, str | DataFrame |

---

### 3.2 generador_scripts.py

**Ubicación:** `03_scripts/generador_scripts.py`

**Propósito:** Genera guiones de conversación personalizados.

**Uso:**

```bash
python3 generador_scripts.py <CTI_ENRIQUECIDO> <scripts_salida>
```

**Flujos de conversación:**

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO SIN CAMPAÑA                        │
│                                                             │
│  APERTURA → IDENTIFICACIÓN → COBRAR PAGO MÍNIMO + GAC      │
│                                     │                       │
│                            ¿Puede pagar?                    │
│                            /         \                      │
│                          SÍ          NO                     │
│                          ↓            ↓                     │
│                       CIERRE    OFRECER ABONO               │
│                       EXITOSO         │                     │
│                                ¿Puede abonar?               │
│                                /         \                  │
│                              SÍ          NO                 │
│                              ↓            ↓                 │
│                           CIERRE   MECANISMOS BASE          │
│                           EXITOSO                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    FLUJO CON CAMPAÑA                        │
│                                                             │
│  APERTURA → IDENTIFICACIÓN → OFERTA CAMPAÑA ESPECIAL       │
│                                     │                       │
│                            ¿Acepta oferta?                  │
│                            /         \                      │
│                          SÍ          NO                     │
│                          ↓            ↓                     │
│                       CIERRE    OFRECER ABONO               │
│                       EXITOSO         │                     │
│                                       ↓                     │
│                                    CIERRE                   │
└─────────────────────────────────────────────────────────────┘
```

---

### 3.3 dashboard.py

**Ubicación:** `dashboard.py` (raíz del proyecto)

**Propósito:** Dashboard interactivo para monitoreo y análisis.

**Ejecutar:**

```bash
streamlit run dashboard.py
```

**Tabs disponibles:**

| Tab | Contenido |
|-----|-----------|
| Resumen Ejecutivo | KPIs, distribución mora, mecanismos |
| Segmentación | Gráfico por segmento, scatter plot |
| Modelo ML | Métricas, importancia de variables |
| Campañas | Análisis de campañas y mecanismos |
| Explorar Datos | Top clientes, búsqueda, exportar |

---

### 3.4 entrenar_xgboost.py

**Ubicación:** `04_modelo_ml/entrenar_xgboost.py`

**Propósito:** Entrenar/reentrenar el modelo de ML.

**Uso:**

```bash
python3 entrenar_xgboost.py <historico_gestiones.xlsx>
```

**Salida:**
- `modelo_xgboost.pkl` - Modelo serializado
- `metricas_modelo.txt` - Métricas de evaluación

---

## 4. Reglas de Negocio

### 4.1 Tabla de Gastos de Cobranza (GAC)

**Fuente oficial:** Documentación de reglas de negocio VoiceBot 2.0

| Días de Mora | Tarifa | Mínimo | Máximo |
|--------------|--------|--------|--------|
| 1 - 10 | 0% | $0 | $0 |
| 11 - 15 | 6% | $10,000 | $260,000 |
| 16 - 30 | 8% | $10,000 | $260,000 |
| 31 - 60 | 9% | $12,000 | $260,000 |
| 61 - 90 | 10% | $15,000 | $260,000 |
| > 90 | 12% | $15,000 | $260,000 |

**Fórmula:**
```python
GAC = min(max(PAGO_MINIMO * TARIFA, MINIMO), MAXIMO) * 1.19  # +IVA
```

**Código:**

```python
# Ubicación: enriquecer_cti.py, línea ~140
GAC_TABLE = {
    (1, 10): {'tarifa': 0.00, 'min': 0, 'max': 0},
    (11, 15): {'tarifa': 0.06, 'min': 10000, 'max': 260000},
    (16, 30): {'tarifa': 0.08, 'min': 10000, 'max': 260000},
    (31, 60): {'tarifa': 0.09, 'min': 12000, 'max': 260000},
    (61, 90): {'tarifa': 0.10, 'min': 15000, 'max': 260000},
    (91, 999): {'tarifa': 0.12, 'min': 15000, 'max': 260000}
}
```

### 4.2 Mecanismos de Campaña

| Mecanismo | Código POPUP_CAMP | Requiere Pago |
|-----------|-------------------|---------------|
| Novación | `NOVACION TASA X.XX%` | Sí (3-10%) |
| Pago Mora | `PM_SIN_PAGO`, `PM_SIN_PAGO_BTASA` | No |
| Consolidación | `CONSOLIDAR`, `CAMP_CONS_AMP` | No |
| Prórroga | `PRORROGA_ESPECIAL` | No |
| Cancelación Total | `CANCELACION_TOTAL` | Sí |

### 4.3 Reglas de Abono

**Tarjetas de Crédito:**
- < 35 días mora: Mínimo 10% del pago mínimo + GAC
- ≥ 35 días mora: Mínimo cuota mensual + GAC

**Créditos/Cartera:**
- Mínimo cuota más vencida + GAC + otros cargos

---

## 5. API de Funciones

### 5.1 calcular_gac

```python
def calcular_gac(dias_mora: int, pago_minimo: float) -> float:
    """
    Calcula los Gastos de Cobranza según la tabla oficial.
    
    Args:
        dias_mora: Días de mora del cliente
        pago_minimo: Monto del pago mínimo
        
    Returns:
        GAC calculado con IVA incluido
        
    Example:
        >>> calcular_gac(45, 1000000)
        107100.0
    """
```

### 5.2 parsear_popup_camp

```python
def parsear_popup_camp(popup_camp: str) -> dict:
    """
    Parsea el campo POPUP_CAMP para extraer información.
    
    Args:
        popup_camp: Código de campaña del CTI
        
    Returns:
        dict con keys:
            - mecanismo: str (NOVACION, CONSOLIDACION, etc.)
            - tasa_nueva: float o None
            - descuento_intereses: int (0-100)
            - descuento_capital: int (0-100)
            - requiere_pago: bool
            - es_consolidacion: bool
            - es_cancelacion: bool
            - baja_tasa: float o None
            
    Example:
        >>> parsear_popup_camp("PM_SIN_PAGO_BTASA_13")
        {
            'mecanismo': 'PAGO_MORA_O_AMPLIACION',
            'requiere_pago': False,
            'baja_tasa': 13.0,
            ...
        }
    """
```

### 5.3 generar_script_cliente

```python
def generar_script_cliente(row: pd.Series) -> dict:
    """
    Genera script personalizado para un cliente.
    
    Args:
        row: Fila del DataFrame CTI enriquecido
        
    Returns:
        dict con keys:
            - tipo: 'CON_CAMPANA' o 'SIN_CAMPANA'
            - apertura: str
            - identificacion: str
            - oferta_principal: str
            - negociacion_abono: str
            - cierre_exitoso: str
            - cierre_sin_acuerdo: str
            - datos_cliente: dict
    """
```

---

## 6. Base de Datos / Archivos

### 6.1 Esquema del CTI Original

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| unique_user_id | string | No | ID único |
| cedula | int | No | Documento |
| celular | string | No | Teléfono |
| name | string | Sí | Nombre |
| producto | string | No | Últimos 4 dígitos |
| Tipo Producto | string | No | TARJETA/CARTERA/SOBREGIRO |
| dias mora | int | No | Días en mora |
| Saldo en mora | float | No | Monto vencido |
| Saldo total | float | No | Deuda total |
| campaign | bool | No | Tiene campaña |
| POPUP_CAMP | string | Sí | Código campaña |

### 6.2 Esquema del CTI Enriquecido

Incluye todos los campos anteriores más:

| Campo Nuevo | Tipo | Descripción |
|-------------|------|-------------|
| GAC_proyectado | float | Gastos de cobranza |
| total_a_pagar | float | Pago mínimo + GAC |
| mecanismo_detectado | string | Tipo de campaña |
| requiere_pago | bool | Si exige pago inicial |
| descuento_intereses | int | % descuento |
| descuento_capital | int | % descuento |
| tasa_nueva | float | Tasa de campaña |
| baja_tasa | float | Reducción de tasa |
| probabilidad_pago_ML | float | Predicción (0-1) |
| segmento_ML | string | A, B, C, D |
| valor_esperado_ML | float | prob × saldo |

### 6.3 Modelo Serializado

**Archivo:** `04_modelo_ml/modelo_xgboost_SIMULADO.pkl`

**Estructura del pickle:**

```python
{
    'modelo': XGBClassifier,
    'features': ['dias_mora_al_momento', 'saldo_mora_al_momento', ...],
    'label_encoder_producto': LabelEncoder,
    'metricas': {
        'auc_roc': 0.6626,
        'accuracy': 0.8485,
        ...
    }
}
```

---

## 7. Despliegue

### 7.1 Desarrollo Local

```bash
# Clonar
git clone https://github.com/giohua0817/voicebot-cobranzas.git
cd voicebot-cobranzas

# Entorno virtual
python3 -m venv venv
source venv/bin/activate

# Dependencias
pip install -r requirements.txt

# Tests
python3 03_scripts/tests_verificacion.py

# Dashboard
streamlit run dashboard.py
```

### 7.2 Producción

**Requisitos del servidor:**
- Python 3.8+
- 4GB RAM mínimo
- Acceso a archivos CTI del banco

**Configuración:**

```bash
# Instalar
pip install -r requirements.txt

# Ejecutar pipeline (cron diario)
python3 03_scripts/enriquecer_cti.py \
    /ruta/cti/CTI_DIARIO.xlsx \
    /ruta/salida/CTI_ENRIQUECIDO.xlsx \
    /ruta/modelo/modelo_xgboost.pkl

# Dashboard (servicio)
streamlit run dashboard.py --server.port 8501 --server.headless true
```

### 7.3 Docker (Opcional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.headless", "true"]
```

---

## 8. Monitoreo

### 8.1 Logs

El sistema imprime logs a stdout:

```
============================================================
🚀 ENRIQUECIMIENTO DE CTI
============================================================
📂 Archivo entrada: CTI_DIARIO.xlsx
📂 Archivo salida: CTI_ENRIQUECIDO.xlsx
🤖 Modelo ML: modelo_xgboost.pkl

📊 Procesando 7504 registros...
   Procesados: 1000
   Procesados: 2000
   ...

✅ ENRIQUECIMIENTO COMPLETADO
📊 Total registros: 7504
💰 GAC total proyectado: $781,942,372
```

### 8.2 Métricas a Monitorear

| Métrica | Umbral | Acción |
|---------|--------|--------|
| AUC-ROC | < 60% | Reentrenar modelo |
| Registros procesados | = 0 | Verificar CTI entrada |
| GAC calculado | < 0 | Bug en calcular_gac |
| Scripts con "nan" | > 0 | Bug en generador |

### 8.3 Tests Automatizados

```bash
# Ejecutar todos los tests
python3 03_scripts/tests_verificacion.py

# Resultado esperado:
# ✅ Tests pasados: 43
# ❌ Tests fallidos: 0
```

---

## 9. Guía de Contribución

### 9.1 Flujo de Trabajo Git

```bash
# 1. Crear rama
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios
# ...

# 3. Ejecutar tests
python3 03_scripts/tests_verificacion.py

# 4. Commit
git add .
git commit -m "Descripción del cambio"

# 5. Push
git push origin feature/nueva-funcionalidad

# 6. Pull Request en GitHub
```

### 9.2 Estilo de Código

- PEP 8 para Python
- Docstrings en todas las funciones públicas
- Comentarios en español
- Tests para funciones nuevas

### 9.3 Añadir Nuevo Mecanismo

1. Editar `enriquecer_cti.py`:

```python
# En función parsear_popup_camp(), agregar:
elif 'NUEVO_MECANISMO' in popup_upper:
    resultado['mecanismo'] = 'NUEVO_MECANISMO'
    resultado['requiere_pago'] = True  # o False
```

2. Editar `generador_scripts.py`:

```python
# En función generar_oferta_campana(), agregar:
elif mecanismo == 'NUEVO_MECANISMO':
    return """
    🎯 OFERTA ESPECIAL: NUEVO MECANISMO
    
    [Descripción de la oferta...]
    """
```

3. Agregar test en `tests_verificacion.py`

4. Actualizar documentación

---

## 📞 Soporte

**Repositorio:** https://github.com/giohua0817/voicebot-cobranzas  
**Issues:** Crear issue en GitHub  
**Última actualización:** Enero 2026
