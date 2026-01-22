# Documentación Técnica - Voicebot Cobranzas
## Banco de Bogotá

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Equipo:** Inteligencia Voicebot

---

## 1. Resumen Ejecutivo

### 1.1 Objetivo del Proyecto

Desarrollar un sistema de inteligencia para el Voicebot de cobranzas que permita:

- **Priorizar llamadas** según probabilidad de pago (modelo XGBoost)
- **Calcular automáticamente** los Gastos de Cobranza (GAC)
- **Parsear campañas especiales** del campo POPUP_CAMP
- **Generar scripts personalizados** para cada cliente

### 1.2 Resultados Obtenidos

| Métrica | Valor |
|---------|-------|
| Registros procesados | 7,504 |
| GAC total proyectado | $781,942,372 |
| Clientes con campaña | 6,328 (84.3%) |
| Scripts generados | 7,504 |
| Precisión modelo ML (AUC-ROC) | 66.26% |

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         FLUJO DE DATOS                          │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  CTI BANCO   │  (Archivo diario con clientes en mora)
    │   (Excel)    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────┐
    │ enriquecer_cti.py │  
    │                  │  • Calcula GAC
    │                  │  • Parsea POPUP_CAMP
    │                  │  • Aplica modelo XGBoost
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │ CTI ENRIQUECIDO  │  (+ 22 columnas nuevas)
    │    (Excel)       │
    └──────┬───────────┘
           │
           ▼
    ┌────────────────────┐
    │ generador_scripts.py│  
    │                    │  • Genera guiones personalizados
    │                    │  • Flujo según campaña/producto
    └──────┬─────────────┘
           │
           ▼
    ┌──────────────────┐
    │    VOICEBOT      │  (Ejecuta scripts con clientes)
    └──────────────────┘
```

---

## 3. Estructura de Archivos

```
voicebot_cobranzas/
│
├── 01_documentacion/
│   └── DOCUMENTACION_TECNICA.md        ← Este documento
│
├── 02_datos/
│   ├── entrada/
│   │   ├── CTI_EJEMPLO_COMPLETO.xlsx   ← CTI con datos de prueba
│   │   ├── DEFINICION_CAMPANAS.xlsx    ← Catálogo de campañas
│   │   └── ESTRUCTURA_CTI.xlsx         ← Diccionario de datos
│   │
│   ├── salida/
│   │   ├── CTI_ENRIQUECIDO_COMPLETO.xlsx
│   │   ├── scripts_conversacion.xlsx
│   │   └── historico_gestiones_SIMULADO.xlsx
│   │
│   └── historico_simulado/
│       └── (datos para entrenar modelo)
│
├── 03_scripts/
│   ├── enriquecer_cti.py               ← Script principal
│   ├── generador_scripts.py            ← Generador de guiones
│   ├── generador_historico.py          ← Genera datos simulados
│   └── tests_verificacion.py           ← Suite de tests
│
└── 04_modelo_ml/
    ├── entrenar_xgboost.py             ← Entrenamiento del modelo
    ├── modelo_xgboost_SIMULADO.pkl     ← Modelo entrenado
    └── metricas_modelo_SIMULADO.txt    ← Métricas de evaluación
