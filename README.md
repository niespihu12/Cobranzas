# 🏦 Voicebot Cobranzas - Banco de Bogotá

Sistema de inteligencia para optimización de cobranzas mediante Machine Learning.

---

## 📋 Contenido

1. [Descripción](#descripción)
2. [Instalación](#instalación)
3. [Uso Rápido](#uso-rápido)
4. [Estructura](#estructura)
5. [Pipeline](#pipeline)
6. [Modelo ML](#modelo-ml)
7. [Dashboard](#dashboard)
8. [Mantenimiento](#mantenimiento)
9. [Troubleshooting](#troubleshooting)

---

## 📖 Descripción

### ¿Qué hace?

1. **Enriquece el CTI** diario con:
   - Cálculo de Gastos de Cobranza (GAC)
   - Parseo de campañas especiales
   - Predicción de probabilidad de pago (XGBoost)
   - Segmentación A, B, C, D

2. **Genera scripts** personalizados para el Voicebot

3. **Dashboard** interactivo para monitoreo

### Flujo

```
CTI Banco → enriquecer_cti.py → generador_scripts.py → Voicebot
                ↓
           Dashboard (monitoreo)
```

---

## 🚀 Instalación

```bash
# Clonar
git clone https://github.com/giohua0817/voicebot-cobranzas.git
cd voicebot-cobranzas

# Instalar dependencias
pip install pandas numpy openpyxl xgboost scikit-learn streamlit plotly

# Verificar
python3 03_scripts/tests_verificacion.py
```

---

## ⚡ Uso Rápido

### Línea de Comandos

```bash
# 1. Enriquecer CTI
python3 03_scripts/enriquecer_cti.py \
    02_datos/entrada/CTI_DIARIO.xlsx \
    02_datos/salida/CTI_ENRIQUECIDO.xlsx \
    04_modelo_ml/modelo_xgboost_SIMULADO.pkl

# 2. Generar scripts
python3 03_scripts/generador_scripts.py \
    02_datos/salida/CTI_ENRIQUECIDO.xlsx \
    02_datos/salida/scripts.xlsx
```

### Dashboard

```bash
streamlit run dashboard.py
# Abre en http://localhost:8501
```

---

## 📁 Estructura

```
voicebot_cobranzas/
├── dashboard.py                    # Dashboard Streamlit
├── README.md                       # Este archivo
├── GUIA_DESARROLLADOR.md          # Guía técnica detallada
│
├── 01_documentacion/
│   └── DOCUMENTACION_TECNICA.md
│
├── 02_datos/
│   ├── entrada/                    # CTI del banco
│   ├── salida/                     # CTI procesado + scripts
│   └── historico_simulado/
│
├── 03_scripts/
│   ├── enriquecer_cti.py          # ⭐ Script principal
│   ├── generador_scripts.py        # Genera guiones
│   ├── generador_historico.py      # Datos de prueba
│   └── tests_verificacion.py       # 43 tests
│
└── 04_modelo_ml/
    ├── entrenar_xgboost.py         # Entrenador
    ├── modelo_xgboost_SIMULADO.pkl # Modelo
    └── metricas_modelo_SIMULADO.txt
```

---

## 🔄 Pipeline

### Entrada: CTI del Banco (Excel)

| Campo | Descripción |
|-------|-------------|
| `cedula` | Documento |
| `name` | Nombre |
| `dias mora` | Días en mora |
| `Saldo en mora` | Monto vencido |
| `campaign` | true/false |
| `POPUP_CAMP` | Código campaña |

### Salida: CTI Enriquecido

| Campo Nuevo | Descripción |
|-------------|-------------|
| `GAC_proyectado` | Gastos de cobranza |
| `mecanismo_detectado` | NOVACION, CONSOLIDACION, etc. |
| `probabilidad_pago_ML` | 0-100% |
| `segmento_ML` | A, B, C, D |
| `valor_esperado_ML` | prob × saldo |

---

## 🤖 Modelo ML

### Métricas (Modelo Simulado)

| Métrica | Valor |
|---------|-------|
| AUC-ROC | 66.26% |
| Accuracy | 84.85% |

### Variables Importantes

| Variable | Importancia |
|----------|-------------|
| Tiene Campaña | 35.4% |
| Requiere Pago | 17.9% |
| Días de Mora | 9.0% |

### Segmentación

| Segmento | Probabilidad | Acción |
|----------|--------------|--------|
| A | ≥75% | 🟢 Llamar primero |
| B | 50-74% | 🔵 Prioridad media |
| C | 25-49% | 🟡 Prioridad baja |
| D | <25% | 🔴 Evaluar |

### ⚠️ IMPORTANTE

El modelo actual es **SIMULADO**. Para producción:

```bash
# 1. Obtener histórico real (mínimo 6 meses)
# 2. Reentrenar
python3 04_modelo_ml/entrenar_xgboost.py historico_real.xlsx
```

---

## 📊 Dashboard

### Ejecutar

```bash
streamlit run dashboard.py
```

### Características

- 5 Tabs: Resumen, Segmentación, Modelo ML, Campañas, Explorar
- Filtros interactivos
- Gráficos Plotly
- Exportar CSV

---

## 🔧 Mantenimiento

### Actualizar Tabla GAC

Editar `03_scripts/enriquecer_cti.py`, línea ~140:

```python
GAC_TABLE = {
    (1, 10): {'tarifa': 0.00, 'min': 0, 'max': 0},
    (11, 15): {'tarifa': 0.06, 'min': 10000, 'max': 260000},
    # modificar según nuevas tarifas...
}
```

### Agregar Mecanismo

Editar función `parsear_popup_camp()`:

```python
elif 'NUEVO_MECANISMO' in popup_upper:
    resultado['mecanismo'] = 'NUEVO_MECANISMO'
```

### Ejecutar Tests

```bash
python3 03_scripts/tests_verificacion.py
# Debe pasar 43/43
```

---

## 🐛 Troubleshooting

| Error | Solución |
|-------|----------|
| `File does not exist: dashboard.py` | Verificar que estás en la carpeta correcta |
| `No module named 'xgboost'` | `pip install xgboost` |
| `No se cargó el modelo` | Verificar ruta del .pkl |
| Dashboard no encuentra CTI | Subir archivo desde sidebar |

---

## 📄 Info

**Repositorio:** https://github.com/giohua0817/voicebot-cobranzas  
**Versión:** 1.0  
**Fecha:** Enero 2026
