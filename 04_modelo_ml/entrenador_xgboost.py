"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  ENTRENADOR DE MODELO XGBOOST - SOLO PARA DEMOSTRACIÓN  ⚠️               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Este script entrena un modelo XGBoost usando datos SIMULADOS.                ║
║                                                                               ║
║  • El modelo NO refleja el comportamiento real de clientes                    ║
║  • Las predicciones son para DEMOSTRACIÓN técnica únicamente                  ║
║  • NO usar en producción sin datos históricos reales                          ║
║                                                                               ║
║  Autor: Equipo de Inteligencia Voicebot                                       ║
║  Fecha: Enero 2026                                                            ║
║  Versión: 1.0                                                                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importar librerías de ML
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve
)
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import pickle

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

CONFIG = {
    'test_size': 0.20,          # 20% para test
    'random_state': 42,         # Reproducibilidad
    'modelo_output': '../02_datos/salida/modelo_xgboost_SIMULADO.pkl',
    'metricas_output': '../02_datos/salida/metricas_modelo_SIMULADO.txt',
}

# Parámetros de XGBoost
XGBOOST_PARAMS = {
    'n_estimators': 100,        # Número de árboles
    'max_depth': 5,             # Profundidad máxima de cada árbol
    'learning_rate': 0.1,       # Tasa de aprendizaje
    'subsample': 0.8,           # Porcentaje de datos por árbol
    'colsample_bytree': 0.8,    # Porcentaje de features por árbol
    'random_state': 42,
    'eval_metric': 'auc',
    'use_label_encoder': False,
}

# ============================================================================
# FUNCIONES
# ============================================================================

def preparar_datos(df):
    """
    Prepara los datos para entrenamiento.
    
    - Selecciona features relevantes
    - Convierte categóricas a numéricas
    - Maneja valores nulos
    """
    print("\n1️⃣ Preparando datos...")
    
    # Features a usar
    features = [
        'dias_mora_al_momento',
        'saldo_mora_al_momento',
        'tenia_campana',
        'requeria_pago',
        'descuento_ofrecido',
        'canal',
        'hora_gestion',
        'intento_numero',
        'producto',
    ]
    
    # Target
    target = 'pago_realizado'
    
    # Copiar solo las columnas necesarias
    df_ml = df[features + [target]].copy()
    
    # Convertir hora a número (extraer solo la hora)
    df_ml['hora_num'] = df_ml['hora_gestion'].apply(
        lambda x: int(str(x).split(':')[0]) if pd.notna(x) else 12
    )
    df_ml = df_ml.drop('hora_gestion', axis=1)
    
    # Convertir booleanos a int
    df_ml['tenia_campana'] = df_ml['tenia_campana'].astype(int)
    df_ml['requeria_pago'] = df_ml['requeria_pago'].astype(int)
    df_ml['pago_realizado'] = df_ml['pago_realizado'].astype(int)
    
    # Convertir categóricas con LabelEncoder
    le_canal = LabelEncoder()
    df_ml['canal_encoded'] = le_canal.fit_transform(df_ml['canal'].fillna('Desconocido'))
    
    le_producto = LabelEncoder()
    df_ml['producto_encoded'] = le_producto.fit_transform(df_ml['producto'].fillna('Desconocido'))
    
    # Manejar nulos en descuento
    df_ml['descuento_ofrecido'] = df_ml['descuento_ofrecido'].fillna(0)
    
    # Seleccionar features finales
    features_finales = [
        'dias_mora_al_momento',
        'saldo_mora_al_momento',
        'tenia_campana',
        'requeria_pago',
        'descuento_ofrecido',
        'canal_encoded',
        'hora_num',
        'intento_numero',
        'producto_encoded',
    ]
    
    X = df_ml[features_finales]
    y = df_ml[target]
    
    print(f"   ✓ Features: {len(features_finales)}")
    print(f"   ✓ Registros: {len(X):,}")
    print(f"   ✓ Target 'pago_realizado': {y.sum():,} positivos ({100*y.mean():.1f}%)")
    
    # Guardar encoders para uso posterior
    encoders = {
        'canal': le_canal,
        'producto': le_producto,
        'features': features_finales
    }
    
    return X, y, encoders


