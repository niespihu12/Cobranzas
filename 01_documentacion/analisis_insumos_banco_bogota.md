# Análisis de Insumos - Proyecto Voicebot Cobranzas
## Banco de Bogotá

---

## 1. Resumen de Insumos Recibidos

| Documento | Descripción | Registros/Items |
|-----------|-------------|-----------------|
| **ESTRUCTURA_CTI_VOICEBOT_2_0_FINAL.xlsx** | Diccionario de datos del CTI | 57 campos |
| **CTI_EJEMPLO_VOICEBOT_MULTIPRODUCTO.xlsx** | Ejemplo real de CTI | 7,504 registros |
| **DEFINICIÓN_CAMPAÑAS_ESPECIALES.xlsx** | Catálogo de campañas | 24 campañas |
| **REGLAS_DE_NEGOCIO_VoiceBot_2_0.pdf** | Reglas y mecanismos | 9 páginas |

---

## 2. Estructura del CTI (57 campos)

### 2.1 Campos de Identificación
| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `unique_user_id` | Llave: +57+CEL+CC | +573132595404209336 |
| `cedula` | Documento sin dígito verificación | 1000410495 |
| `celular` | Celular principal | 3132595404 |
| `Phone`, `Phone_2`, `Phone_3` | Teléfonos con +57 | +573132595404 |
| `name`, `fullname` | Nombres del cliente | Cesar, Cesar Fiquitiva |

### 2.2 Campos del Producto
| Campo | Descripción | Valores |
|-------|-------------|---------|
| `producto` | Últimos 4 dígitos obligación | 4698 |
| `Nombre producto` | Descripción | Reestructurad, libre destino |
| `Tipo Producto` | Categoría | CARTERA, TARJETA DE CREDITO, SOBREGIRO |
| `Tipo Cartera` | Clasificación | CONSUMO, COMERCIAL |
| `OBLIGACION` | Número completo | 4506689999991234 |

### 2.3 Campos de Mora y Saldos
| Campo | Descripción | Rango Ejemplo |
|-------|-------------|---------------|
| `dias mora` | Días en mora | 2 - 150 |
| `PAGO MINIMO` | Valor a cobrar | $269K - $17M |
| `Saldo total` | Deuda total | $269K - $17M |
| `Capital Total` | Capital adeudado | Variable |
| `Capital Mora` | Capital en mora | Variable |
| `Cuota Mensual Aprox` | Cuota mensual | $162K - $355K |
| `Saldo en mora` | Monto vencido | Variable |

### 2.4 Campos de Intereses
| Campo | Descripción |
|-------|-------------|
| `Interes Corriente` | Intereses normales |
| `Interes Mora` | Intereses por mora |
| `Interes Extracontable` | Intereses extra |
| `Honorarios` | Gastos legales |
| `Tasa Interes` | Tasa E.A. del producto |

### 2.5 Campos de Campaña ⭐ CRÍTICOS
| Campo | Descripción | Valores |
|-------|-------------|---------|
| `campaign` | ¿Tiene campaña especial? | **true** / **false** |
| `POPUP_CAMP` | Código de campaña | PM_SIN_PAGO, NOVACION TASA... |
| `Campaña` | Nombre de campaña | NOVACIONES / BASE_CAMPAÑAS |
| `% Baja en cuenta interes campaña` | Descuento intereses | 0-100% |
| `% Baja en cuenta capital campaña` | Descuento capital | 0-25% |
| `% Baja Tasa` | Nueva tasa | 0-19.63% |

### 2.6 Campos de Control
| Campo | Descripción |
|-------|-------------|
| `Ciclo` | Fecha de corte |
| `Fecha Vencimiento` | Fin del crédito |
| `Ultima Neg Aplicada` | Último mecanismo |
| `Fecha Ultima Neg Aplicada` | Fecha último mecanismo |
| `BLOQUEO` | Tipo bloqueo (02, 03, 04) |
| `EXCLUIR` | Marcar para excluir |
| `CONCEPTO_EXCLUSION` | Razón de exclusión |
| `Marca Producto` | N, PM, PR, R |

