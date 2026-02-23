import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Control de Deudas — Terapias PHL",
    page_icon="📊",
    layout="wide"
)

# ── Estilos personalizados ───────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700&display=swap');

  html, body, [class*="css"] {
    background-color: #0D0D0D !important;
    color: #E8E8E8 !important;
    font-family: 'DM Sans', sans-serif;
  }

  section[data-testid="stSidebar"] {
    background-color: #141414 !important;
    border-right: 1px solid #2A2A2A;
  }

  h1 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: .05em; }
  h2, h3 { font-family: 'Bebas Neue', sans-serif !important; color: #5A5A5A !important; letter-spacing: .05em; }

  .kpi-card {
    background: #141414;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: .5rem;
    position: relative;
  }
  .kpi-label { font-size: .72rem; color: #5A5A5A; text-transform: uppercase; letter-spacing: .07em; margin-bottom: .3rem; }
  .kpi-value { font-family: 'Bebas Neue', sans-serif; font-size: 3rem; line-height: 1; }
  .kpi-sub   { font-size: .72rem; color: #5A5A5A; margin-top: .2rem; }
  .red    { color: #FF2B2B; }
  .amber  { color: #FF9500; }
  .green  { color: #00C471; }
  .blue   { color: #4C9EFF; }
  .white  { color: #E8E8E8; }

  .badge {
    display: inline-flex; align-items: center; gap: .5rem;
    background: rgba(255,43,43,.12); border: 1px solid rgba(255,43,43,.35);
    padding: .4rem 1rem; border-radius: 100px;
    font-family: 'JetBrains Mono', monospace; font-size: .72rem;
    color: #FF2B2B; letter-spacing: .06em; text-transform: uppercase;
  }

  .stFileUploader { background: #141414; border-radius: 12px; border: 1px dashed #2A2A2A; }
  hr { border-color: #2A2A2A !important; }
</style>
""", unsafe_allow_html=True)

# ── Colores ────────────────────────────────────────────────────────────────
COLOR_RED   = "#FF2B2B"
COLOR_AMBER = "#FF9500"
COLOR_GREEN = "#00C471"
COLOR_BLUE  = "#4C9EFF"
COLOR_BG    = "#0D0D0D"
COLOR_PANEL = "#141414"
COLOR_MUTED = "#5A5A5A"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📂 CARGAR REGISTRO")
    st.markdown("---")
    uploaded = st.file_uploader(
        "Sube REGISTRO_VISITAS_PHL.xlsx",
        type=["xlsx", "xls"],
        help="Archivo con hojas mensuales (ENERO, FEBRERO, etc.)"
    )
    st.markdown("---")
    st.markdown("""
    <div style='font-family:JetBrains Mono;font-size:.65rem;color:#5A5A5A;line-height:1.8'>
    <b style='color:#E8E8E8'>✓ Registro Manual Semanal</b><br>
    • Una hoja por mes<br>
    • Seguimiento de deudas<br>
    • Control de reposiciones
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown("<h1 style='font-size:3.5rem;margin-bottom:0'>CONTROL DE <span style='color:#FF2B2B'>DEUDAS</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-family:JetBrains Mono;font-size:.72rem;color:#5A5A5A;letter-spacing:.06em;text-transform:uppercase'>Patología del Habla y Lenguaje · Seguimiento Semanal · {datetime.now().strftime('%B %Y')}</p>", unsafe_allow_html=True)
with col_badge:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="badge">📊 ACTUALIZACIÓN SEMANAL</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Funciones de carga ────────────────────────────────────────────────────────
@st.cache_data
def cargar_hojas_disponibles(archivo):
    """Lee todas las hojas del Excel"""
    xl = pd.ExcelFile(archivo)
    return xl.sheet_names

@st.cache_data
def cargar_datos_mes(archivo, hoja):
    """Carga datos de una hoja específica"""
    # Saltar la primera fila (título del mes)
    df = pd.read_excel(archivo, sheet_name=hoja, skiprows=1)
    
    # Limpiar columnas
    df = df[[col for col in df.columns if 'Unnamed' not in str(col)]]
    
    # Renombrar si es necesario
    df.columns = df.columns.str.strip()
    
    # Agregar columna de mes
    df['MES'] = hoja
    
    # Limpiar datos
    df = df.dropna(subset=['ESTUDIANTE'])
    
    # Convertir columnas numéricas
    cols_numericas = ['OFRECIDAS REG', 'TERAPIAS ADEUDADAS', 'OFRECIDAS REP', 
                      'DEUDA ADQUIRIDA', 'BALANCE DE DEUDAS']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

if uploaded:
    hojas_disponibles = cargar_hojas_disponibles(uploaded)
    
    st.markdown("### 📅 Selecciona los Meses a Analizar")
    
    # Crear checkboxes para cada mes
    cols = st.columns(min(6, len(hojas_disponibles)))
    meses_seleccionados = []
    
    for i, hoja in enumerate(hojas_disponibles):
        with cols[i % 6]:
            if st.checkbox(hoja, value=True, key=f"mes_{hoja}"):
                meses_seleccionados.append(hoja)
    
    if not meses_seleccionados:
        st.warning("⚠️ Selecciona al menos un mes para analizar")
        st.stop()
    
    # Cargar datos de meses seleccionados
    dfs = []
    for mes in meses_seleccionados:
        df_mes = cargar_datos_mes(uploaded, mes)
        dfs.append(df_mes)
    
    df_completo = pd.concat(dfs, ignore_index=True)
    
    st.success(f"✅ Analizando {len(meses_seleccionados)} mes(es): {', '.join(meses_seleccionados)}")
    st.markdown("---")
    
    # ── Cálculos principales ──────────────────────────────────────────────────
    total_estudiantes = df_completo['ESTUDIANTE'].nunique()
    total_especialistas = df_completo['ESPEC.'].nunique()
    
    # Obtener el último balance de cada estudiante
    df_ultimo_balance = df_completo.sort_values('MES').groupby('ESTUDIANTE').last().reset_index()
    
    deuda_total = df_ultimo_balance['BALANCE DE DEUDAS'].sum()
    deuda_promedio = df_ultimo_balance['BALANCE DE DEUDAS'].mean()
    
    estudiantes_criticos = len(df_ultimo_balance[df_ultimo_balance['BALANCE DE DEUDAS'] > 5])
    estudiantes_alerta = len(df_ultimo_balance[(df_ultimo_balance['BALANCE DE DEUDAS'] > 0) & 
                                                (df_ultimo_balance['BALANCE DE DEUDAS'] <= 5)])
    estudiantes_ok = len(df_ultimo_balance[df_ultimo_balance['BALANCE DE DEUDAS'] == 0])
    
    reposiciones_ofrecidas = df_completo['OFRECIDAS REP'].sum()
    deudas_adquiridas = df_completo['DEUDA ADQUIRIDA'].sum()
    
    # ── KPIs ──────────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid {COLOR_RED}">
          <div class="kpi-label">🚨 Deuda Total</div>
          <div class="kpi-value red">{int(deuda_total)}</div>
          <div class="kpi-sub">Terapias pendientes</div>
        </div>""", unsafe_allow_html=True)
    
    with k2:
        nivel = "🔴" if estudiantes_criticos > 10 else "🟡" if estudiantes_criticos > 5 else "🟢"
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid {COLOR_AMBER}">
          <div class="kpi-label">{nivel} Casos Críticos</div>
          <div class="kpi-value amber">{estudiantes_criticos}</div>
          <div class="kpi-sub">Balance > 5 terapias</div>
        </div>""", unsafe_allow_html=True)
    
    with k3:
        tasa_repo = round((reposiciones_ofrecidas / deuda_total * 100)) if deuda_total > 0 else 0
        color_tasa = COLOR_GREEN if tasa_repo > 50 else COLOR_AMBER if tasa_repo > 25 else COLOR_RED
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid {color_tasa}">
          <div class="kpi-label">📈 Reposiciones</div>
          <div class="kpi-value" style="color:{color_tasa}">{int(reposiciones_ofrecidas)}</div>
          <div class="kpi-sub">{tasa_repo}% vs deuda total</div>
        </div>""", unsafe_allow_html=True)
    
    with k4:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid {COLOR_BLUE}">
          <div class="kpi-label">👥 Estudiantes</div>
          <div class="kpi-value blue">{total_estudiantes}</div>
          <div class="kpi-sub">{total_especialistas} especialistas</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── Distribución de Casos ─────────────────────────────────────────────────
    g1, g2 = st.columns(2)
    
    with g1:
        st.markdown("### 📊 Distribución de Casos")
        
        labels = ["✅ Al día (0)", "⚠️ Alerta (1-5)", "🚨 Crítico (>5)"]
        values = [estudiantes_ok, estudiantes_alerta, estudiantes_criticos]
        colors = [COLOR_GREEN, COLOR_AMBER, COLOR_RED]
        
        fig_casos = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=.65,
            marker=dict(colors=colors, line=dict(color=COLOR_BG, width=3)),
            textinfo="value+percent",
            textfont=dict(family="JetBrains Mono", size=12, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value} estudiantes<extra></extra>"
        ))
        
        fig_casos.add_annotation(
            text=f"<b>{total_estudiantes}</b><br><span style='font-size:10px'>ESTUDIANTES</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(family="Bebas Neue", size=34, color="#E8E8E8"),
            align="center"
        )
        
        fig_casos.update_layout(
            paper_bgcolor=COLOR_PANEL, plot_bgcolor=COLOR_PANEL,
            font=dict(color="#E8E8E8", family="DM Sans"),
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11), orientation="v", x=1.02),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300
        )
        st.plotly_chart(fig_casos, use_container_width=True)
    
    with g2:
        st.markdown("### 🎯 Top 10 — Mayor Balance de Deudas")
        
        # Obtener el balance más reciente de cada estudiante
        df_ultimo = df_completo.sort_values('MES').groupby('ESTUDIANTE').last().reset_index()
        top_deudas = df_ultimo.nlargest(10, 'BALANCE DE DEUDAS')[['ESTUDIANTE', 'BALANCE DE DEUDAS', 'ESPEC.']]
        top_deudas = top_deudas.set_index('ESTUDIANTE')
        
        fig_top = go.Figure(go.Bar(
            y=top_deudas.index,
            x=top_deudas['BALANCE DE DEUDAS'],
            orientation="h",
            marker=dict(color=COLOR_RED, line=dict(color=COLOR_BG, width=1)),
            text=top_deudas['BALANCE DE DEUDAS'].astype(int),
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=11, color="#E8E8E8"),
            customdata=top_deudas['ESPEC.'],
            hovertemplate="<b>%{y}</b><br>%{x} terapias<br>Especialista: %{customdata}<extra></extra>"
        ))
        
        fig_top.update_layout(
            paper_bgcolor=COLOR_PANEL, plot_bgcolor=COLOR_PANEL,
            font=dict(color="#E8E8E8", family="DM Sans"),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, color="#E8E8E8", tickfont=dict(size=10)),
            margin=dict(l=10, r=60, t=10, b=10),
            height=300,
            bargap=0.2
        )
        st.plotly_chart(fig_top, use_container_width=True)
    
    # ── Análisis por Especialista ─────────────────────────────────────────────
    if len(meses_seleccionados) >= 1:
        st.markdown("---")
        st.markdown("### 👨‍⚕️ Resumen por Especialista")
        
        # Calcular métricas por especialista
        df_ultimo_completo = df_completo.sort_values('MES').groupby('ESTUDIANTE').last().reset_index()
        
        resumen_esp = df_ultimo_completo.groupby('ESPEC.').agg({
            'BALANCE DE DEUDAS': 'sum',
            'ESTUDIANTE': 'count'
        }).rename(columns={'BALANCE DE DEUDAS': 'Deuda Total', 'ESTUDIANTE': 'Casos'})
        
        resumen_esp['Promedio'] = (resumen_esp['Deuda Total'] / resumen_esp['Casos']).round(1)
        resumen_esp = resumen_esp.sort_values('Deuda Total', ascending=False)
        
        col_esp1, col_esp2 = st.columns([2, 1])
        
        with col_esp1:
            fig_esp = go.Figure()
            
            fig_esp.add_trace(go.Bar(
                name="Deuda Total",
                y=resumen_esp.index,
                x=resumen_esp['Deuda Total'],
                orientation="h",
                marker=dict(color=COLOR_RED),
                text=resumen_esp['Deuda Total'].astype(int),
                textposition="outside",
            ))
            
            fig_esp.update_layout(
                paper_bgcolor=COLOR_PANEL, plot_bgcolor=COLOR_PANEL,
                font=dict(color="#E8E8E8", family="DM Sans"),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, color="#E8E8E8", tickfont=dict(size=11)),
                margin=dict(l=10, r=60, t=10, b=10),
                height=max(200, total_especialistas * 60),
                bargap=0.3
            )
            st.plotly_chart(fig_esp, use_container_width=True)
        
        with col_esp2:
            st.markdown("#### Métricas")
            for esp in resumen_esp.index:
                with st.container():
                    st.markdown(f"**{esp}**")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Casos", int(resumen_esp.loc[esp, 'Casos']))
                    with cols[1]:
                        st.metric("Deuda", int(resumen_esp.loc[esp, 'Deuda Total']))
                    with cols[2]:
                        st.metric("Prom", f"{resumen_esp.loc[esp, 'Promedio']:.1f}")
                    st.markdown("---")
    
    # ── Evolución Temporal (si hay múltiples meses) ───────────────────────────
    if len(meses_seleccionados) > 1:
        st.markdown("---")
        st.markdown("### 📈 Evolución Temporal")
        
        # Calcular balance total por mes (suma de balances de estudiantes en ese mes)
        evol_data = []
        for mes in meses_seleccionados:
            df_mes = df_completo[df_completo['MES'] == mes]
            evol_data.append({
                'MES': mes,
                'BALANCE DE DEUDAS': df_mes['BALANCE DE DEUDAS'].sum(),
                'OFRECIDAS REP': df_mes['OFRECIDAS REP'].sum(),
                'DEUDA ADQUIRIDA': df_mes['DEUDA ADQUIRIDA'].sum()
            })
        
        evol = pd.DataFrame(evol_data).set_index('MES')
        
        fig_evol = go.Figure()
        
        fig_evol.add_trace(go.Scatter(
            x=evol.index,
            y=evol['BALANCE DE DEUDAS'],
            mode="lines+markers",
            name="Balance de Deudas",
            line=dict(color=COLOR_RED, width=3),
            marker=dict(size=10, color=COLOR_RED, line=dict(color=COLOR_BG, width=2)),
            fill="tozeroy",
            fillcolor="rgba(255,43,43,0.08)"
        ))
        
        fig_evol.add_trace(go.Scatter(
            x=evol.index,
            y=evol['OFRECIDAS REP'],
            mode="lines+markers",
            name="Reposiciones Ofrecidas",
            line=dict(color=COLOR_GREEN, width=2),
            marker=dict(size=8, color=COLOR_GREEN)
        ))
        
        fig_evol.update_layout(
            paper_bgcolor=COLOR_PANEL, plot_bgcolor=COLOR_PANEL,
            font=dict(color="#E8E8E8", family="DM Sans"),
            xaxis=dict(showgrid=False, color=COLOR_MUTED, tickfont=dict(size=11)),
            yaxis=dict(showgrid=True, gridcolor="#2A2A2A", color=COLOR_MUTED, tickfont=dict(size=11)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_evol, use_container_width=True)
        
        # Análisis de cambios
        if len(meses_seleccionados) >= 2:
            mes_inicial = meses_seleccionados[0]
            mes_final = meses_seleccionados[-1]
            
            deuda_inicial = evol.loc[mes_inicial, 'BALANCE DE DEUDAS']
            deuda_final = evol.loc[mes_final, 'BALANCE DE DEUDAS']
            cambio = deuda_final - deuda_inicial
            pct_cambio = (cambio / deuda_inicial * 100) if deuda_inicial > 0 else 0
            
            if cambio > 0:
                st.error(f"📈 **Tendencia negativa:** Las deudas aumentaron {int(cambio)} terapias ({pct_cambio:+.1f}%) de {mes_inicial} a {mes_final}")
            elif cambio < 0:
                st.success(f"📉 **Tendencia positiva:** Las deudas disminuyeron {int(abs(cambio))} terapias ({pct_cambio:+.1f}%) de {mes_inicial} a {mes_final}")
            else:
                st.info(f"➡️ **Sin cambios:** Las deudas se mantienen estables en {int(deuda_final)} terapias")
    
    # ── Tabla Detallada ───────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📋 Ver Tabla Detallada — Todos los Estudiantes"):
        # Mostrar el estado más reciente de cada estudiante
        df_ultimo_tabla = df_completo.sort_values('MES').groupby('ESTUDIANTE').last().reset_index()
        df_display = df_ultimo_tabla[['ESTUDIANTE', 'ESPEC.', 'DISCIPLINA', 'TERAPIAS ADEUDADAS', 
                                       'OFRECIDAS REP', 'DEUDA ADQUIRIDA', 'BALANCE DE DEUDAS', 'MES']]
        df_display = df_display.sort_values('BALANCE DE DEUDAS', ascending=False)
        
        st.dataframe(
            df_display.style.apply(
                lambda row: [
                    f"background-color: rgba(255,43,43,0.2)" if row['BALANCE DE DEUDAS'] > 5
                    else f"background-color: rgba(255,149,0,0.1)" if row['BALANCE DE DEUDAS'] > 0
                    else ""
                    for _ in row
                ], axis=1
            ),
            use_container_width=True,
            height=400
        )
    
    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f'<p style="font-family:JetBrains Mono;font-size:.65rem;color:#5A5A5A;text-align:center">'
        f'Registro Manual · Actualización Semanal · '
        f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")} · '
        f'Meses analizados: {", ".join(meses_seleccionados)} · '
        f'Deuda total: {int(deuda_total)} terapias</p>',
        unsafe_allow_html=True
    )

else:
    st.warning("👆 **Sube el archivo REGISTRO_VISITAS_PHL.xlsx** en el panel izquierdo para comenzar.")
    st.info("💡 El archivo debe tener una hoja por mes (ENERO, FEBRERO, MARZO, etc.)")