```

---

## 4. Componentes del Sistema

### 4.1 Script Principal: `enriquecer_cti.py`

**Propósito:** Enriquecer el CTI diario con cálculos y predicciones.

**Uso:**
```bash
python3 enriquecer_cti.py <CTI_entrada> <CTI_salida> [modelo.pkl]
```

**Ejemplo:**
```bash
python3 enriquecer_cti.py CTI_DIARIO.xlsx CTI_ENRIQUECIDO.xlsx modelo_xgboost.pkl
```

**Columnas que agrega:**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `GAC_proyectado` | Numérico | Gastos de cobranza calculados |
| `total_a_pagar` | Numérico | Pago mínimo + GAC |
| `mecanismo_detectado` | Texto | NOVACION, CONSOLIDACION, etc. |
| `requiere_pago` | Booleano | Si la campaña exige pago inicial |
| `descuento_intereses` | Numérico | % de descuento en intereses |
| `descuento_capital` | Numérico | % de descuento en capital |
| `probabilidad_pago_ML` | Numérico | Predicción XGBoost (0-1) |
| `segmento_ML` | Texto | A, B, C, D según probabilidad |
| `valor_esperado_ML` | Numérico | probabilidad × saldo_mora |

---

### 4.2 Generador de Scripts: `generador_scripts.py`

**Propósito:** Crear guiones personalizados para el Voicebot.

**Uso:**
```bash
python3 generador_scripts.py <CTI_ENRIQUECIDO> <scripts_salida>
```

**Flujos de conversación:**

| Escenario | Flujo |
|-----------|-------|
| **Sin campaña** | Cobrar pago mínimo + GAC → Ofrecer abono → Mecanismos base |
| **Con campaña** | Ofrecer campaña especial directamente → Si rechaza, ofrecer abono |

---

### 4.3 Modelo XGBoost: `entrenar_xgboost.py`

**Propósito:** Entrenar modelo de predicción de probabilidad de pago.

**Variables de entrada (features):**

| Variable | Descripción |
|----------|-------------|
| `dias_mora_al_momento` | Días de mora del cliente |
| `saldo_mora_al_momento` | Monto en mora |
| `tenia_campana` | Si tiene campaña especial (1/0) |
| `requeria_pago` | Si la campaña requiere pago (1/0) |
| `descuento_ofrecido` | % de descuento |
| `intento_numero` | Número de intento de llamada |
| `hora_num` | Hora de la gestión |
| `es_voicebot` | Si es voicebot o humano (1/0) |
| `producto_encoded` | Tipo de producto codificado |

**Variable objetivo:** `pago_realizado` (1 = pagó, 0 = no pagó)

**Métricas del modelo:**

| Métrica | Valor |
|---------|-------|
| AUC-ROC | 0.6626 |
| Accuracy | 0.8485 |

**Importancia de variables:**

| Variable | Importancia |
|----------|-------------|
| tenia_campana | 35.4% |
| requeria_pago | 17.9% |
| dias_mora_al_momento | 9.0% |
| descuento_ofrecido | 8.0% |

---

## 5. Reglas de Negocio Implementadas

### 5.1 Tabla de Gastos de Cobranza (GAC)

| Días de Mora | Tarifa | Mínimo | Máximo |
|--------------|--------|--------|--------|
| 1 - 10 | 0% | $0 | $0 |
| 11 - 15 | 6% + IVA | $10,000 + IVA | $260,000 + IVA |
| 16 - 30 | 8% + IVA | $10,000 + IVA | $260,000 + IVA |
| 31 - 60 | 9% + IVA | $12,000 + IVA | $260,000 + IVA |
| 61 - 90 | 10% + IVA | $15,000 + IVA | $260,000 + IVA |
| > 90 | 12% + IVA | $15,000 + IVA | $260,000 + IVA |

**Fórmula:**
```
GAC = MIN(MAX(PAGO_MINIMO × TARIFA, MINIMO), MAXIMO) × 1.19
```

---

### 5.2 Mecanismos de Negociación

| Mecanismo | Aplica a | Pago requerido |
|-----------|----------|----------------|
| **Novación** | Tarjetas de crédito | 3-10% según mora |
| **Pago Mora** | Todos (mora >31 días) | Saldo en mora con descuento |
| **Ampliación** | Créditos/Cartera | Intereses + cargos |
| **Consolidación** | Múltiples productos | NO requiere pago |
| **Prórroga** | Con campaña especial | NO requiere pago |
| **Cancelación Total** | Todos (mora >61 días) | Saldo total con descuento |

---

### 5.3 Reglas de Abono

**Tarjetas de Crédito:**
- Mora < 35 días: Mínimo 10% del pago mínimo + GAC
- Mora ≥ 35 días: Mínimo cuota mensual + GAC

**Créditos/Cartera:**
- Mínimo cuota más vencida + GAC + otros cargos

---

## 6. Instalación y Configuración

### 6.1 Requisitos

```
Python 3.8+
pandas
numpy
openpyxl
xgboost
scikit-learn
```

### 6.2 Instalación

```bash
pip install pandas numpy openpyxl xgboost scikit-learn
```

### 6.3 Ejecución del Pipeline Completo

```bash
# 1. Enriquecer CTI
python3 enriquecer_cti.py CTI_DIARIO.xlsx CTI_ENRIQUECIDO.xlsx modelo_xgboost.pkl