---

## 3. Estadísticas del CTI Ejemplo

### 3.1 Distribución General
```
📊 Total Registros:     7,504
📊 Clientes Únicos:     1 (ejemplo multiproducto)

🎯 Con Campaña (True):  6,328 (84.4%)
🎯 Sin Campaña (False): 1,176 (15.6%)
```

### 3.2 Por Tipo de Producto
| Tipo Producto | Registros | % | Con Campaña | Días Mora Prom |
|---------------|-----------|---|-------------|----------------|
| CARTERA | 6,010 | 80.1% | 85.8% | 67.4 |
| TARJETA DE CREDITO | 1,429 | 19.0% | 82.2% | 59.0 |
| SOBREGIRO | 65 | 0.9% | 0.0% | 62.5 |

### 3.3 Top 10 Campañas Especiales (POPUP_CAMP)
| Campaña | Registros | Mecanismo |
|---------|-----------|-----------|
| CAMP_CONS_AMP/PM DCTO_INT 100% | 1,729 | Pago Mora / Ampliación |
| CAMP_CONS_AMP/PM DCTO_INT100%UCI | 905 | Pago Mora / Ampliación |
| PM_SIN_PAGO | 464 | Pago Mora sin pago |
| CAMP_CONS_AMP/PM DCTO_INT 85% | 291 | Pago Mora / Ampliación |
| PM_SIN_PAGO_BTASA 13% | 211 | Pago Mora sin pago |
| CAMP_CONS_PM DCTO 50% | 188 | Pago Mora |
| NOVACION TASA PONDERADA | 173 | Novación 48 meses |
| CAMP_CONS_AMP/PM DCTO_INT 100% BTASA 19.63% | 137 | Con baja tasa |
| NOVACION TASA 0.98% | 116 | Novación tasa baja |
| PRORROGA_ESPECIAL_UCI | 113 | Prórroga |

---

## 4. Campañas Especiales (24 tipos)

### 4.1 Mecanismos Disponibles
| Mecanismo | Descripción | Productos |
|-----------|-------------|-----------|
| **Pago Mora de Contado** | Descuentos en intereses para normalizar | Todos >31 días |
| **Ampliación de Plazo** | Diferir capital a nuevo plazo | Créditos |
| **Novación Saldo Total** | Rediferir saldo total | Tarjetas |
| **Cancelación Total** | Pago definitivo con descuentos | Todos >61 días |
| **Consolidación** | Unificar varios productos | Marcados especiales |
| **Prórroga** | Trasladar cuota al final | Campaña especial |

### 4.2 Matriz de Descuentos por Campaña
| Campaña | Int. Mora | Int. Corrientes | Capital | Requiere Pago | Baja Tasa |
|---------|-----------|-----------------|---------|---------------|-----------|
| CAMP_CCIALPN_PM/AMP_DCTO_INT 35% | 100% | 35% | No | Sí | No |
| CAMP_CONS_AMP/PM DCTO_INT 100% | 100% | 100% | No | Sí | No |
| CAMP_CONS_AMP/PM DCTO_INT100%_BTASA_13% | 100% | 100% | No | Sí | 13% |
| CAMP_UCI_CANCELACION_TOTAL_DCTO_CAPITAL_25% | 100% | 100% | 25% | Sí | No |
| PM_SIN_PAGO | 100% | 100% | No | **No** | No |
| PM_SIN_PAGO_BTASA 13% | 100% | 100% | No | **No** | 13% |
| CONSOLIDAR 13% NO PIDE PAGO | N/A | N/A | N/A | **No** | 13% |
| PRORROGA_ESPECIAL | 100% | 100% | No | **No** | Var |

---

## 5. Reglas de Negocio Clave

