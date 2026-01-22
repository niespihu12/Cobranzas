#!/usr/bin/env python3
"""
⚠️ ========================================================================
⚠️  MODELO ENTRENADO CON DATOS SIMULADOS - NO USAR EN PRODUCCIÓN
⚠️ ========================================================================

Entrenador de Modelo XGBoost para Predicción de Pago
Voicebot de Cobranzas - Banco de Bogotá

Este script:
1. Carga el histórico simulado de gestiones
2. Prepara features y target
3. Entrena un modelo XGBoost
4. Evalúa métricas (AUC, precisión, recall)
5. Guarda el modelo entrenado

Autor: Equipo de Inteligencia Voicebot
Fecha: Enero 2026
"""

import pandas as pd
import numpy as np
import pickle
import os
import sys
from datetime import datetime

# Verificar dependencias
try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (
        roc_auc_score, accuracy_score, precision_score, 
        recall_score, f1_score, confusion_matrix, classification_report
    )
    from sklearn.preprocessing import LabelEncoder
except ImportError as e:
    print(f"❌ ERROR: Falta instalar dependencias: {e}")
    print("   Ejecuta: pip install xgboost scikit-learn --break-system-packages")
    sys.exit(1)

# Seed para reproducibilidad
np.random.seed(42)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

FEATURES = [
    'dias_mora_al_momento',
    'saldo_mora_al_momento',
    'tenia_campana',
    'requeria_pago',
    'descuento_ofrecido',
    'intento_numero',
    'hora_num',
    'es_voicebot',
    'producto_encoded'
]

TARGET = 'pago_realizado'

# Parámetros XGBoost
XGBOOST_PARAMS = {
    'objective': 'binary:logistic',
    'eval_metric': 'auc',
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42,
    'use_label_encoder': False
}

# ============================================================================
# FUNCIONES
# ============================================================================

def preparar_features(df):
    """Prepara las features para el modelo"""
    
    df_prep = df.copy()
    
    # Convertir hora a número
    df_prep['hora_num'] = df_prep['hora_gestion'].apply(
        lambda x: int(str(x).split(':')[0]) if pd.notna(x) else 12
    )
    
    # Convertir canal a binario
    df_prep['es_voicebot'] = (df_prep['canal'] == 'Voicebot').astype(int)
    
    # Encodear producto
    le_producto = LabelEncoder()
    df_prep['producto_encoded'] = le_producto.fit_transform(
        df_prep['producto'].fillna('DESCONOCIDO').astype(str)
    )
    
    # Convertir booleanos a int
    df_prep['tenia_campana'] = df_prep['tenia_campana'].astype(int)
    df_prep['requeria_pago'] = df_prep['requeria_pago'].fillna(True).astype(int)
    df_prep['pago_realizado'] = df_prep['pago_realizado'].astype(int)
    
    # Rellenar nulos
    df_prep['descuento_ofrecido'] = df_prep['descuento_ofrecido'].fillna(0)
    df_prep['saldo_mora_al_momento'] = df_prep['saldo_mora_al_momento'].fillna(0)
    df_prep['dias_mora_al_momento'] = df_prep['dias_mora_al_momento'].fillna(30)
    df_prep['intento_numero'] = df_prep['intento_numero'].fillna(1)
    
    return df_prep, le_producto


def entrenar_modelo(X_train, y_train, X_test, y_test):
    """Entrena el modelo XGBoost"""
    
    print("\n🤖 Entrenando modelo XGBoost...")
    
    modelo = xgb.XGBClassifier(**XGBOOST_PARAMS)
    
    modelo.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    return modelo


def evaluar_modelo(modelo, X_test, y_test):
    """Evalúa el modelo y retorna métricas"""
    
    # Predicciones
    y_pred = modelo.predict(X_test)
    y_prob = modelo.predict_proba(X_test)[:, 1]
    
    # Métricas
    metricas = {
        'auc_roc': roc_auc_score(y_test, y_prob),
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0)
    }
    
    # Matriz de confusión
    cm = confusion_matrix(y_test, y_pred)
    
    return metricas, cm, y_pred, y_prob