def entrenar_modelo(X_train, y_train, X_test, y_test):
    """
    Entrena el modelo XGBoost.
    """
    print("\n2️⃣ Entrenando modelo XGBoost...")
    print(f"   • Árboles: {XGBOOST_PARAMS['n_estimators']}")
    print(f"   • Profundidad máxima: {XGBOOST_PARAMS['max_depth']}")
    print(f"   • Learning rate: {XGBOOST_PARAMS['learning_rate']}")
    
    # Crear modelo
    modelo = xgb.XGBClassifier(**XGBOOST_PARAMS)
    
    # Entrenar
    modelo.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    print("   ✓ Modelo entrenado")
    
    return modelo


def evaluar_modelo(modelo, X_test, y_test):
    """
    Evalúa el modelo y genera métricas.
    """
    print("\n3️⃣ Evaluando modelo...")
    
    # Predicciones
    y_pred = modelo.predict(X_test)
    y_pred_proba = modelo.predict_proba(X_test)[:, 1]
    
    # Métricas
    metricas = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'auc_roc': roc_auc_score(y_test, y_pred_proba),
    }
    
    # Matriz de confusión
    cm = confusion_matrix(y_test, y_pred)
    
    # Reporte de clasificación
    reporte = classification_report(y_test, y_pred, target_names=['No Paga', 'Paga'])
    
    return metricas, cm, reporte, y_pred_proba


def obtener_importancia_variables(modelo, features):
    """
    Obtiene la importancia de cada variable.
    """
    importancia = pd.DataFrame({
        'feature': features,
        'importancia': modelo.feature_importances_
    }).sort_values('importancia', ascending=False)
    
    return importancia