### 5.1 Gastos de Cobranza (GAC)
| Días Mora | Tarifa % | Valor Mínimo | Valor Máximo |
|-----------|----------|--------------|--------------|
| 1 - 10 | 0% | $0 | $0 |
| 11 - 15 | 6% + IVA | $10,000 + IVA | $260,000 + IVA |
| 16 - 30 | 8% + IVA | $10,000 + IVA | $260,000 + IVA |
| 31 - 60 | 9% + IVA | $12,000 + IVA | $260,000 + IVA |
| 61 - 90 | 10% + IVA | $15,000 + IVA | $260,000 + IVA |
| > 90 | 12% + IVA | $15,000 + IVA | $260,000 + IVA |

### 5.2 Flujo de Decisión Principal
```
┌─────────────────────────────────────────────────────────────────┐
│                    LECTURA CAMPO "campaign"                      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
       campaign = FALSE                campaign = TRUE
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│ 1. Cobrar Pago Mínimo   │     │ 1. NO cobrar Pago Mínimo        │
│ 2. + Gastos Cobranza    │     │ 2. Ofertar campaña POPUP_CAMP   │
│ 3. Plazo: 3 días        │     │ 3. Si rechaza → ofrecer abono   │
│ 4. Si no puede:         │     │ 4. Aplicar descuentos especiales│
│    → Ofrecer mecanismos │     │                                 │
└─────────────────────────┘     └─────────────────────────────────┘
```

### 5.3 Abonos Mínimos Permitidos
| Producto | Mora | Abono Mínimo |
|----------|------|--------------|
| Tarjeta de Crédito | < 35 días | > 10% del Pago Mínimo + GAC |
| Tarjeta de Crédito | ≥ 35 días | > Cuota Mensual Aprox + GAC |
| Créditos/Cartera | Cualquiera | ≥ Cuota Mensual Aprox + GAC + Otros cargos + Convenio |

### 5.4 Tiempo Entre Mecanismos
| Mecanismo | Sin Campaña | Con Campaña |
|-----------|-------------|-------------|
| Novación | 3 meses | No en mismo mes |
| Pago Mora (TC) | 4 meses | Sin restricción |
| Pago Mora (Hipotecario) | 3 años | Sin restricción |
| Pago Mora (Otros) | 12 meses | Sin restricción |
| Ampliación (≤60 días) | 4 meses | - |
| Ampliación (>60 días) | 6 meses | - |

### 5.5 Bloqueos Resultantes
| Mecanismo | Bloqueo Modificado | Bloqueo Reestructurado |
|-----------|-------------------|------------------------|
| Novación | Definitivo + 2 meses preventivo | Definitivo + 3 meses |
| Pago Mora | 120 días todos productos con cupo | - |
| Consolidación | Pierde productos incluidos | - |
| Ampliación | 2 meses | 3 meses |

---

## 6. Oportunidades para ML

### 6.1 Variables Predictivas Disponibles en CTI
```python
# Ya vienen en el CTI - Se pueden usar directamente
features_cti = {
    'producto': ['Tipo Producto', 'Tipo Cartera', 'Nombre producto'],
    'mora': ['dias mora', 'Saldo en mora', 'Capital Mora'],
    'financiero': ['PAGO MINIMO', 'Saldo total', 'Cuota Mensual Aprox', 'Tasa Interes'],
    'intereses': ['Interes Corriente', 'Interes Mora', 'Interes Extracontable', 'Honorarios'],
    'historial': ['Ultima Neg Aplicada', 'Fecha Ultima Neg Aplicada'],
    'estado': ['BLOQUEO', 'Marca Producto', 'Ciclo'],
    'campaña': ['campaign', 'POPUP_CAMP', '% Baja en cuenta interes campaña']
}
```