def mostrar_importancia_features(modelo, feature_names):
    """Muestra la importancia de cada feature"""
    
    importancias = modelo.feature_importances_
    indices = np.argsort(importancias)[::-1]
    
    print("\n📊 IMPORTANCIA DE VARIABLES:")
    print("-" * 50)
    for i, idx in enumerate(indices):
        barra = "█" * int(importancias[idx] * 30)
        print(f"   {i+1}. {feature_names[idx]:<25} {importancias[idx]:.3f} {barra}")


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    
    print("=" * 70)
    print("⚠️  ENTRENAMIENTO XGBOOST - DATOS SIMULADOS")
    print("=" * 70)
    
    # Rutas
    if len(sys.argv) > 1:
        HISTORICO_PATH = sys.argv[1]
    else:
        HISTORICO_PATH = '/mnt/user-data/outputs/historico_gestiones_SIMULADO.xlsx'
    
    OUTPUT_DIR = '/mnt/user-data/outputs'
    MODELO_PATH = f'{OUTPUT_DIR}/modelo_xgboost_SIMULADO.pkl'
    METRICAS_PATH = f'{OUTPUT_DIR}/metricas_modelo_SIMULADO.txt'
    
    print(f"\n📂 Histórico: {HISTORICO_PATH}")
    print(f"📂 Modelo salida: {MODELO_PATH}")
    
    # =========================================================================
    # PASO 1: Cargar datos
    # =========================================================================
    print("\n" + "=" * 50)
    print("PASO 1: CARGAR DATOS")
    print("=" * 50)
    
    if not os.path.exists(HISTORICO_PATH):
        print(f"❌ ERROR: No se encontró el histórico en {HISTORICO_PATH}")
        sys.exit(1)
    
    df = pd.read_excel(HISTORICO_PATH)
    print(f"✅ Cargados {len(df):,} registros")
    print(f"   → Pagaron: {df['pago_realizado'].sum():,} ({df['pago_realizado'].mean()*100:.1f}%)")
    print(f"   → No pagaron: {(~df['pago_realizado']).sum():,} ({(~df['pago_realizado']).mean()*100:.1f}%)")
    
    # =========================================================================
    # PASO 2: Preparar features
    # =========================================================================
    print("\n" + "=" * 50)
    print("PASO 2: PREPARAR FEATURES")
    print("=" * 50)
    
    df_prep, le_producto = preparar_features(df)
    
    X = df_prep[FEATURES]
    y = df_prep[TARGET]
    
    print(f"✅ Features preparadas: {len(FEATURES)} variables")
    for f in FEATURES:
        print(f"   → {f}")
    
    # =========================================================================
    # PASO 3: Dividir train/test
    # =========================================================================
    print("\n" + "=" * 50)
    print("PASO 3: DIVIDIR TRAIN/TEST")
    print("=" * 50)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"✅ Datos divididos:")
    print(f"   → Train: {len(X_train):,} registros ({len(X_train)/len(X)*100:.0f}%)")
    print(f"   → Test: {len(X_test):,} registros ({len(X_test)/len(X)*100:.0f}%)")
    
    # =========================================================================
    # PASO 4: Entrenar modelo
    # =========================================================================
    print("\n" + "=" * 50)
    print("PASO 4: ENTRENAR MODELO")
    print("=" * 50)
    
    modelo = entrenar_modelo(X_train, y_train, X_test, y_test)
    print("✅ Modelo entrenado exitosamente")
    
    # =========================================================================
    # PASO 5: Evaluar modelo
    # =========================================================================
    print("\n" + "=" * 50)
    print("PASO 5: EVALUAR MODELO")
    print("=" * 50)
    
    metricas, cm, y_pred, y_prob = evaluar_modelo(modelo, X_test, y_test)
    
    print("\n📈 MÉTRICAS DEL MODELO:")
    print("-" * 50)
    print(f"   AUC-ROC:    {metricas['auc_roc']:.4f}  ← Capacidad de discriminación")
    print(f"   Accuracy:   {metricas['accuracy']:.4f}  ← Precisión general")
    print(f"   Precision:  {metricas['precision']:.4f}  ← De los que predijo pago, cuántos pagaron")
    print(f"   Recall:     {metricas['recall']:.4f}  ← De los que pagaron, cuántos detectó")
    print(f"   F1-Score:   {metricas['f1']:.4f}  ← Balance precision/recall")
    
    print("\n📊 MATRIZ DE CONFUSIÓN:")
    print("-" * 50)
    print(f"                    Predicho")
    print(f"                 No Paga | Paga")
    print(f"   Real No Paga:  {cm[0,0]:5,}  | {cm[0,1]:5,}")
    print(f"   Real Paga:     {cm[1,0]:5,}  | {cm[1,1]:5,}")
    
    # Importancia de features
    mostrar_importancia_features(modelo, FEATURES)
    
    # =========================================================================
    # PASO 6: Guardar modelo
    # =========================================================================
    print("\n" + "=" * 50)
    print("PASO 6: GUARDAR MODELO")
    print("=" * 50)
    
    # Guardar modelo con pickle
    modelo_data = {
        'modelo': modelo,
        'features': FEATURES,
        'label_encoder_producto': le_producto,
        'metricas': metricas,
        'fecha_entrenamiento': datetime.now().isoformat(),
        'advertencia': 'MODELO ENTRENADO CON DATOS SIMULADOS - NO USAR EN PRODUCCIÓN'
    }
    
    with open(MODELO_PATH, 'wb') as f:
        pickle.dump(modelo_data, f)
    
    print(f"✅ Modelo guardado en: {MODELO_PATH}")
    
    # Guardar métricas en texto
    with open(METRICAS_PATH, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("⚠️  MÉTRICAS DEL MODELO - DATOS SIMULADOS\n")
        f.write("=" * 70 + "\n\n")
        f.write("ADVERTENCIA: Este modelo fue entrenado con datos SIMULADOS.\n")
        f.write("NO refleja el comportamiento real de los clientes.\n")
        f.write("NO usar en producción.\n\n")
        f.write(f"Fecha entrenamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Registros de entrenamiento: {len(X_train):,}\n")
        f.write(f"Registros de test: {len(X_test):,}\n\n")
        f.write("MÉTRICAS:\n")
        f.write(f"  AUC-ROC:   {metricas['auc_roc']:.4f}\n")
        f.write(f"  Accuracy:  {metricas['accuracy']:.4f}\n")
        f.write(f"  Precision: {metricas['precision']:.4f}\n")
        f.write(f"  Recall:    {metricas['recall']:.4f}\n")
        f.write(f"  F1-Score:  {metricas['f1']:.4f}\n\n")
        f.write("IMPORTANCIA DE VARIABLES:\n")
        importancias = modelo.feature_importances_
        indices = np.argsort(importancias)[::-1]
        for i, idx in enumerate(indices):
            f.write(f"  {i+1}. {FEATURES[idx]}: {importancias[idx]:.4f}\n")
    
    print(f"✅ Métricas guardadas en: {METRICAS_PATH}")
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print(f"\n📊 Resumen:")
    print(f"   → AUC-ROC: {metricas['auc_roc']:.2%} (capacidad predictiva)")
    print(f"   → El modelo puede distinguir entre pagadores y no pagadores")
    print(f"\n⚠️  RECUERDA: Modelo entrenado con datos SIMULADOS")
    print("=" * 70)