# 2. Generar scripts
python3 generador_scripts.py CTI_ENRIQUECIDO.xlsx scripts_conversacion.xlsx

# 3. (Opcional) Ejecutar tests
python3 tests_verificacion.py
```

---

## 7. Flujo de Uso Diario

```
06:00 AM  │  Banco genera CTI diario
          ▼
07:00 AM  │  Ejecutar enriquecer_cti.py
          │  → Calcula GAC
          │  → Predice probabilidades
          │  → Prioriza clientes
          ▼
07:30 AM  │  Ejecutar generador_scripts.py
          │  → Genera guiones personalizados
          ▼
08:00 AM  │  Cargar al Voicebot
          │  → Inicia llamadas por segmento A → B → C → D
          ▼
18:00 PM  │  Recopilar resultados
          │  → Alimentar histórico para reentrenar modelo
```

---

## 8. Segmentación de Clientes

| Segmento | Probabilidad | Prioridad | Acción |
|----------|--------------|-----------|--------|
| **A** | ≥ 75% | Alta | Llamar primero |
| **B** | 50% - 74% | Media-Alta | Llamar segundo |
| **C** | 25% - 49% | Media | Llamar tercero |
| **D** | < 25% | Baja | Llamar último / Evaluar si llamar |

---

## 9. Consideraciones Importantes

### 9.1 Datos Simulados

⚠️ **ADVERTENCIA:** El modelo actual fue entrenado con datos **SIMULADOS**.

- Las probabilidades NO reflejan comportamiento real de clientes
- Usar solo para demostración técnica y pruebas de integración
- Reentrenar con datos históricos reales antes de producción

### 9.2 Para Producción

1. Obtener histórico real de gestiones (mínimo 6 meses)
2. Reentrenar modelo XGBoost con datos reales
3. Validar métricas (AUC-ROC objetivo > 0.70)
4. Implementar monitoreo de drift del modelo
5. Reentrenar periódicamente (mensual recomendado)

---

## 10. Pruebas y Validación

### 10.1 Tests Disponibles

```bash
python3 tests_verificacion.py
```

| Test | Validaciones |
|------|--------------|
| Archivos fuente | Existencia de CTI, Campañas, Estructura |
| Carga CTI | Lectura correcta del Excel |
| Columnas críticas | Campos obligatorios presentes |
| calcular_gac | 9 casos de prueba |
| parsear_popup_camp | 13 casos de prueba |
| CTI enriquecido | Columnas nuevas generadas |

**Total:** 43 tests

---

## 11. Contacto y Soporte

**Equipo:** Inteligencia Voicebot  
**Proyecto:** Voicebot Cobranzas Banco de Bogotá  
**Versión:** 1.0 - Enero 2026

---

## Anexo A: Campos del CTI Original

| # | Campo | Descripción |
|---|-------|-------------|
| 1 | unique_user_id | Identificador único |
| 2 | Phone | Teléfono principal |
| 3 | name | Nombre del cliente |
| 4 | cedula | Número de cédula |
| 5 | campaign | true/false - tiene campaña |
| 6 | producto | Últimos 4 dígitos |
| 7 | Tipo Producto | TARJETA, CARTERA, etc. |
| 8 | dias mora | Días en mora |
| 9 | Saldo en mora | Monto vencido |
| 10 | Saldo total | Deuda total |
| 11 | POPUP_CAMP | Código de campaña especial |
| ... | ... | (45 campos en total) |

---

## Anexo B: Códigos de Campaña (POPUP_CAMP)

| Código | Mecanismo | Descripción |
|--------|-----------|-------------|
| `NOVACION TASA X.XX%` | Novación | Diferir saldo a nuevo plazo |
| `PM_SIN_PAGO` | Pago Mora | Sin pago inicial requerido |
| `PM_SIN_PAGO_BTASA_XX%` | Pago Mora | Con baja de tasa |
| `CONSOLIDAR XX%` | Consolidación | Unificar deudas |
| `PRORROGA_ESPECIAL` | Prórroga | Trasladar cuota |
| `CANCELACION_TOTAL_XX%` | Cancelación | Liquidar con descuento |

---

*Fin del documento*
