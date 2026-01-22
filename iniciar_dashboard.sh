#!/bin/bash
# ============================================================================
# INICIAR DASHBOARD - VOICEBOT COBRANZAS
# ============================================================================

echo "🏦 Iniciando Dashboard Voicebot Cobranzas..."
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar dependencias
echo "📦 Verificando dependencias..."
pip3 install -q streamlit pandas numpy plotly openpyxl

# Iniciar Streamlit
echo ""
echo "🚀 Abriendo dashboard en http://localhost:8501"
echo "   Presiona Ctrl+C para detener"
echo ""

streamlit run dashboard.py --server.headless true --browser.gatherUsageStats false
