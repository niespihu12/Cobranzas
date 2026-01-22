# Arquitectura de Producto: Capa de Inteligencia para Voicebot de Cobranzas
## Banco de Bogotá

---

## 1. Visión General de la Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                        ARQUITECTURA DE ALTO NIVEL                                   │
│                   Inteligencia para Voicebot de Cobranzas                          │
│                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   FUENTES   │    │   CAPA DE       │    │  MOTOR DE   │    │   CANALES DE    │  │
│  │   DE DATOS  │───▶│   INTELIGENCIA  │───▶│  DECISIÓN   │───▶│   EJECUCIÓN     │  │
│  │             │    │   (ML/AI)       │    │             │    │                 │  │
│  └─────────────┘    └─────────────────┘    └─────────────┘    └─────────────────┘  │
│        │                    │                    │                    │            │
│        │                    │                    │                    │            │
│        ▼                    ▼                    ▼                    ▼            │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                        CAPA DE OBSERVABILIDAD                               │  │
│  │              (Monitoreo, Logs, Métricas, Feedback Loop)                     │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Arquitectura Detallada por Capas

### 2.1 Capa de Datos (Data Layer)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CAPA DE DATOS                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  FUENTES INTERNAS                          FUENTES EXTERNAS                         │
│  ─────────────────                         ─────────────────                         │
│                                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  CORE BANCARIO   │  │  ARCHIVO CTI     │  │  CENTRALES DE    │                   │
│  │                  │  │  (Banco Bogotá)  │  │  RIESGO          │                   │
│  │  • Saldos        │  │                  │  │                  │                   │
│  │  • Productos     │  │  • Cédula        │  │  • DataCrédito   │                   │
│  │  • Movimientos   │  │  • Producto      │  │  • TransUnion    │                   │
│  │  • Pagos         │  │  • Días mora     │  │  • CIFIN         │                   │
│  │  • Clientes      │  │  • Valor pagar   │  │                  │                   │
│  │                  │  │  • Campaña       │  │  • Score         │                   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                     │                     │                             │
│           └─────────────────────┼─────────────────────┘                             │
│                                 ▼                                                   │
│                    ┌────────────────────────┐                                       │
│                    │     DATA LAKE /        │                                       │
│                    │     FEATURE STORE      │                                       │
│                    │                        │                                       │
│                    │  • Raw Data Zone       │                                       │
│                    │  • Processed Zone      │                                       │
│                    │  • Feature Store       │                                       │
│                    │  • Model Registry      │                                       │
│                    └────────────────────────┘                                       │
│                                                                                     │
│  TECNOLOGÍAS SUGERIDAS:                                                            │
│  • Azure Data Lake / AWS S3 / GCP BigQuery                                         │
│  • Apache Spark para procesamiento                                                 │
│  • MLflow para Feature Store y Model Registry                                      │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Capa de Inteligencia (ML/AI Layer)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE INTELIGENCIA (ML)                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FEATURE ENGINEERING                                  │   │
│  │                                                                              │   │
│  │   Datos Crudos ──▶ Transformación ──▶ Agregación ──▶ Features Finales       │   │
│  │                                                                              │   │
│  │   • 400+ variables calculadas por cliente                                   │   │
│  │   • Ventanas temporales: 7d, 30d, 90d, 12m                                  │   │
│  │   • Ratios, tendencias, patrones                                            │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                          │
│                                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                          MODELOS XGBOOST                                     │   │
│  ├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤   │
│  │                 │                 │                 │                       │   │
│  │  MODELO 1       │  MODELO 2       │  MODELO 3       │  MODELO 4             │   │
│  │  ───────────    │  ───────────    │  ───────────    │  ───────────          │   │
│  │                 │                 │                 │                       │   │
│  │  Probabilidad   │  Probabilidad   │  Mejor Hora     │  Receptividad         │   │
│  │  de Pago        │  Contacto       │  de Contacto    │  al Voicebot          │   │
│  │                 │                 │                 │                       │   │
│  │  Input:         │  Input:         │  Input:         │  Input:               │   │
│  │  • Hist. pagos  │  • Teléfonos    │  • Patrones     │  • Edad               │   │
│  │  • Días mora    │  • Intentos     │  • Ocupación    │  • Digital            │   │
│  │  • Capacidad    │  • Horarios     │  • Historial    │  • Hist. bot          │   │
│  │                 │                 │                 │                       │   │
│  │  Output:        │  Output:        │  Output:        │  Output:              │   │
│  │  prob [0-1]     │  prob [0-1]     │  hora [0-3]     │  prob [0-1]           │   │
│  │                 │                 │                 │                       │   │
│  └─────────────────┴─────────────────┴─────────────────┴───────────────────────┘   │
│                                         │                                          │
│                                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                     MODELO DE SEGMENTACIÓN                                   │   │
│  │                                                                              │   │
│  │   Combina outputs de modelos para segmentar:                                │   │
│  │                                                                              │   │
│  │   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐   │   │
│  │   │  SEGMENTO A   │ │  SEGMENTO B   │ │  SEGMENTO C   │ │  SEGMENTO D   │   │   │
│  │   │  ───────────  │ │  ───────────  │ │  ───────────  │ │  ───────────  │   │   │
│  │   │  VOICEBOT     │ │  VOICEBOT +   │ │  DERIVAR A    │ │  NO GESTIONAR │   │   │
│  │   │  PRIORITARIO  │ │  SEGUIMIENTO  │ │  HUMANO       │ │  HOY          │   │   │
│  │   │               │ │               │ │               │ │               │   │   │
│  │   │  prob_pago≥0.5│ │  prob_pago≥0.3│ │  receptiv<0.4 │ │  prob_pago<0.1│   │   │
│  │   │  recept≥0.6   │ │  recept≥0.4   │ │  monto>$10M   │ │  contacto<0.2 │   │   │
│  │   └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  TECNOLOGÍAS:                                                                      │
│  • XGBoost / LightGBM                                                              │
│  • Scikit-learn para pipelines                                                     │
│  • MLflow para tracking y versionamiento                                           │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Capa de Decisión (Decision Engine)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           MOTOR DE DECISIÓN                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      ORQUESTADOR DE REGLAS                                   │   │
│  │                                                                              │   │
│  │   Predicciones ML ──▶ Reglas de Negocio ──▶ Decisión Final                  │   │
│  │                                                                              │   │
│  │   ┌────────────────────────────────────────────────────────────────────┐    │   │
│  │   │  REGLAS DE NEGOCIO (Configurables por el Banco)                    │    │   │
│  │   │                                                                     │    │   │
│  │   │  • Umbrales de segmentación                                        │    │   │
│  │   │  • Priorización cabeza de mora                                     │    │   │
│  │   │  • Horarios permitidos (Ley 2300)                                  │    │   │
│  │   │  • Frecuencia máxima de contacto                                   │    │   │
│  │   │  • Exclusiones y restricciones                                     │    │   │
│  │   │  • Campañas especiales (override)                                  │    │   │
│  │   └────────────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                          │
│                                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      GENERADOR DE CTI ENRIQUECIDO                            │   │
│  │                                                                              │   │
│  │   CTI Original + Scores ML + Personalización = CTI Inteligente              │   │
│  │                                                                              │   │
│  │   ┌──────────────────────────────────────────────────────────────────────┐  │   │
│  │   │  CAMPOS ORIGINALES    │  CAMPOS ML           │  PERSONALIZACIÓN      │  │   │
│  │   │  ──────────────────   │  ───────────         │  ────────────────     │  │   │
│  │   │  • CEDULA             │  • prob_pago_30d     │  • tono_sugerido      │  │   │
│  │   │  • TIPO_PRODUCTO      │  • prob_contestar    │  • mecanismos_orden   │  │   │
│  │   │  • DIAS_MORA          │  • mejor_hora        │  • argumentos_clave   │  │   │
│  │   │  • VALOR_PAGAR        │  • receptividad_bot  │  • velocidad_habla    │  │   │
│  │   │  • CAMPAÑA_ESPECIAL   │  • valor_esperado    │  • enfasis_mensaje    │  │   │
│  │   │  • POPUP_CAMP         │  • score_prioridad   │  • max_reintentos     │  │   │
│  │   │                       │  • segmento          │                       │  │   │
│  │   │                       │  • orden_llamada     │                       │  │   │
│  │   └──────────────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  TECNOLOGÍAS:                                                                      │
│  • Python / FastAPI para servicios                                                 │
│  • Redis para caché de decisiones                                                  │
│  • PostgreSQL para reglas configurables                                            │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Capa de Ejecución (Execution Layer)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE EJECUCIÓN                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│                          CTI INTELIGENTE                                            │
│                               │                                                     │
│           ┌───────────────────┼───────────────────┐                                 │
│           ▼                   ▼                   ▼                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                       │
│  │   SEGMENTO A    │ │   SEGMENTO B    │ │   SEGMENTO C    │                       │
│  │   SEGMENTO B    │ │   (Seguimiento) │ │   (Humano)      │                       │
│  │   (Voicebot)    │ │                 │ │                 │                       │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘                       │
│           │                   │                   │                                 │
│           ▼                   ▼                   ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │   │
│  │  │                 │  │                 │  │                 │              │   │
│  │  │    VOICEBOT     │  │   VOICEBOT +    │  │   CALL CENTER   │              │   │
│  │  │    (Piloto)     │  │   AGENTE IA     │  │   HUMANO        │              │   │
│  │  │                 │  │   Seguimiento   │  │                 │              │   │
│  │  │  ┌───────────┐  │  │                 │  │  Casos:         │              │   │
│  │  │  │ Flujo del │  │  │  Si no paga en  │  │  • Monto alto   │              │   │
│  │  │  │ Piloto    │  │  │  7 días:        │  │  • Baja recept. │              │   │
│  │  │  │ Banco de  │  │  │  • WhatsApp     │  │  • Complejo     │              │   │
│  │  │  │ Bogotá    │  │  │  • SMS          │  │                 │              │   │
│  │  │  └───────────┘  │  │  • Email        │  │                 │              │   │
│  │  │                 │  │                 │  │                 │              │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘              │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                          │
│                                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      CAPTURA DE RESULTADOS                                   │   │
│  │                                                                              │   │
│  │   • Tipificación por llamada                                                │   │
│  │   • Mecanismo aceptado                                                      │   │
│  │   • Valor comprometido                                                      │   │
│  │   • Transcripción y audio                                                   │   │
│  │   • Timestamp de eventos                                                    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.5 Capa de Observabilidad (Monitoring & Analytics)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        CAPA DE OBSERVABILIDAD                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         DASHBOARD OPERATIVO                                  │   │
│  │                                                                              │   │
│  │   ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌──────────────┐ │   │
│  │   │ Contactabilidad│ │   Conversión   │ │   Cumplimiento │ │    Valor     │ │   │
│  │   │     68.5%      │ │     23.4%      │ │      100%      │ │  $2.3B COP   │ │   │
│  │   │   ▲ +5.2%      │ │   ▲ +8.1%      │ │   ✓ Ley 2300   │ │  comprometido│ │   │
│  │   └────────────────┘ └────────────────┘ └────────────────┘ └──────────────┘ │   │
│  │                                                                              │   │
│  │   ┌──────────────────────────────────────────────────────────────────────┐  │   │
│  │   │  MÉTRICAS EN TIEMPO REAL                                             │  │   │
│  │   │  ═══════════════════════                                             │  │   │
│  │   │                                                                       │  │   │
│  │   │  • Llamadas en curso: 45                                             │  │   │
│  │   │  • Llamadas hoy: 3,456 / 5,000 (meta)                               │  │   │
│  │   │  • Promesas obtenidas: 234                                           │  │   │
│  │   │  • Tasa éxito por hora: [gráfico]                                   │  │   │
│  │   └──────────────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         DASHBOARD ANALÍTICO                                  │   │
│  │                                                                              │   │
│  │   ┌──────────────────────────────────────────────────────────────────────┐  │   │
│  │   │  VALIDACIÓN DE MODELOS ML                                            │  │   │
│  │   │                                                                       │  │   │
│  │   │  Modelo              AUC      Precisión    Lift Top Decil            │  │   │
│  │   │  ────────────────    ─────    ─────────    ──────────────            │  │   │
│  │   │  Prob. Pago          0.847    72.3%        3.2x                      │  │   │
│  │   │  Contactabilidad     0.812    68.9%        2.8x                      │  │   │
│  │   │  Mejor Hora          0.756    64.2%        2.1x                      │  │   │
│  │   │  Receptividad Bot    0.789    66.5%        2.5x                      │  │   │
│  │   └──────────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                              │   │
│  │   ┌──────────────────────────────────────────────────────────────────────┐  │   │
│  │   │  COMPARATIVO POR SEGMENTO                                            │  │   │
│  │   │                                                                       │  │   │
│  │   │  Segmento    Volumen    Contacto    Conversión    Valor Recup.       │  │   │
│  │   │  ─────────   ───────    ────────    ──────────    ────────────       │  │   │
│  │   │  A (Prior)   2,345      78.2%       34.5%         $1.2B              │  │   │
│  │   │  B (Seguim)  1,890      65.4%       21.3%         $650M              │  │   │
│  │   │  C (Humano)  567        72.1%       28.9%         $380M              │  │   │
│  │   │  D (No gest) 1,234      --          --            --                 │  │   │
│  │   └──────────────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                          FEEDBACK LOOP                                       │   │
│  │                                                                              │   │
│  │   Resultados ──▶ Validación ──▶ Reentrenamiento ──▶ Deploy ──▶ Producción   │   │
│  │       │              │                │                │                     │   │
│  │       │              │                │                │                     │   │
│  │       ▼              ▼                ▼                ▼                     │   │
│  │   [Diario]      [Semanal]        [Semanal]        [Quincenal]               │   │
│  │                                                                              │   │
│  │   • Captura     • Compara        • Retrain si     • A/B test                │   │
│  │     resultados    predicho vs      AUC cae         nuevo modelo             │   │
│  │   • Calcula       real             >2%           • Rollback si              │   │
│  │     métricas    • Detecta drift                    empeora                  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  TECNOLOGÍAS:                                                                      │
│  • Grafana / Power BI para dashboards                                              │
│  • Prometheus para métricas                                                        │
│  • ELK Stack para logs                                                             │
│  • MLflow para tracking de modelos                                                 │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA DE INTEGRACIÓN                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│                              BANCO DE BOGOTÁ                                        │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                              │  │
│   │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │  │
│   │  │ Core Bancario│    │   AdminFO    │    │  Centrales   │                   │  │
│   │  │              │    │              │    │  de Riesgo   │                   │  │
│   │  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │  │
│   │         │                   │                   │                            │  │
│   └─────────┼───────────────────┼───────────────────┼────────────────────────────┘  │
│             │                   │                   │                               │
│             │      SFTP / API   │                   │                               │
│             ▼                   ▼                   ▼                               │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                              │  │
│   │                    PLATAFORMA DE INTELIGENCIA                               │  │
│   │                    ══════════════════════════                               │  │
│   │                                                                              │  │
│   │  ┌────────────────────────────────────────────────────────────────────────┐ │  │
│   │  │                         API GATEWAY                                     │ │  │
│   │  │                    (Kong / AWS API Gateway)                            │ │  │
│   │  └────────────────────────────────────────────────────────────────────────┘ │  │
│   │                                    │                                         │  │
│   │         ┌──────────────────────────┼──────────────────────────┐             │  │
│   │         ▼                          ▼                          ▼             │  │
│   │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │  │
│   │  │  SERVICIO       │    │  SERVICIO       │    │  SERVICIO       │          │  │
│   │  │  INGESTA        │    │  SCORING        │    │  REPORTES       │          │  │
│   │  │                 │    │                 │    │                 │          │  │
│   │  │  POST /cti      │    │  POST /score    │    │  GET /dashboard │          │  │
│   │  │  GET /status    │    │  GET /segment   │    │  GET /metrics   │          │  │
│   │  └─────────────────┘    └─────────────────┘    └─────────────────┘          │  │
│   │                                    │                                         │  │
│   │                                    ▼                                         │  │
│   │  ┌────────────────────────────────────────────────────────────────────────┐ │  │
│   │  │                      MESSAGE QUEUE                                      │ │  │
│   │  │                   (RabbitMQ / Kafka)                                   │ │  │
│   │  └────────────────────────────────────────────────────────────────────────┘ │  │
│   │                                                                              │  │
│   └──────────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                                │
│                    SFTP / API      │                                                │
│                                    ▼                                                │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                              │  │
│   │                    PROVEEDOR VOICEBOT (Piloto)                              │  │
│   │                                                                              │  │
│   │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │  │
│   │  │ Recibe CTI   │───▶│  Ejecuta     │───▶│  Envía       │                   │  │
│   │  │ Enriquecido  │    │  Llamadas    │    │  Resultados  │                   │  │
│   │  └──────────────┘    └──────────────┘    └──────────────┘                   │  │
│   │                                                                              │  │
│   └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Flujo de Datos End-to-End

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          FLUJO DE DATOS DIARIO                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  HORA        PROCESO                              RESPONSABLE                       │
│  ────        ───────                              ───────────                       │
│                                                                                     │
│  05:00 AM    ┌─────────────────────────────────┐                                   │
│              │  1. EXTRACCIÓN                   │  Banco de Bogotá                 │
│              │     • Core genera archivo CTI    │  (proceso existente)             │
│              │     • Incluye todos los morosos  │                                   │
│              └──────────────┬──────────────────┘                                   │
│                             │                                                       │
│                             ▼                                                       │
│  05:30 AM    ┌─────────────────────────────────┐                                   │
│              │  2. TRANSFERENCIA                │  Automático                       │
│              │     • SFTP: CTI → Plataforma ML  │  (scheduled job)                  │
│              └──────────────┬──────────────────┘                                   │
│                             │                                                       │
│                             ▼                                                       │
│  06:00 AM    ┌─────────────────────────────────┐                                   │
│              │  3. FEATURE ENGINEERING          │  Plataforma ML                    │
│              │     • Cruza con datos históricos │                                   │
│              │     • Calcula 400+ features      │                                   │
│              │     • Valida calidad de datos    │                                   │
│              └──────────────┬──────────────────┘                                   │
│                             │                                                       │
│                             ▼                                                       │
│  06:30 AM    ┌─────────────────────────────────┐                                   │
│              │  4. SCORING ML                   │  Plataforma ML                    │
│              │     • Ejecuta 4 modelos XGBoost  │                                   │
│              │     • Genera probabilidades      │                                   │
│              │     • Asigna segmentos           │                                   │
│              └──────────────┬──────────────────┘                                   │
│                             │                                                       │
│                             ▼                                                       │
│  07:00 AM    ┌─────────────────────────────────┐                                   │
│              │  5. MOTOR DE DECISIÓN            │  Plataforma ML                    │
│              │     • Aplica reglas de negocio   │                                   │
│              │     • Genera personalización     │                                   │
│              │     • Ordena prioridad llamadas  │                                   │
│              └──────────────┬──────────────────┘                                   │
│                             │                                                       │
│                             ▼                                                       │
│  07:30 AM    ┌─────────────────────────────────┐                                   │
│              │  6. GENERACIÓN CTI ENRIQUECIDO   │  Plataforma ML                    │
│              │     • CTI original + ML scores   │                                   │
│              │     • Formato compatible piloto  │                                   │
│              │     • SFTP → Proveedor Voicebot  │                                   │
│              └──────────────┬──────────────────┘                                   │
│                             │                                                       │
│                             ▼                                                       │
│  08:00 AM    ┌─────────────────────────────────┐                                   │
│  - 20:00 PM  │  7. EJECUCIÓN VOICEBOT           │  Proveedor Voicebot              │
│              │     • Carga CTI enriquecido      │  (piloto existente)              │
│              │     • Ejecuta llamadas priorizadas│                                  │
│              │     • Respeta horarios Ley 2300  │                                   │
│              │     • Captura resultados         │                                   │
│              └──────────────┬──────────────────┘                                   │
│                             │                                                       │
│                             ▼                                                       │
│  21:00 PM    ┌─────────────────────────────────┐                                   │
│              │  8. CIERRE Y RESULTADOS          │  Proveedor Voicebot              │
│              │     • Genera reporte CSV/Excel   │                                   │
│              │     • SFTP → Plataforma ML       │                                   │
│              └──────────────┬──────────────────┘                                   │
│                             │                                                       │
│                             ▼                                                       │
│  22:00 PM    ┌─────────────────────────────────┐                                   │
│              │  9. FEEDBACK LOOP                │  Plataforma ML                    │
│              │     • Procesa resultados         │                                   │
│              │     • Actualiza métricas         │                                   │
│              │     • Valida modelos             │                                   │
│              │     • Dashboard disponible       │                                   │
│              └─────────────────────────────────┘                                   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Stack Tecnológico Recomendado

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         STACK TECNOLÓGICO                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  CAPA                 TECNOLOGÍA                  ALTERNATIVA                       │
│  ────                 ──────────                  ───────────                       │
│                                                                                     │
│  INFRAESTRUCTURA      ┌─────────────────────────────────────────────────────────┐  │
│                       │  Azure (recomendado para bancos en Colombia)             │  │
│                       │  • Azure Kubernetes Service (AKS)                        │  │
│                       │  • Azure Data Lake Storage                               │  │
│                       │  • Azure Machine Learning                                │  │
│                       │                                                          │  │
│                       │  Alternativas: AWS, GCP, On-premise                      │  │
│                       └─────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  DATA                 ┌─────────────────────────────────────────────────────────┐  │
│                       │  • Apache Spark (procesamiento batch)                    │  │
│                       │  • PostgreSQL (datos operacionales)                      │  │
│                       │  • Redis (caché de scores)                               │  │
│                       │  • Delta Lake (almacenamiento)                           │  │
│                       └─────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  ML/AI                ┌─────────────────────────────────────────────────────────┐  │
│                       │  • XGBoost (modelos de clasificación/regresión)          │  │
│                       │  • Scikit-learn (pipelines, preprocessing)               │  │
│                       │  • MLflow (experiment tracking, model registry)          │  │
│                       │  • SHAP (explicabilidad de modelos)                      │  │
│                       └─────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  BACKEND              ┌─────────────────────────────────────────────────────────┐  │
│                       │  • Python 3.11+                                          │  │
│                       │  • FastAPI (APIs REST)                                   │  │
│                       │  • Celery (tareas asíncronas)                            │  │
│                       │  • RabbitMQ / Kafka (mensajería)                         │  │
│                       └─────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  FRONTEND             ┌─────────────────────────────────────────────────────────┐  │
│                       │  • React / Next.js (dashboard web)                       │  │
│                       │  • Grafana (métricas operativas)                         │  │
│                       │  • Power BI (reportes ejecutivos)                        │  │
│                       └─────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  OBSERVABILIDAD       ┌─────────────────────────────────────────────────────────┐  │
│                       │  • Prometheus + Grafana (métricas)                       │  │
│                       │  • ELK Stack (logs)                                      │  │
│                       │  • Jaeger (tracing)                                      │  │
│                       │  • PagerDuty (alertas)                                   │  │
│                       └─────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  SEGURIDAD            ┌─────────────────────────────────────────────────────────┐  │
│                       │  • Azure AD / Okta (autenticación)                       │  │
│                       │  • Vault (secretos)                                      │  │
│                       │  • TLS 1.3 (encriptación en tránsito)                    │  │
│                       │  • AES-256 (encriptación en reposo)                      │  │
│                       └─────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Modelo de Despliegue

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         MODELO DE DESPLIEGUE                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│                              KUBERNETES CLUSTER                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │  ┌─────────────────────────────────────────────────────────────────────┐    │   │
│  │  │                         NAMESPACE: ml-cobranzas                      │    │   │
│  │  │                                                                      │    │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │   │
│  │  │  │ Pod: API    │  │ Pod: Scoring│  │ Pod: Worker │  │ Pod: Dash   │ │    │   │
│  │  │  │ Gateway     │  │ Service     │  │ ETL         │  │ board       │ │    │   │
│  │  │  │             │  │             │  │             │  │             │ │    │   │
│  │  │  │ replicas: 3 │  │ replicas: 2 │  │ replicas: 4 │  │ replicas: 2 │ │    │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │    │   │
│  │  │                                                                      │    │   │
│  │  │  ┌─────────────────────────────────────────────────────────────────┐│    │   │
│  │  │  │                    PERSISTENT VOLUMES                           ││    │   │
│  │  │  │  • Model artifacts  • Feature store  • Logs  • Metrics         ││    │   │
│  │  │  └─────────────────────────────────────────────────────────────────┘│    │   │
│  │  └─────────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                              │   │
│  │  ┌─────────────────────────────────────────────────────────────────────┐    │   │
│  │  │                         NAMESPACE: monitoring                        │    │   │
│  │  │                                                                      │    │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │    │   │
│  │  │  │ Prometheus  │  │ Grafana     │  │ AlertManager│                  │    │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘                  │    │   │
│  │  └─────────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                              │   │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  SERVICIOS EXTERNOS (Managed)                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  • Azure PostgreSQL     • Azure Redis Cache     • Azure Blob Storage        │   │
│  │  • Azure Key Vault      • Azure Monitor         • Azure AD                  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Seguridad y Compliance

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        SEGURIDAD Y COMPLIANCE                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  DATOS SENSIBLES MANEJADOS:                                                        │
│  ─────────────────────────                                                         │
│  • Cédulas de ciudadanía (PII)                                                     │
│  • Información financiera (deudas, pagos)                                          │
│  • Teléfonos de contacto                                                           │
│  • Historial crediticio                                                            │
│                                                                                     │
│  CONTROLES IMPLEMENTADOS:                                                          │
│  ────────────────────────                                                          │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  DATOS EN REPOSO                                                            │   │
│  │  • Encriptación AES-256 en todas las bases de datos                         │   │
│  │  • Enmascaramiento de PII en ambientes no productivos                       │   │
│  │  • Segregación de datos por ambiente (dev/staging/prod)                     │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  DATOS EN TRÁNSITO                                                          │   │
│  │  • TLS 1.3 para todas las comunicaciones                                    │   │
│  │  • VPN site-to-site con el Banco de Bogotá                                  │   │
│  │  • Certificados gestionados por Azure Key Vault                             │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  ACCESO                                                                     │   │
│  │  • Autenticación multi-factor (MFA)                                         │   │
│  │  • RBAC (Role-Based Access Control)                                         │   │
│  │  • Principio de mínimo privilegio                                           │   │
│  │  • Auditoría de accesos                                                     │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  COMPLIANCE                                                                 │   │
│  │  • Ley 1581 de 2012 (Habeas Data Colombia)                                  │   │
│  │  • Ley 2300 de 2023 (Cobranza respetuosa)                                   │   │
│  │  • Circular 007 de 2018 SFC (Ciberseguridad)                                │   │
│  │  • SOC 2 Type II (en proceso)                                               │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Estimación de Recursos

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        ESTIMACIÓN DE RECURSOS                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  INFRAESTRUCTURA CLOUD (Azure - estimado mensual)                                  │
│  ───────────────────────────────────────────────                                   │
│                                                                                     │
│  Recurso                          Especificación           Costo USD/mes           │
│  ────────                         ──────────────           ──────────────          │
│  AKS Cluster                      3 nodos D4s v3           $450                    │
│  Azure PostgreSQL                 Gen5, 4 vCores           $300                    │
│  Azure Redis Cache                Premium P1               $200                    │
│  Azure Blob Storage               100 GB                   $25                     │
│  Azure ML Workspace               Standard                 $150                    │
│  Azure Monitor                    Logs + Metrics           $100                    │
│  Networking (VPN, etc.)           Standard                 $150                    │
│  ─────────────────────────────────────────────────────────────────────────         │
│  TOTAL INFRAESTRUCTURA                                     ~$1,375/mes             │
│                                                            ~$5.5M COP/mes          │
│                                                                                     │
│  EQUIPO HUMANO (estimado para implementación)                                      │
│  ────────────────────────────────────────────                                      │
│                                                                                     │
│  Rol                              Dedicación        Duración                        │
│  ───                              ──────────        ────────                        │
│  ML Engineer (Senior)             100%              4 meses                         │
│  Data Engineer                    100%              3 meses                         │
│  Backend Developer                50%               3 meses                         │
│  DevOps Engineer                  50%               2 meses                         │
│  Project Manager                  25%               4 meses                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```