### 6.2 Variables a Calcular/Enriquecer
```python
# Features derivadas para ML
features_calculadas = {
    # Ratios financieros
    'ratio_mora_saldo': 'Saldo en mora / Saldo total',
    'ratio_capital_mora': 'Capital Mora / Capital Total',
    'cobertura_cuota': 'Cuota Mensual Aprox / Saldo en mora',
    
    # Proyecciones
    'dias_mora_proyectado': 'dias mora + días hasta pago',
    'gac_proyectado': 'Calcular GAC según tabla',
    'valor_total_pagar': 'PAGO MINIMO + GAC proyectado',
    
    # Temporales
    'dias_desde_ultima_neg': 'Hoy - Fecha Ultima Neg Aplicada',
    'puede_aplicar_mecanismo': 'Validar tiempo entre mecanismos',
    'dias_para_siguiente_bucket': 'Próximo corte de mora',
    
    # Campaña
    'tiene_campana_sin_pago': 'POPUP_CAMP contiene SIN_PAGO',
    'descuento_total_interes': '% Baja en cuenta interes campaña',
    'atractivo_campana': 'Score de qué tan buena es la campaña'
}
```

### 6.3 Modelos Propuestos con Datos Reales

#### Modelo 1: Probabilidad de Pago en 30 días
```
Features principales:
- dias mora (disponible ✓)
- Saldo en mora / Saldo total (calcular)
- Tipo Producto (disponible ✓)
- Cuota Mensual Aprox (disponible ✓)
- tiene_campana_sin_pago (calcular)
- Ultima Neg Aplicada (disponible ✓)

Target: ¿Pagó dentro de 30 días? (del histórico)
```

#### Modelo 2: Probabilidad de Aceptar Campaña
```
Features principales:
- POPUP_CAMP (disponible ✓)
- % Baja en cuenta interes campaña (disponible ✓)
- descuento_total (calcular)
- requiere_pago (del catálogo campañas)
- dias mora (disponible ✓)
- Tipo Producto (disponible ✓)

Target: ¿Aceptó la campaña? (del histórico)
```

#### Modelo 3: Mejor Mecanismo a Ofrecer
```
Features:
- Todos los anteriores
- mecanismos_disponibles (calcular según reglas)
- valor_abono_minimo (calcular según reglas)
- bloqueo_resultante (del catálogo)

Target: Mecanismo que generó pago (multiclase)
```

---

## 7. Integración con Arquitectura Propuesta

