import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  # Añade esta importación al inicio
from datetime import datetime
from PIL import Image  # Añade esta importación al inicio


# Configuración de la página
st.set_page_config(layout="wide", page_title="Dashboard de Certificaciones TI" ,page_icon="📊")

# Cargar datos desde el Excel generado
@st.cache_data

def load_data():
    return pd.read_excel("certificaciones_gerentes.xlsx")  # Asegúrate de tener el archivo en la misma carpeta
df = load_data()



# Sidebar con filtros
st.sidebar.header("🔍 Filtros")
gerentes_seleccionados = st.sidebar.multiselect(
    "Seleccionar Gerente(s)",
    options=sorted(df['Gerente'].unique()),
    default=df['Gerente'].unique()
)

status_seleccionados = st.sidebar.multiselect(
    "Seleccionar Status",
    options=sorted(df['Status'].unique()),
    default=["APPROVE"]  # Por defecto muestra solo aprobados
)

# Filtrar datos
df_filtrado = df[
    (df['Gerente'].isin(gerentes_seleccionados)) &
    (df['Status'].isin(status_seleccionados))
]

# Mostrar datos filtrados
logo_path = "ibm.jpg"  # Cambia esto por la ruta de tu logo
logo = Image.open(logo_path)

# Ajuste de tamaño (proporcional al ancho del sidebar)
col1, col2 = st.columns([1, 4])
with col1:
    st.image(logo, width=150)  # Streamlit ajustará la altura automáticamente

with col2:
    st.header("📊 Dashboard de Certificaciones TI",  divider="blue")
st.subheader("Recursos Certificados")
st.dataframe(df_filtrado.style.applymap(lambda x: 'background-color: #e6f3ff' if x == True else '', 
                                      subset=['AWS', 'Google', 'IBM', 'Microsoft', 'Red Hat']),
            use_container_width=True,
            height=300)

# Gráficas
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔝 Certificaciones Más Demandadas")
    cert_counts = df[['AWS', 'Google', 'IBM', 'Microsoft', 'Red Hat']].sum().sort_values(ascending=False)
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.barplot(x=cert_counts.index, y=cert_counts.values, palette="viridis")
    plt.xticks(rotation=45)
    ax1.set_ylabel("Total")
    st.pyplot(fig1)

with col2:
    st.subheader("✅ Distribución de Aprobaciones")
    df_approve = df[df['Status'] == 'APPROVE']
    cert_approve = df_approve[['AWS', 'Google', 'IBM', 'Microsoft', 'Red Hat']].sum().reset_index()
    cert_approve.columns = ['Certificación', 'Total']
    
    fig_pie = px.pie(
        cert_approve,
        names='Certificación',
        values='Total',
        color='Certificación',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.3  # Opcional: agrega un hueco para estilo dona
    )
    
    # Personalizar interactividad
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>Total: %{value}"
    )
    
    fig_pie.update_layout(
        clickmode='event+select',  # Permite seleccionar elementos
        showlegend=True,
        margin=dict(l=20, r=20, t=30, b=0)
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

# KPIs
st.subheader("📌 Métricas Clave")
total_recursos = len(df_filtrado)
total_certificaciones = df_filtrado[['AWS', 'Google', 'IBM', 'Microsoft', 'Red Hat']].sum().sum()
aprob_rate = (len(df_filtrado[df_filtrado['Status'] == 'APPROVE']) / len(df_filtrado)) * 100 if len(df_filtrado) > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Recursos Filtrados", total_recursos)
kpi2.metric("Certificaciones Filtradas", total_certificaciones)
kpi3.metric("Tasa de Aprobación", f"{aprob_rate:.1f}%")

# Instrucciones
st.sidebar.markdown("""
**Nota:** 
- Los datos son los generados en el primer prompt (10 gerentes con recursos aleatorios).
- Fechas de obtención: Q1-Q3 2023.
- Filtros aplicables en tiempo real.
""")
