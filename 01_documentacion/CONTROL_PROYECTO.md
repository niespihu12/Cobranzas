# CONTROL DEL PROYECTO - Voicebot Cobranzas Banco de Bogotá

**Fecha de creación:** 2026-01-20
**Última actualización:** 2026-01-20

---

## 1. INVENTARIO DE ARCHIVOS

### 1.1 Archivos Fuente (Proporcionados por el banco)
| Archivo | Descripción | Estado |
|---------|-------------|--------|
| `CTI_EJMPLO_VOICEBOT_MULTIPRODUCTO.xlsx` | CTI de ejemplo con 7,504 registros | ✅ Recibido |
| `DEFINICIO_N_-_CAMPAN_AS_ESPECIALES.xlsx` | Catálogo de 24 campañas especiales | ✅ Recibido |
| `ESTRUCTURA_CTI_VOICEBOT_2_0_FINAL.xlsx` | Diccionario de datos (57 campos) | ✅ Recibido |
| `REGLAS_DE_NEGOCIO_-_Flujo_VoiceBot_2_0__1_.pdf` | Reglas de negocio y mecanismos | ✅ Recibido |
| `alcance_pilotoVoicebot_de_Gestio_n_de_Cobranza.docx` | Alcance del piloto | ✅ Recibido |

### 1.2 Archivos Generados (Nuestro trabajo)
| Archivo | Descripción | Estado | Versión |
|---------|-------------|--------|---------|
| `enriquecer_cti.py` | Script de enriquecimiento del CTI | ✅ Funcional | 1.0 |
| `CTI_ENRIQUECIDO.xlsx` | Resultado del enriquecimiento | ✅ Generado | 1.0 |
| `analisis_insumos_banco_bogota.md` | Documentación técnica | ✅ Completo | 1.0 |
| `arquitectura_voicebot_cobranzas.md` | Arquitectura del sistema | ✅ Completo | 1.0 |
| `arquitectura_voicebot_interactiva.html` | Visualización de arquitectura | ✅ Funcional | 1.0 |
| `dashboard_cti_enriquecido.html` | Dashboard de resultados | ✅ Funcional | 1.0 |

---

## 2. ESTADO ACTUAL DE FUNCIONALIDADES

### 2.1 Funcionalidades LISTAS para producción
| Funcionalidad | Archivo | Probado |
|---------------|---------|---------|
| Cálculo de GAC | `enriquecer_cti.py` → `calcular_gac()` | ⏳ Pendiente test |
| Parseo de POPUP_CAMP | `enriquecer_cti.py` → `parsear_popup_camp()` | ⏳ Pendiente test |
| Limpieza de datos numéricos | `enriquecer_cti.py` | ⏳ Pendiente test |

### 2.2 Funcionalidades SIMULADAS (necesitan datos históricos)
| Funcionalidad | Archivo | Notas |
|---------------|---------|-------|
| Probabilidad de pago | `enriquecer_cti.py` → `calcular_prob_pago_simple()` | Reglas inventadas |
| Segmentación A/B/C/D | `enriquecer_cti.py` → `asignar_segmento_basico()` | Reglas inventadas |
| Priorización de llamadas | `enriquecer_cti.py` | Depende de simulados |

### 2.3 Funcionalidades PENDIENTES
| Funcionalidad | Estado | Requiere |
|---------------|--------|----------|
| Validación tiempo entre mecanismos | Parcial | Datos completos de `Fecha Ultima Neg Aplicada` |
| Histórico simulado | No iniciado | Crear con cuidado |
| Modelo XGBoost | No iniciado | Histórico (real o simulado) |

---

## 3. PLAN DE TRABAJO - HISTÓRICO SIMULADO

### Fase 1: Verificación (ACTUAL)
- [ ] Crear tests para funciones existentes
- [ ] Ejecutar tests y confirmar que todo funciona
- [ ] Documentar resultados de tests

### Fase 2: Diseño del histórico simulado
- [ ] Definir estructura de datos del histórico
- [ ] Definir reglas de simulación (documentadas)
- [ ] Revisar con el usuario antes de implementar

### Fase 3: Implementación del histórico simulado
- [ ] Crear script de generación (archivo separado)
- [ ] Generar histórico simulado
- [ ] Verificar integridad de datos generados

### Fase 4: Modelo XGBoost (si procede)
- [ ] Crear script de entrenamiento (archivo separado)
- [ ] Entrenar modelo con datos simulados
- [ ] Generar métricas y reportes
- [ ] Advertencias claras de "SOLO DEMOSTRACIÓN"

---

## 4. REGLAS DE SEGURIDAD

1. **NO modificar** archivos existentes sin backup
2. **NO sobrescribir** archivos fuente del banco
3. **Crear archivos nuevos** para funcionalidades nuevas
4. **Probar antes** de integrar
5. **Documentar** cada cambio

---

## 5. HISTORIAL DE CAMBIOS

| Fecha | Cambio | Archivo Afectado | Resultado |
|-------|--------|------------------|-----------|
| 2026-01-20 | Creación inicial | Todos | ✅ OK |
| | | | |

