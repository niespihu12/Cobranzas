"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  DASHBOARD VOICEBOT COBRANZAS - BANCO DE BOGOTÁ (VERSIÓN AUTO-REFRESH)       ║
║  Sistema de Inteligencia para Gestión de Cobranzas                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Ejecutar:  streamlit run dashboard.py                                        ║
║  Puerto:    http://localhost:8501                                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

MEJORAS EN AUTO-ACTUALIZACIÓN:
✓ Cache reducido a 30 segundos
✓ Refresco automático unificado
✓ Indicador visual de última actualización
✓ Manejo robusto de errores
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Intentar importar requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Intentar importar streamlit-autorefresh
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Voicebot Cobranzas | Banco de Bogotá",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS (mantener los mismos)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0c1222 0%, #1a2744 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1729 0%, #1a2744 100%);
        border-right: 1px solid #2d3a4f;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #10b981 !important;
    }
    
    h1, h2, h3, h4 { color: #f1f5f9 !important; }
    p, span, label, li { color: #cbd5e1 !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: #1e293b;
        border-radius: 8px 8px 0 0;
        color: #94a3b8;
        padding: 12px 24px;
        border: 1px solid #334155;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white !important;
        border-color: #2563eb;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    }
    
    .refresh-indicator {
        background: linear-gradient(135deg, #065f46 0%, #059669 100%);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: white;
        display: inline-block;
        margin: 4px 0;
    }
    
    .error-indicator {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: white;
        display: inline-block;
        margin: 4px 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES DE DATOS (MEJORADAS)
# ============================================================================

# Configuración Google Apps Script
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwjTxqCoL2euA72zP6LFf0segsKw1EOtoe-3K883xcGIqcdyGDOcu1NWHT_cWvjAFqv/exec"

# MEJORA 1: Cache reducido a 30 segundos para actualización frecuente
@st.cache_data(ttl=30, show_spinner=False)
def cargar_datos_sheets(url=APPS_SCRIPT_URL, timestamp=None):
    """
    Carga datos desde Google Apps Script.
    
    Args:
        url: URL del endpoint
        timestamp: Parámetro para forzar recarga (no usado en lógica, solo para cache)
    """
    if not REQUESTS_AVAILABLE:
        st.error("📦 **Módulo requerido**: Instala 'requests' con: pip install requests")
        return None, "Error: requests no disponible"
        
    try:
        # Agregar timeout para evitar esperas infinitas
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                df_procesado = procesar_datos_sheets(df)
                return df_procesado, None
            else:
                return None, "No se encontraron datos en la respuesta"
        else:
            return None, f"Error HTTP {response.status_code}: {response.text[:100]}"
            
    except requests.Timeout:
        return None, "Timeout: El servidor tardó demasiado en responder"
    except requests.ConnectionError:
        return None, "Error de conexión: Verifica tu internet"
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"

def procesar_datos_sheets(df):
    """Procesa y enriquece datos de Google Sheets."""
    # Limpiar y convertir columnas numéricas
    def limpiar_numero(valor):
        if pd.isna(valor) or valor == '':
            return 0
        valor_str = str(valor).replace('$', '').replace(',', '').replace('.', '')
        try:
            return float(valor_str)
        except:
            return 0
    
    # Convertir tipos de datos
    numeric_cols = ['dias mora', 'Saldo en mora', 'Saldo total', 'Capital Total', 
                   'Capital Mora', 'Cuota Mensual Aprox']
    for col in numeric_cols:
        if col in df.columns:
            if col == 'dias mora':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = df[col].apply(limpiar_numero)
    
    # Calcular GAC proyectado
    df['GAC_proyectado'] = calcular_gac(df)
    
    # Detectar mecanismos
    df['mecanismo_detectado'] = df.apply(lambda row: parsear_popup_camp(row.get('POPUP_CAMP', '')), axis=1)
    
    # Simular probabilidad ML
    np.random.seed(42)
    df['probabilidad_pago_SIMULADA'] = np.random.beta(2, 5, len(df))
    
    # Segmentación
    df['segmento_SIMULADO'] = df['probabilidad_pago_SIMULADA'].apply(lambda x: 
        'A' if x >= 0.75 else 'B' if x >= 0.50 else 'C' if x >= 0.25 else 'D')
    
    # Valor esperado
    df['valor_esperado_SIMULADO'] = df['probabilidad_pago_SIMULADA'] * df['Saldo en mora']
    
    # Requiere pago
    df['requiere_pago'] = df['mecanismo_detectado'].apply(lambda x: 'PAGO' in str(x).upper())
    
    return df

def calcular_gac(df):
    """Calcula Gastos de Cobranza según tabla GAC."""
    GAC_TABLE = {
        (1, 10): {'tarifa': 0.00, 'min': 0, 'max': 0},
        (11, 15): {'tarifa': 0.06, 'min': 10000, 'max': 260000},
        (16, 30): {'tarifa': 0.08, 'min': 15000, 'max': 350000},
        (31, 60): {'tarifa': 0.10, 'min': 20000, 'max': 450000},
        (61, 90): {'tarifa': 0.12, 'min': 25000, 'max': 550000},
        (91, 9999): {'tarifa': 0.15, 'min': 30000, 'max': 650000}
    }
    
    gac_values = []
    for _, row in df.iterrows():
        dias = row.get('dias mora', 0)
        saldo = row.get('Saldo en mora', 0)
        
        gac = 0
        for (min_dias, max_dias), config in GAC_TABLE.items():
            if min_dias <= dias <= max_dias:
                gac_calc = saldo * config['tarifa']
                gac = max(config['min'], min(gac_calc, config['max']))
                break
        gac_values.append(gac)
    
    return gac_values

def parsear_popup_camp(popup):
    """Parsea POPUP_CAMP para detectar mecanismo."""
    if pd.isna(popup) or popup == '':
        return 'SIN_MECANISMO'
    
    popup_upper = str(popup).upper()
    
    if 'NOVACION' in popup_upper:
        return 'NOVACION'
    elif 'CONSOLIDACION' in popup_upper:
        return 'CONSOLIDACION'
    elif 'PAGO' in popup_upper:
        return 'ACUERDO_PAGO'
    elif 'DESCUENTO' in popup_upper:
        return 'DESCUENTO'
    else:
        return 'OTRO_MECANISMO'

def calcular_metricas(df):
    """Calcula todas las métricas del dashboard."""
    m = {}
    
    # Básicas
    m['total'] = len(df)
    m['gac_total'] = df['GAC_proyectado'].sum() if 'GAC_proyectado' in df.columns else 0
    m['gac_promedio'] = df['GAC_proyectado'].mean() if 'GAC_proyectado' in df.columns else 0
    
    # Campañas
    if 'campaign' in df.columns:
        camp_true = (df['campaign'] == True) if df['campaign'].dtype == bool else (df['campaign'].astype(str).str.lower() == 'true')
        m['con_campana'] = camp_true.sum()
        m['sin_campana'] = m['total'] - m['con_campana']
        m['pct_campana'] = m['con_campana'] / m['total'] * 100 if m['total'] > 0 else 0
    else:
        m['con_campana'], m['sin_campana'], m['pct_campana'] = 0, m['total'], 0
    
    # Probabilidad
    prob_col = 'probabilidad_pago_ML' if 'probabilidad_pago_ML' in df.columns else 'probabilidad_pago_SIMULADA'
    if prob_col in df.columns:
        m['prob_media'] = df[prob_col].mean() * 100
        m['prob_max'] = df[prob_col].max() * 100
        m['prob_min'] = df[prob_col].min() * 100
    else:
        m['prob_media'], m['prob_max'], m['prob_min'] = 0, 0, 0
    
    # Segmentos
    seg_col = 'segmento_ML' if 'segmento_ML' in df.columns else 'segmento_SIMULADO'
    m['segmentos'] = df[seg_col].value_counts().to_dict() if seg_col in df.columns else {}
    
    # Mecanismos
    m['mecanismos'] = df['mecanismo_detectado'].value_counts().to_dict() if 'mecanismo_detectado' in df.columns else {}
    
    # Productos
    prod_col = 'producto' if 'producto' in df.columns else 'Tipo Producto'
    m['productos'] = df[prod_col].value_counts().to_dict() if prod_col in df.columns else {}
    
    # Mora
    if 'dias mora' in df.columns:
        bins = [0, 10, 30, 60, 90, 9999]
        labels = ['1-10', '11-30', '31-60', '61-90', '>90']
        mora_cat = pd.cut(df['dias mora'], bins=bins, labels=labels)
        m['mora_dist'] = mora_cat.value_counts().to_dict()
        m['mora_promedio'] = df['dias mora'].mean()
    else:
        m['mora_dist'], m['mora_promedio'] = {}, 0
    
    # Requiere pago
    if 'requiere_pago' in df.columns:
        m['req_pago'] = (df['requiere_pago'] == True).sum()
        m['no_req_pago'] = m['total'] - m['req_pago']
    else:
        m['req_pago'], m['no_req_pago'] = 0, 0
    
    # Valor esperado
    val_col = 'valor_esperado_ML' if 'valor_esperado_ML' in df.columns else 'valor_esperado_SIMULADO'
    m['valor_esperado_total'] = df[val_col].sum() if val_col in df.columns else 0
    
    return m

# ============================================================================
# COMPONENTES GRÁFICOS (MANTENER LOS MISMOS)
# ============================================================================

def grafico_barras(datos, titulo, color_scale='Blues', horizontal=True):
    """Gráfico de barras profesional."""
    if not datos:
        return None
    
    df = pd.DataFrame({'cat': list(datos.keys()), 'val': list(datos.values())})
    df = df.sort_values('val', ascending=horizontal)
    
    if horizontal:
        fig = go.Figure(go.Bar(
            x=df['val'], y=df['cat'], orientation='h',
            marker=dict(color=df['val'], colorscale=color_scale),
            text=[f'{v:,.0f}' for v in df['val']],
            textposition='auto', textfont=dict(color='white', size=12)
        ))
    else:
        fig = go.Figure(go.Bar(
            x=df['cat'], y=df['val'],
            marker=dict(color=df['val'], colorscale=color_scale),
            text=[f'{v:,.0f}' for v in df['val']],
            textposition='outside', textfont=dict(color='white', size=11)
        ))
    
    fig.update_layout(
        title=dict(text=titulo, font=dict(color='#f1f5f9', size=16)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8')),
        yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8')),
        margin=dict(l=10, r=10, t=50, b=10), height=350,
        showlegend=False, coloraxis_showscale=False
    )
    return fig

def grafico_dona(datos, titulo, colores=None):
    """Gráfico de dona profesional."""
    if not datos:
        return None
    
    if colores is None:
        colores = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#6b7280']
    
    fig = go.Figure(go.Pie(
        labels=list(datos.keys()), values=list(datos.values()),
        hole=0.65, marker=dict(colors=colores[:len(datos)]),
        textinfo='percent', textfont=dict(color='white', size=12),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f} clientes<br>%{percent}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=titulo, font=dict(color='#f1f5f9', size=16)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(font=dict(color='#cbd5e1'), bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=10, r=10, t=50, b=10), height=350
    )
    return fig

def grafico_gauge(valor, titulo, max_val=100):
    """Gauge profesional."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': titulo, 'font': {'size': 14, 'color': '#94a3b8'}},
        number={'font': {'size': 36, 'color': '#f1f5f9'}, 'suffix': '%'},
        gauge={
            'axis': {'range': [0, max_val], 'tickcolor': '#475569', 'tickfont': {'color': '#64748b'}},
            'bar': {'color': '#3b82f6'},
            'bgcolor': '#1e293b',
            'borderwidth': 0,
            'steps': [
                {'range': [0, max_val*0.33], 'color': '#7f1d1d'},
                {'range': [max_val*0.33, max_val*0.66], 'color': '#713f12'},
                {'range': [max_val*0.66, max_val], 'color': '#14532d'}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', height=200,
        margin=dict(l=20, r=20, t=30, b=10)
    )
    return fig

def grafico_histograma(df, col, titulo):
    """Histograma profesional."""
    if col not in df.columns:
        return None
    
    fig = go.Figure(go.Histogram(
        x=df[col] * 100 if df[col].max() <= 1 else df[col],
        nbinsx=25, marker=dict(color='#3b82f6', line=dict(color='#1e293b', width=1))
    ))
    
    fig.update_layout(
        title=dict(text=titulo, font=dict(color='#f1f5f9', size=16)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'), title=''),
        yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'), title='Clientes'),
        margin=dict(l=10, r=10, t=50, b=10), height=300
    )
    return fig

def grafico_scatter_mora(df):
    """Scatter de mora vs probabilidad."""
    prob_col = 'probabilidad_pago_ML' if 'probabilidad_pago_ML' in df.columns else 'probabilidad_pago_SIMULADA'
    if prob_col not in df.columns or 'dias mora' not in df.columns:
        return None
    
    sample = df.sample(min(500, len(df)))
    
    fig = px.scatter(
        sample, x='dias mora', y=sample[prob_col]*100,
        color=sample[prob_col]*100, color_continuous_scale='Viridis',
        opacity=0.7
    )
    
    fig.update_layout(
        title=dict(text='Días de Mora vs Probabilidad de Pago', font=dict(color='#f1f5f9', size=16)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'), title='Días de Mora'),
        yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'), title='Probabilidad (%)'),
        coloraxis_colorbar=dict(title='Prob %', tickfont=dict(color='#94a3b8')),
        margin=dict(l=10, r=10, t=50, b=10), height=400
    )
    return fig

# ============================================================================
# APLICACIÓN PRINCIPAL (MEJORADA)
# ============================================================================

def main():
    # MEJORA 2: Auto-refresh unificado al inicio
    refresh_interval_ms = 60000  # 1 minuto en milisegundos
    
    if AUTOREFRESH_AVAILABLE:
        # Un solo autorefresh que actualiza todo
        refresh_count = st_autorefresh(interval=refresh_interval_ms, key="unified_refresh")
    
    # ===== HEADER =====
    col_h1, col_h2 = st.columns([4, 1])
    
    with col_h1:
        st.markdown("# Voicebot Cobranzas")
        st.markdown("**Banco de Bogotá** • Sistema de Inteligencia para Gestión de Cobranzas")

    with col_h2:
        now = datetime.now()
        st.markdown(
            f"""
            <div style="text-align:right;">
                <span style="color:#94a3b8; font-size:0.85rem;">Última hora</span><br>
                <strong style="font-size:1rem;">{now.strftime('%d/%m/%Y %H:%M:%S')}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("## Configuración")
        
        # MEJORA 3: Indicador de estado de actualización
        st.markdown("### Estado de Actualización")
        if AUTOREFRESH_AVAILABLE:
            st.markdown(
                f'<div class="refresh-indicator">🔄 Auto-actualización ACTIVA (cada {refresh_interval_ms//1000}s)</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="error-indicator">⚠️ Auto-refresh NO disponible (instalar streamlit-autorefresh)</div>',
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        # Cargar datos
        st.markdown("### Fuente de Datos")
        
        fuente = st.radio("Seleccionar fuente:", 
                         ["Google Sheets", "Archivo Excel"], 
                         horizontal=True)
        
        df = None
        error_msg = None
        
        if fuente == "Google Sheets":
            st.markdown("**Opción 1: URL predeterminada**")
            
            # MEJORA 4: Cargar automáticamente al inicio
            if 'auto_load' not in st.session_state:
                st.session_state['auto_load'] = True
            
            if st.button("Cargar desde Google Sheets", type="primary") or st.session_state.get('auto_load', False):
                st.session_state['auto_load'] = False
                
                with st.spinner("Cargando datos..."):
                    # Pasar timestamp para forzar recarga en cache
                    df, error_msg = cargar_datos_sheets(
                        url=APPS_SCRIPT_URL,
                        timestamp=datetime.now().timestamp()
                    )
                    
                    if df is not None:
                        st.session_state['df_sheets'] = df
                        st.session_state['last_update'] = datetime.now()
                        st.session_state['last_error'] = None
                        st.success(f"✅ {len(df):,} registros cargados")
                    else:
                        st.session_state['last_error'] = error_msg
                        st.error(f"❌ {error_msg}")
            
            st.markdown("**Opción 2: URL personalizada**")
            url_custom = st.text_input(
                "URL del Google Sheet (formato CSV)", 
                placeholder="https://docs.google.com/spreadsheets/d/TU_SHEET_ID/export?format=csv&gid=0",
                help="Pega aquí la URL de tu Google Sheet público"
            )
            
            if url_custom and st.button("Cargar URL personalizada"):
                with st.spinner("Cargando datos..."):
                    try:
                        df_temp = pd.read_csv(url_custom)
                        if len(df_temp) > 0:
                            df = procesar_datos_sheets(df_temp)
                            st.session_state['df_sheets'] = df
                            st.session_state['last_update'] = datetime.now()
                            st.success(f"✅ {len(df):,} registros cargados")
                        else:
                            st.error("No se encontraron datos")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # MEJORA 5: Usar datos en session_state y mostrar info detallada
            if 'df_sheets' in st.session_state:
                df = st.session_state['df_sheets']
                last_update = st.session_state.get('last_update', datetime.now())
                time_diff = datetime.now() - last_update
                
                # Indicador visual de frescura de datos
                if time_diff.seconds < 60:
                    freshness = "🟢 RECIENTE"
                    color = "success"
                elif time_diff.seconds < 180:
                    freshness = "🟡 ACTUALIZADO"
                    color = "warning"
                else:
                    freshness = "🔴 ANTIGUO"
                    color = "error"
                
                st.markdown(f"""
                **Estado de Datos:**
                - Registros: {len(df):,}
                - Última actualización: {last_update.strftime('%H:%M:%S')}
                - Hace: {time_diff.seconds}s
                - Estado: {freshness}
                """)
                
                # Mostrar último error si existe
                if st.session_state.get('last_error'):
                    with st.expander("⚠️ Último error"):
                        st.error(st.session_state['last_error'])
        
        else:  # Archivo Excel
            archivo_subido = st.file_uploader("Cargar archivo Excel", type=['xlsx'])
            if archivo_subido:
                df = pd.read_excel(archivo_subido)
                df = procesar_datos_sheets(df)  # Aplicar mismo procesamiento
                st.success(f"✅ {len(df):,} registros")
        
        if df is None:
            st.warning("⚠️ Sin datos cargados")
            st.info("👆 Presiona 'Cargar desde Google Sheets' o sube un archivo Excel")
        
        st.markdown("---")
        
        # Filtros (mantener los mismos)
        if df is not None:
            st.markdown("### Filtros")
            
            filtro_camp = st.radio("Campaña", ['Todos', 'Con Campaña', 'Sin Campaña'], horizontal=True)
            
            # Segmento
            seg_col = 'segmento_ML' if 'segmento_ML' in df.columns else 'segmento_SIMULADO'
            if seg_col in df.columns:
                segs_disponibles = df[seg_col].dropna().unique().tolist()
                filtro_seg = st.multiselect("Segmentos", segs_disponibles, default=segs_disponibles)
            else:
                filtro_seg = []
            
            # Mora
            if 'dias mora' in df.columns:
                mora_min, mora_max = int(df['dias mora'].min()), int(df['dias mora'].max())
                if mora_min == mora_max:
                    st.info(f"Todos los registros tienen {mora_min} días de mora")
                    filtro_mora = (mora_min, mora_max)
                else:
                    filtro_mora = st.slider("Días de Mora", mora_min, mora_max, (mora_min, mora_max))
            else:
                filtro_mora = (0, 999)
            
            # Producto
            prod_col = 'producto' if 'producto' in df.columns else 'Tipo Producto'
            if prod_col in df.columns:
                prods = ['Todos'] + df[prod_col].dropna().unique().tolist()
                filtro_prod = st.selectbox("Producto", prods)
            else:
                filtro_prod = 'Todos'
            
            # Aplicar filtros
            df_f = df.copy()
            
            if filtro_camp == 'Con Campaña':
                mask = (df_f['campaign'] == True) if df_f['campaign'].dtype == bool else (df_f['campaign'].astype(str).str.lower() == 'true')
                df_f = df_f[mask]
            elif filtro_camp == 'Sin Campaña':
                mask = (df_f['campaign'] == False) if df_f['campaign'].dtype == bool else (df_f['campaign'].astype(str).str.lower() != 'true')
                df_f = df_f[mask]
            
            if seg_col in df_f.columns and filtro_seg:
                df_f = df_f[df_f[seg_col].isin(filtro_seg)]
            
            if 'dias mora' in df_f.columns:
                df_f = df_f[(df_f['dias mora'] >= filtro_mora[0]) & (df_f['dias mora'] <= filtro_mora[1])]
            
            if filtro_prod != 'Todos':
                prod_col = 'producto' if 'producto' in df_f.columns else 'Tipo Producto'
                if prod_col in df_f.columns:
                    df_f = df_f[df_f[prod_col] == filtro_prod]
            
            st.markdown("---")
            st.metric("Registros filtrados", f"{len(df_f):,}")
        else:
            df_f = None
    
    # ===== CONTENIDO PRINCIPAL =====
    if df_f is None or len(df_f) == 0:
        st.info("👆 Selecciona una fuente de datos y carga la información para comenzar")
        
        # Mostrar información sobre la estructura esperada
        with st.expander("📊 Estructura de datos esperada"):
            st.markdown("""
            **Columnas principales requeridas:**
            - `unique_user_id`, `Phone`, `name`, `cedula`
            - `campaign`, `producto`, `dias mora`, `Saldo en mora`
            - `Saldo total`, `Capital Total`, `Cuota Mensual Aprox`
            - `Tipo Producto`, `POPUP_CAMP`
            
            **Columnas opcionales:**
            - `Phone_2`, `Phone_3`, `fullname`, `celular`
            - `Campaña`, `Nombre producto`, `Capital Mora`
            - `Ciclo`, `Interes Corriente`, `Interes Mora`
            """)
        
        with st.expander("🔧 Cómo configurar Google Sheets"):
            st.markdown("""
            **Para usar Google Sheets:**
            
            1. **Hacer el sheet público:**
               - Abre tu Google Sheet
               - Clic en 'Compartir' (esquina superior derecha)
               - Cambiar a 'Cualquier persona con el enlace puede ver'
               - Guardar
            
            2. **Obtener la URL:**
               - Copia el ID del sheet desde la URL
               - Formato: `https://docs.google.com/spreadsheets/d/TU_SHEET_ID/export?format=csv&gid=0`
               - Reemplaza `TU_SHEET_ID` con el ID real
            
            3. **Estructura requerida:**
               - Primera fila debe contener los nombres de las columnas
               - Datos numéricos en formato correcto
               - Sin filas vacías al inicio
            
            4. **Auto-actualización:**
               - El dashboard se actualiza automáticamente cada 60 segundos
               - Los datos se refrescan desde el cache cada 30 segundos
               - Modifica el Google Sheet y espera hasta 60s para ver cambios
            """)
        
        with st.expander("⚙️ Instalación de dependencias"):
            st.markdown("""
            **Para activar auto-actualización, instala:**
            ```bash
            pip install streamlit-autorefresh
            ```
            
            **Otras dependencias requeridas:**
            ```bash
            pip install streamlit pandas plotly requests openpyxl
            ```
            """)
        
        return
    
    m = calcular_metricas(df_f)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Resumen Ejecutivo",
        "🎯 Segmentación",
        "🤖 Modelo ML",
        "📢 Campañas",
        "🔍 Explorar Datos",
        "📞 Gestionar Llamadas",
        "📋 Trazabilidad Llamadas"
    ])
    
    # ===== TAB 1: RESUMEN =====
    with tab1:
        # KPIs
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Clientes", f"{m['total']:,}")
        c2.metric("GAC Total", f"${m['gac_total']/1e6:.1f}M")
        c3.metric("Con Campaña", f"{m['con_campana']:,}", f"{m['pct_campana']:.0f}%")
        c4.metric("Prob. Media", f"{m['prob_media']:.1f}%")
        c5.metric("Mora Prom.", f"{m['mora_promedio']:.0f} días")
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            fig = grafico_barras(m['mora_dist'], 'Distribución por Días de Mora', 'Blues')
            if fig: st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = grafico_dona(m['mecanismos'], 'Mecanismos de Negociación')
            if fig: st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        with col3:
            fig = grafico_barras(m['productos'], 'Distribución por Producto', 'Viridis')
            if fig: st.plotly_chart(fig, use_container_width=True)
        with col4:
            prob_col = 'probabilidad_pago_ML' if 'probabilidad_pago_ML' in df_f.columns else 'probabilidad_pago_SIMULADA'
            fig = grafico_histograma(df_f, prob_col, 'Distribución de Probabilidad')
            if fig: st.plotly_chart(fig, use_container_width=True)
    
    # ===== TAB 2: SEGMENTACIÓN =====
    with tab2:
        st.markdown("### Análisis de Segmentos")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            colores_seg = {'A': '#10b981', 'B': '#3b82f6', 'C': '#f59e0b', 'D': '#ef4444'}
            if m['segmentos']:
                df_seg = pd.DataFrame({'Segmento': list(m['segmentos'].keys()), 'Clientes': list(m['segmentos'].values())})
                df_seg['Color'] = df_seg['Segmento'].map(colores_seg)
                
                fig = go.Figure(go.Bar(
                    x=df_seg['Segmento'], y=df_seg['Clientes'],
                    marker_color=df_seg['Color'],
                    text=[f'{v:,}' for v in df_seg['Clientes']],
                    textposition='outside', textfont=dict(color='white', size=14)
                ))
                fig.update_layout(
                    title=dict(text='Clientes por Segmento', font=dict(color='#f1f5f9', size=18)),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(tickfont=dict(color='#f1f5f9', size=14)),
                    yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8')),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Definición")
            info_seg = [
                ("A", "≥75%", "Alta prioridad"),
                ("B", "50-74%", "Media prioridad"),
                ("C", "25-49%", "Baja prioridad"),
                ("D", "<25%", "Evaluar contacto")
            ]
            for seg, prob, desc in info_seg:
                cant = m['segmentos'].get(seg, 0)
                st.markdown(f"**{seg}** ({prob}): **{cant:,}** - {desc}")
        
        st.markdown("---")
        fig = grafico_scatter_mora(df_f)
        if fig: st.plotly_chart(fig, use_container_width=True)
    
    # ===== TAB 3: MODELO ML =====
    with tab3:
        st.markdown("### Modelo XGBoost")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Métricas de Evaluación")
            m1, m2 = st.columns(2)
            with m1:
                fig = grafico_gauge(66.26, 'AUC-ROC')
                st.plotly_chart(fig, use_container_width=True)
            with m2:
                fig = grafico_gauge(84.85, 'Accuracy')
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("##### Métricas adicionales")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Precision", "31.25%")
            mc2.metric("Recall", "1.11%")
            mc3.metric("F1-Score", "2.15%")
        
        with col2:
            st.markdown("#### Importancia de Variables")
            imp = {
                'Tiene Campaña': 35.4, 'Requiere Pago': 17.9, 'Días de Mora': 9.0,
                'Descuento': 8.0, 'Hora': 6.9, 'Saldo Mora': 6.4,
                'Producto': 5.9, 'N° Intento': 5.4, 'Canal': 5.2
            }
            fig = grafico_barras(imp, 'Importancia (%)', 'Purples')
            if fig: st.plotly_chart(fig, use_container_width=True)
        
        st.warning("⚠️ Modelo Simulado: Entrenado con datos ficticios. Reentrenar con datos reales antes de producción.")
    
    # ===== TAB 4: CAMPAÑAS =====
    with tab4:
        st.markdown("### Análisis de Campañas")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Con Campaña", f"{m['con_campana']:,}")
        c2.metric("Sin Campaña", f"{m['sin_campana']:,}")
        c3.metric("Req. Pago", f"{m['req_pago']:,}")
        c4.metric("Sin Pago Inicial", f"{m['no_req_pago']:,}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            fig = grafico_barras(m['mecanismos'], 'Clientes por Mecanismo', 'Tealgrn', horizontal=False)
            if fig: st.plotly_chart(fig, use_container_width=True)
        with col2:
            if m['mecanismos']:
                df_mec = pd.DataFrame({'Mecanismo': list(m['mecanismos'].keys()), 'Clientes': list(m['mecanismos'].values())})
                df_mec = df_mec.sort_values('Clientes', ascending=False)
                df_mec['% Total'] = (df_mec['Clientes'] / df_mec['Clientes'].sum() * 100).round(1)
                st.dataframe(df_mec, use_container_width=True, hide_index=True)
    
    # ===== TAB 5: EXPLORAR =====
    with tab5:
        st.markdown("### Exploración de Datos")
        
        st.markdown("#### Top 10 por Valor Esperado")
        val_col = 'valor_esperado_ML' if 'valor_esperado_ML' in df_f.columns else 'valor_esperado_SIMULADO'
        prob_col = 'probabilidad_pago_ML' if 'probabilidad_pago_ML' in df_f.columns else 'probabilidad_pago_SIMULADA'
        prod_col = 'producto' if 'producto' in df_f.columns else 'Tipo Producto'
        
        cols_top = ['name', prod_col, 'dias mora', prob_col, 'GAC_proyectado', val_col]
        cols_exist = [c for c in cols_top if c in df_f.columns]
        
        if val_col in df_f.columns:
            top10 = df_f.nlargest(10, val_col)[cols_exist]
            st.dataframe(top10, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Buscar
        st.markdown("#### Buscar Cliente")
        busq = st.text_input("🔍 Buscar por nombre, cédula o producto")
        if busq:
            mask = df_f.apply(lambda row: busq.lower() in str(row.values).lower(), axis=1)
            resultados = df_f[mask]
            st.markdown(f"**{len(resultados)} resultados encontrados**")
            st.dataframe(resultados.head(50), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Exportar
        col_e1, col_e2 = st.columns([1, 3])
        with col_e1:
            csv = df_f.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Exportar CSV", 
                csv, 
                f"cobranzas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                "text/csv",
                key="download_csv"
            )
        with col_e2:
            st.caption(f"📊 {len(df_f):,} registros | {len(df_f.columns)} columnas | Última actualización: {st.session_state.get('last_update', datetime.now()).strftime('%H:%M:%S')}")
    
    # ===== TAB 6: GESTIONAR LLAMADAS =====
    with tab6:
        st.markdown("### Gestionar Llamadas")
        
        if 'cedula' not in df_f.columns:
            st.error("❌ No se encontró la columna 'cedula' en los datos")
        else:
            st.markdown(f"**Total clientes disponibles: {len(df_f):,}**")
            
            # Filtro adicional para priorización
            col_pri1, col_pri2 = st.columns(2)
            with col_pri1:
                ordenar_por = st.selectbox(
                    "Ordenar por:",
                    ["Valor esperado (mayor)", "Probabilidad (mayor)", "Días mora (mayor)", "Saldo mora (mayor)"],
                    index=0
                )
            with col_pri2:
                mostrar = st.number_input("Mostrar registros:", min_value=5, max_value=100, value=20, step=5)
            
            # Ordenar según selección
            if ordenar_por == "Valor esperado (mayor)":
                val_col = 'valor_esperado_ML' if 'valor_esperado_ML' in df_f.columns else 'valor_esperado_SIMULADO'
                df_llamadas = df_f.sort_values(val_col, ascending=False) if val_col in df_f.columns else df_f
            elif ordenar_por == "Probabilidad (mayor)":
                prob_col = 'probabilidad_pago_ML' if 'probabilidad_pago_ML' in df_f.columns else 'probabilidad_pago_SIMULADA'
                df_llamadas = df_f.sort_values(prob_col, ascending=False) if prob_col in df_f.columns else df_f
            elif ordenar_por == "Días mora (mayor)":
                df_llamadas = df_f.sort_values('dias mora', ascending=False) if 'dias mora' in df_f.columns else df_f
            else:  # Saldo mora
                df_llamadas = df_f.sort_values('Saldo en mora', ascending=False) if 'Saldo en mora' in df_f.columns else df_f
            
            st.markdown("---")
            
            # Mostrar clientes priorizados
            for idx, row in df_llamadas.head(int(mostrar)).iterrows():
                col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 2, 1.5, 1, 1.5, 1, 1])
                
                with col1:
                    st.text(f"CC: {row.get('cedula', 'N/A')}")
                with col2:
                    st.text(f"{row.get('name', 'N/A')[:20]}")
                with col3:
                    st.text(f"📞 {row.get('Phone', 'N/A')}")
                with col4:
                    mora_dias = row.get('dias mora', 0)
                    color_mora = "🔴" if mora_dias > 90 else "🟡" if mora_dias > 30 else "🟢"
                    st.text(f"{color_mora} {mora_dias:.0f}d")
                with col5:
                    saldo = row.get('Saldo en mora', 0)
                    st.text(f"${saldo:,.0f}")
                with col6:
                    prob_col = 'probabilidad_pago_ML' if 'probabilidad_pago_ML' in df_f.columns else 'probabilidad_pago_SIMULADA'
                    if prob_col in df_f.columns:
                        prob = row.get(prob_col, 0) * 100
                        st.text(f"{prob:.0f}%")
                with col7:
                    if st.button("☎️ Llamar", key=f"call_{idx}", type="primary"):
                        if not REQUESTS_AVAILABLE:
                            st.error("Módulo 'requests' no disponible")
                        else:
                            webhook_url = "https://workflows.aosinternational.us/webhook-test/AmericanBPO"
                            cedula = str(row.get('cedula', ''))
                            
                            try:
                                with st.spinner("Iniciando llamada..."):
                                    response = requests.post(webhook_url, json={"cedula": cedula}, timeout=5)
                                    if response.status_code == 200:
                                        st.success(f"✅ Llamada iniciada para {cedula}")
                                    else:
                                        st.error(f"❌ Error: {response.status_code}")
                            except requests.Timeout:
                                st.error("⏱️ Timeout: El webhook no respondió")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                
                st.markdown("---")

    # ===== TAB 7: TRAZABILIDAD LLAMADAS =====
    with tab7:
        st.markdown("### 📋 Trazabilidad de Llamadas")
        
        # Configuración API ElevenLabs
        ELEVENLABS_API_KEY = "sk_cb54edd4334b8729b80d295c75432102be6879217dd736f6"
        AGENT_ID = "agent_7901kfgkj27ef9mt2d2whyk2nzrg"
        
        # Funciones para API ElevenLabs
        @st.cache_data(ttl=60)
        def obtener_conversaciones(agent_id, cursor=""):
            """Obtiene lista de conversaciones del agente."""
            if not REQUESTS_AVAILABLE:
                return None, "Requests no disponible"
            
            try:
                url = "https://api.elevenlabs.io/v1/convai/conversations"
                headers = {"xi-api-key": ELEVENLABS_API_KEY}
                params = {"agent_id": agent_id, "cursor": cursor}
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    return response.json(), None
                else:
                    return None, f"Error {response.status_code}: {response.text}"
            except Exception as e:
                return None, str(e)
        
        def obtener_detalle_conversacion(conversation_id):
            """Obtiene detalle de una conversación específica."""
            if not REQUESTS_AVAILABLE:
                return None, "Requests no disponible"
            
            try:
                url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}"
                headers = {"xi-api-key": ELEVENLABS_API_KEY}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    return response.json(), None
                else:
                    return None, f"Error {response.status_code}: {response.text}"
            except Exception as e:
                return None, str(e)
        
        def obtener_audio_conversacion(conversation_id):
            """Obtiene el audio de una conversación."""
            if not REQUESTS_AVAILABLE:
                return None, "Requests no disponible"
            
            try:
                url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}/audio"
                headers = {"xi-api-key": ELEVENLABS_API_KEY}
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    return response.content, None
                else:
                    return None, f"Error {response.status_code}: {response.text}"
            except Exception as e:
                return None, str(e)
        
        # Cargar conversaciones
        with st.spinner("🔄 Cargando conversaciones..."):
            data, error = obtener_conversaciones(AGENT_ID)
        
        if error:
            st.error(f"❌ Error al cargar conversaciones: {error}")
            return
        
        if not data or 'conversations' not in data:
            st.warning("⚠️ No se encontraron conversaciones")
            return
        
        conversaciones = data['conversations']
        
        # Métricas generales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_calls = len(conversaciones)
        successful_calls = len([c for c in conversaciones if c.get('call_successful') == 'success'])
        failed_calls = len([c for c in conversaciones if c.get('call_successful') != 'success'])
        total_duration = sum([c.get('call_duration_secs', 0) for c in conversaciones])
        avg_duration = total_duration / total_calls if total_calls > 0 else 0
        
        col1.metric("Total Llamadas", f"{total_calls:,}")
        col2.metric("Exitosas", f"{successful_calls:,}", f"{successful_calls/total_calls*100:.1f}%" if total_calls > 0 else "0%")
        col3.metric("Fallidas", f"{failed_calls:,}", f"{failed_calls/total_calls*100:.1f}%" if total_calls > 0 else "0%")
        col4.metric("Duración Total", f"{total_duration//60:.0f}m {total_duration%60:.0f}s")
        col5.metric("Duración Promedio", f"{avg_duration:.0f}s")
        
        st.markdown("---")
        
        # Filtros
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            filtro_estado = st.selectbox(
                "Estado de llamada:",
                ["Todas", "Exitosas", "Fallidas"],
                index=0
            )
        
        with col_f2:
            filtro_duracion = st.selectbox(
                "Duración:",
                ["Todas", "Cortas (<30s)", "Normales (30s-2m)", "Largas (>2m)"],
                index=0
            )
        
        with col_f3:
            mostrar_registros = st.number_input(
                "Mostrar registros:",
                min_value=10, max_value=100, value=20, step=10
            )
        
        # Aplicar filtros
        conversaciones_filtradas = conversaciones.copy()
        
        if filtro_estado == "Exitosas":
            conversaciones_filtradas = [c for c in conversaciones_filtradas if c.get('call_successful') == 'success']
        elif filtro_estado == "Fallidas":
            conversaciones_filtradas = [c for c in conversaciones_filtradas if c.get('call_successful') != 'success']
        
        if filtro_duracion == "Cortas (<30s)":
            conversaciones_filtradas = [c for c in conversaciones_filtradas if c.get('call_duration_secs', 0) < 30]
        elif filtro_duracion == "Normales (30s-2m)":
            conversaciones_filtradas = [c for c in conversaciones_filtradas if 30 <= c.get('call_duration_secs', 0) <= 120]
        elif filtro_duracion == "Largas (>2m)":
            conversaciones_filtradas = [c for c in conversaciones_filtradas if c.get('call_duration_secs', 0) > 120]
        
        # Limitar registros mostrados
        conversaciones_mostrar = conversaciones_filtradas[:int(mostrar_registros)]
        
        st.markdown(f"**Mostrando {len(conversaciones_mostrar)} de {len(conversaciones_filtradas)} conversaciones**")
        
        # Lista de conversaciones
        for i, conv in enumerate(conversaciones_mostrar):
            with st.expander(
                f"📞 {conv.get('call_summary_title', 'Sin título')} - "
                f"{datetime.fromtimestamp(conv.get('start_time_unix_secs', 0)).strftime('%d/%m %H:%M')} - "
                f"{conv.get('call_duration_secs', 0)}s"
            ):
                # Información básica
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.markdown(f"""
                    **📅 Información Básica:**
                    - ID: `{conv.get('conversation_id', 'N/A')}`
                    - Estado: {'✅ Exitosa' if conv.get('call_successful') == 'success' else '❌ Fallida'}
                    - Duración: {conv.get('call_duration_secs', 0)}s
                    - Mensajes: {conv.get('message_count', 0)}
                    """)
                
                with col_info2:
                    start_time = datetime.fromtimestamp(conv.get('start_time_unix_secs', 0))
                    st.markdown(f"""
                    **🕰️ Tiempo:**
                    - Inicio: {start_time.strftime('%d/%m/%Y %H:%M:%S')}
                    - Dirección: {conv.get('direction', 'N/A')}
                    - Agente: {conv.get('agent_name', 'N/A')}
                    - Rating: {conv.get('rating', 'Sin rating')}
                    """)
                
                with col_info3:
                    branch_id = conv.get('branch_id', 'N/A')
                    version_id = conv.get('version_id', 'N/A')
                    st.markdown(f"""
                    **📝 Resumen:**
                    - Título: {conv.get('call_summary_title', 'N/A')}
                    - Estado: {conv.get('status', 'N/A')}
                    - Branch: `{branch_id[:20] + '...' if branch_id and branch_id != 'N/A' and len(branch_id) > 20 else branch_id}`
                    - Version: `{version_id[:20] + '...' if version_id and version_id != 'N/A' and len(version_id) > 20 else version_id}`
                    """)
                
                # Botones de acción
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button(f"🔍 Ver Detalle", key=f"detail_{i}"):
                        with st.spinner("Cargando detalle..."):
                            detalle, error_det = obtener_detalle_conversacion(conv['conversation_id'])
                            
                            if error_det:
                                st.error(f"Error: {error_det}")
                            else:
                                st.session_state[f'detalle_{conv["conversation_id"]}'] = detalle
                                st.success("Detalle cargado")
                
                with col_btn2:
                    if st.button(f"🎧 Descargar Audio", key=f"audio_{i}"):
                        with st.spinner("Descargando audio..."):
                            audio_data, error_audio = obtener_audio_conversacion(conv['conversation_id'])
                            
                            if error_audio:
                                st.error(f"Error: {error_audio}")
                            else:
                                st.download_button(
                                    label="💾 Descargar MP3",
                                    data=audio_data,
                                    file_name=f"llamada_{conv['conversation_id']}.mp3",
                                    mime="audio/mpeg",
                                    key=f"download_audio_{i}"
                                )
                
                with col_btn3:
                    if st.button(f"📋 Ver Transcripción", key=f"transcript_{i}"):
                        st.session_state[f'show_transcript_{conv["conversation_id"]}'] = True
                
                # Mostrar detalle si está cargado
                detalle_key = f'detalle_{conv["conversation_id"]}'
                if detalle_key in st.session_state:
                    detalle = st.session_state[detalle_key]
                    
                    st.markdown("#### 📝 Detalle de la Conversación")
                    
                    # Información adicional del detalle
                    if 'metadata' in detalle:
                        metadata = detalle['metadata']
                        
                        col_meta1, col_meta2 = st.columns(2)
                        
                        with col_meta1:
                            st.markdown(f"""
                            **📊 Métricas:**
                            - Costo: ${metadata.get('cost', 0)/100:.2f}
                            - Teléfono: {metadata.get('phone_call', {}).get('external_number', 'N/A')}
                            - Idioma: {metadata.get('main_language', 'N/A')}
                            - Razón fin: {metadata.get('termination_reason', 'N/A')}
                            """)
                        
                        with col_meta2:
                            if 'charging' in metadata:
                                charging = metadata['charging']
                                st.markdown(f"""
                                **💰 Facturación:**
                                - Precio LLM: ${charging.get('llm_price', 0):.4f}
                                - Cargo llamada: {charging.get('call_charge', 0)}
                                - Tier: {charging.get('tier', 'N/A')}
                                - Minutos gratis: {charging.get('free_minutes_consumed', 0)}
                                """)
                    
                    # Variables dinámicas
                    if 'conversation_initiation_client_data' in detalle:
                        client_data = detalle['conversation_initiation_client_data']
                        if 'dynamic_variables' in client_data:
                            variables = client_data['dynamic_variables']
                            
                            st.markdown("**📊 Variables de la Llamada:**")
                            
                            # Mostrar variables importantes
                            vars_importantes = ['Nombre', 'Producto', 'Saldo_en_mora', 'Fecha_Pago_Cliente', 'Campaign']
                            
                            col_vars = st.columns(len(vars_importantes))
                            for idx, var in enumerate(vars_importantes):
                                if var in variables:
                                    with col_vars[idx]:
                                        st.metric(var.replace('_', ' '), variables[var])
                
                # Mostrar transcripción si está solicitada
                transcript_key = f'show_transcript_{conv["conversation_id"]}'
                if st.session_state.get(transcript_key, False):
                    if detalle_key in st.session_state:
                        detalle = st.session_state[detalle_key]
                        
                        if 'transcript' in detalle:
                            st.markdown("#### 🗣️ Transcripción de la Llamada")
                            
                            transcript = detalle['transcript']
                            
                            for msg_idx, mensaje in enumerate(transcript):
                                role = mensaje.get('role', 'unknown')
                                content = mensaje.get('message', '')
                                time_in_call = mensaje.get('time_in_call_secs', 0)
                                
                                # Icono según el rol
                                icon = "🤖" if role == 'agent' else "👤" if role == 'user' else "❓"
                                
                                # Color de fondo según el rol
                                bg_color = "background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);" if role == 'agent' else "background: linear-gradient(135deg, #065f46 0%, #047857 100%);"
                                
                                st.markdown(
                                    f"""
                                    <div style="{bg_color} padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {'#3b82f6' if role == 'agent' else '#10b981'};">
                                        <strong>{icon} {role.title()} ({time_in_call}s):</strong><br>
                                        {content}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            
                            # Botón para ocultar transcripción
                            if st.button(f"🙈 Ocultar Transcripción", key=f"hide_transcript_{i}"):
                                st.session_state[transcript_key] = False
                                st.rerun()
                        else:
                            st.warning("No hay transcripción disponible")
                    else:
                        st.warning("Primero carga el detalle de la conversación")
        
        # Paginación
        if len(conversaciones_filtradas) > mostrar_registros:
            st.markdown("---")
            st.info(f"📄 Mostrando {mostrar_registros} de {len(conversaciones_filtradas)} conversaciones. Ajusta el filtro 'Mostrar registros' para ver más.")
        
        # Resumen de análisis
        if conversaciones:
            st.markdown("---")
            st.markdown("### 📊 Análisis de Llamadas")
            
            # Gráfico de duraciones
            duraciones = [c.get('call_duration_secs', 0) for c in conversaciones if c.get('call_duration_secs', 0) > 0]
            
            if duraciones:
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    fig_dur = go.Figure(go.Histogram(
                        x=duraciones,
                        nbinsx=20,
                        marker=dict(color='#3b82f6', line=dict(color='#1e293b', width=1))
                    ))
                    
                    fig_dur.update_layout(
                        title=dict(text='Distribución de Duraciones', font=dict(color='#f1f5f9', size=16)),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'), title='Segundos'),
                        yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'), title='Llamadas'),
                        margin=dict(l=10, r=10, t=50, b=10), height=300
                    )
                    
                    st.plotly_chart(fig_dur, use_container_width=True)
                
                with col_chart2:
                    # Gráfico de éxito vs fallo
                    estados = {}
                    for c in conversaciones:
                        estado = 'Exitosa' if c.get('call_successful') == 'success' else 'Fallida'
                        estados[estado] = estados.get(estado, 0) + 1
                    
                    fig_estados = go.Figure(go.Pie(
                        labels=list(estados.keys()),
                        values=list(estados.values()),
                        hole=0.6,
                        marker=dict(colors=['#10b981', '#ef4444']),
                        textinfo='percent+label',
                        textfont=dict(color='white', size=12)
                    ))
                    
                    fig_estados.update_layout(
                        title=dict(text='Tasa de Éxito', font=dict(color='#f1f5f9', size=16)),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        legend=dict(font=dict(color='#cbd5e1')),
                        margin=dict(l=10, r=10, t=50, b=10), height=300
                    )
                    
                    st.plotly_chart(fig_estados, use_container_width=True)

# ============================================================================
# EJECUTAR
# ============================================================================

if __name__ == "__main__":
    main()