### 7.1 Flujo de Datos Actualizado
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  BANCO DE BOGOTÁ                    PLATAFORMA ML                          │
│  ══════════════                     ════════════                           │
│                                                                             │
│  ┌──────────────┐                  ┌──────────────────────────────────┐    │
│  │   CTI.xlsx   │                  │                                  │    │
│  │   (57 cols)  │ ────SFTP────▶   │  1. VALIDACIÓN                   │    │
│  │   7,500 reg  │                  │     • Campos obligatorios        │    │
│  └──────────────┘                  │     • Formato de datos           │    │
│                                     │     • Cédulas válidas            │    │
│  ┌──────────────┐                  │                                  │    │
│  │  CAMPAÑAS    │                  │  2. ENRIQUECIMIENTO              │    │
│  │  ESPECIALES  │ ────Config───▶  │     • Calcular GAC proyectado    │    │
│  │   (24 tipos) │                  │     • Validar tiempo mecanismos  │    │
│  └──────────────┘                  │     • Parsear POPUP_CAMP         │    │
│                                     │                                  │    │
│  ┌──────────────┐                  │  3. SCORING ML                   │    │
│  │   REGLAS     │                  │     • XGBoost Prob. Pago         │    │
│  │  DE NEGOCIO  │ ────Config───▶  │     • XGBoost Prob. Aceptación   │    │
│  │   (GAC, etc) │                  │     • Mejor Mecanismo            │    │
│  └──────────────┘                  │                                  │    │
│                                     │  4. SEGMENTACIÓN                 │    │
│                                     │     • A: Voicebot + campaña      │    │
│                                     │     • B: Voicebot + seguimiento  │    │
│                                     │     • C: Agente humano           │    │
│                                     │     • D: No gestionar            │    │
│                                     │                                  │    │
│                                     │  5. PRIORIZACIÓN                 │    │
│                                     │     • Ordenar por valor esperado │    │
│                                     │     • Respetar cabeza de mora    │    │
│                                     └──────────────────────────────────┘    │
│                                                    │                        │
│                                                    ▼                        │
│                                     ┌──────────────────────────────────┐    │
│                                     │  CTI_ENRIQUECIDO.xlsx            │    │
│                                     │  • 57 cols originales            │    │
│                                     │  • + prob_pago_30d               │    │
│                                     │  • + prob_aceptacion_campana     │    │
│                                     │  • + mejor_mecanismo             │    │
│                                     │  • + segmento (A/B/C/D)          │    │
│                                     │  • + orden_llamada               │    │
│                                     │  • + gac_proyectado              │    │
│                                     │  • + valor_esperado              │    │
│                                     └──────────────────────────────────┘    │
│                                                    │                        │
│                                               SFTP │                        │
│                                                    ▼                        │
│                                     ┌──────────────────────────────────┐    │
│                                     │         VOICEBOT                 │    │
│                                     │     (Piloto Existente)           │    │
│                                     │                                  │    │
│                                     │  • Lee CTI enriquecido           │    │
│                                     │  • Prioriza por orden_llamada    │    │
│                                     │  • Respeta reglas campaign       │    │
│                                     │  • Aplica flujo según segmento   │    │
│                                     └──────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Campos Nuevos en CTI Enriquecido
| Campo Nuevo | Tipo | Descripción |
|-------------|------|-------------|
| `prob_pago_30d` | float | Probabilidad de pago 0-1 |
| `prob_aceptacion_campana` | float | Probabilidad de aceptar campaña 0-1 |
| `mejor_mecanismo_sugerido` | string | Mecanismo con mayor prob. éxito |
| `segmento_ml` | string | A, B, C, D |
| `orden_llamada` | int | Prioridad de llamada 1-N |
| `valor_esperado` | float | prob_pago × Saldo en mora |
| `gac_proyectado` | float | GAC calculado a fecha pago |
| `valor_total_proyectado` | float | PAGO MINIMO + GAC |
| `puede_novacion` | bool | Cumple tiempo entre mecanismos |
| `puede_pago_mora` | bool | Cumple tiempo entre mecanismos |
| `campana_requiere_pago` | bool | Parseado de POPUP_CAMP |
| `descuento_intereses` | float | % descuento de la campaña |

---

## 8. Próximos Pasos

### 8.1 Datos Necesarios para Entrenar Modelos
| Dato | Descripción | Para qué |
|------|-------------|----------|
| **Histórico de gestiones** | Resultados de llamadas pasadas | Target: pagó/no pagó |
| **Histórico de campañas** | Aceptación de mecanismos | Target: aceptó/rechazó |
| **Datos de contactabilidad** | Horarios de contacto exitoso | Modelo mejor hora |
| **Resultados por Voicebot vs Humano** | Comparativo de canales | Modelo receptividad |

### 8.2 Entregables Inmediatos Posibles
1. ✅ Parseador de POPUP_CAMP → Estructura de datos
2. ✅ Calculador de GAC según tabla
3. ✅ Validador de tiempo entre mecanismos
4. ✅ Script de enriquecimiento básico del CTI
5. ✅ Dashboard de análisis del CTI

---

## 9. Conclusión

Los insumos proporcionados son **excelentes** para implementar la capa de inteligencia:

✅ **CTI bien estructurado** - 57 campos con toda la información necesaria
✅ **Campañas documentadas** - 24 tipos con sus parámetros claros
✅ **Reglas de negocio claras** - GAC, tiempos, mecanismos bien definidos
✅ **Campo `campaign` como pivote** - Define el flujo principal

**Siguiente paso recomendado**: Obtener histórico de resultados para entrenar los modelos predictivos.