def generar_reporte(metricas, cm, reporte, importancia, X_train, X_test):
    """
    Genera un reporte completo en texto.
    """
    linea = "=" * 70
    
    texto = f"""
{linea}
⚠️  REPORTE DE MODELO XGBOOST - DATOS SIMULADOS - SOLO DEMOSTRACIÓN  ⚠️
{linea}

Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{linea}
1. RESUMEN DEL DATASET
{linea}

• Registros de entrenamiento: {len(X_train):,}
• Registros de prueba: {len(X_test):,}
• Total: {len(X_train) + len(X_test):,}
• División: 80% entrenamiento / 20% prueba

{linea}
2. MÉTRICAS DE RENDIMIENTO
{linea}

╔════════════════════╦═══════════════╗
║      Métrica       ║     Valor     ║
╠════════════════════╬═══════════════╣
║ AUC-ROC            ║    {metricas['auc_roc']:.4f}      ║
║ Accuracy           ║    {metricas['accuracy']:.4f}      ║
║ Precisión          ║    {metricas['precision']:.4f}      ║
║ Recall             ║    {metricas['recall']:.4f}      ║
║ F1-Score           ║    {metricas['f1']:.4f}      ║
╚════════════════════╩═══════════════╝

Interpretación:
• AUC-ROC {metricas['auc_roc']:.2f}: {"Excelente" if metricas['auc_roc'] >= 0.9 else "Muy bueno" if metricas['auc_roc'] >= 0.8 else "Bueno" if metricas['auc_roc'] >= 0.7 else "Regular"} capacidad de discriminación
• Precisión {metricas['precision']:.2f}: De cada 100 que predice como "paga", {int(metricas['precision']*100)} realmente pagan
• Recall {metricas['recall']:.2f}: De cada 100 que realmente pagan, identifica {int(metricas['recall']*100)}

{linea}
3. MATRIZ DE CONFUSIÓN
{linea}

                    Predicción
                 No Paga    Paga
              ┌──────────┬──────────┐
Realidad      │          │          │
  No Paga     │  {cm[0][0]:>6,}  │  {cm[0][1]:>6,}  │
              ├──────────┼──────────┤
  Paga        │  {cm[1][0]:>6,}  │  {cm[1][1]:>6,}  │
              └──────────┴──────────┘

• Verdaderos Negativos (No paga → Predijo No paga): {cm[0][0]:,}
• Falsos Positivos (No paga → Predijo Paga): {cm[0][1]:,}
• Falsos Negativos (Paga → Predijo No paga): {cm[1][0]:,}
• Verdaderos Positivos (Paga → Predijo Paga): {cm[1][1]:,}

{linea}
4. REPORTE DE CLASIFICACIÓN DETALLADO
{linea}

{reporte}

{linea}
5. IMPORTANCIA DE VARIABLES
{linea}

¿Qué factores influyen más en la predicción de pago?

"""
    
    # Agregar importancia de variables con barras visuales
    max_imp = importancia['importancia'].max()
    for _, row in importancia.iterrows():
        barra_len = int(30 * row['importancia'] / max_imp)
        barra = "█" * barra_len
        texto += f"  {row['feature']:<25} {barra} {row['importancia']:.4f} ({100*row['importancia']:.1f}%)\n"
    
    texto += f"""

{linea}
6. PARÁMETROS DEL MODELO
{linea}

• Algoritmo: XGBoost (Gradient Boosting)
• Número de árboles: {XGBOOST_PARAMS['n_estimators']}
• Profundidad máxima: {XGBOOST_PARAMS['max_depth']}
• Learning rate: {XGBOOST_PARAMS['learning_rate']}
• Subsample: {XGBOOST_PARAMS['subsample']}
• Colsample by tree: {XGBOOST_PARAMS['colsample_bytree']}

{linea}
⚠️  ADVERTENCIA IMPORTANTE
{linea}

Este modelo fue entrenado con DATOS SIMULADOS.

• Las métricas NO reflejan el rendimiento real que tendría con datos del banco
• Las probabilidades de pago son FICTICIAS
• La importancia de variables puede ser diferente con datos reales

USAR SOLO PARA:
✅ Demostración técnica
✅ Pruebas de integración
✅ Capacitación del equipo

NO USAR PARA:
❌ Decisiones de negocio reales
❌ Producción
❌ Reportes oficiales

{linea}
"""
    
    return texto


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " ⚠️  ENTRENAMIENTO DE MODELO XGBOOST - DATOS SIMULADOS ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Cargar histórico simulado
    print("\n📂 Cargando histórico simulado...")
    df = pd.read_excel('../02_datos/salida/historico_gestiones_SIMULADO.xlsx')
    print(f"   ✓ {len(df):,} registros cargados")
    
    # Preparar datos
    X, y, encoders = preparar_datos(df)
    
    # Dividir en train/test
    print("\n   Dividiendo datos 80/20...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=CONFIG['test_size'],
        random_state=CONFIG['random_state'],
        stratify=y  # Mantener proporción de clases
    )
    print(f"   ✓ Entrenamiento: {len(X_train):,} registros")
    print(f"   ✓ Prueba: {len(X_test):,} registros")
    
    # Entrenar modelo
    modelo = entrenar_modelo(X_train, y_train, X_test, y_test)
    
    # Evaluar modelo
    metricas, cm, reporte, y_pred_proba = evaluar_modelo(modelo, X_test, y_test)
    
    # Importancia de variables
    print("\n4️⃣ Calculando importancia de variables...")
    importancia = obtener_importancia_variables(modelo, encoders['features'])
    print("   ✓ Importancia calculada")
    
    # Mostrar métricas en consola
    print("\n" + "=" * 70)
    print("📊 MÉTRICAS DEL MODELO")
    print("=" * 70)
    print(f"\n   AUC-ROC:    {metricas['auc_roc']:.4f}")
    print(f"   Accuracy:   {metricas['accuracy']:.4f}")
    print(f"   Precisión:  {metricas['precision']:.4f}")
    print(f"   Recall:     {metricas['recall']:.4f}")
    print(f"   F1-Score:   {metricas['f1']:.4f}")
    
    print("\n📊 IMPORTANCIA DE VARIABLES (Top 5):")
    for i, (_, row) in enumerate(importancia.head().iterrows()):
        print(f"   {i+1}. {row['feature']}: {100*row['importancia']:.1f}%")
    
    # Guardar modelo
    print(f"\n5️⃣ Guardando modelo...")
    modelo_guardado = {
        'modelo': modelo,
        'encoders': encoders,
        'metricas': metricas,
        'importancia': importancia,
        'fecha_entrenamiento': datetime.now().isoformat(),
        'advertencia': 'MODELO ENTRENADO CON DATOS SIMULADOS - SOLO DEMOSTRACIÓN'
    }
    
    with open(CONFIG['modelo_output'], 'wb') as f:
        pickle.dump(modelo_guardado, f)
    print(f"   ✓ Modelo guardado en: {CONFIG['modelo_output']}")
    
    # Generar y guardar reporte
    print(f"\n6️⃣ Generando reporte...")
    reporte_texto = generar_reporte(metricas, cm, reporte, importancia, X_train, X_test)
    
    with open(CONFIG['metricas_output'], 'w') as f:
        f.write(reporte_texto)
    print(f"   ✓ Reporte guardado en: {CONFIG['metricas_output']}")
    
    print("\n" + "=" * 70)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print("\n⚠️  RECUERDA: Este modelo usa datos SIMULADOS, solo para demostración.")
    print("=" * 70)
