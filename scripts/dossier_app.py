import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="La Batalla del Movimiento - Dossier",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
    }
    .stExpander {
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Proyecto: La Batalla")
st.sidebar.markdown("**Museo Paleontológico Egidio Feruglio**")
nav = st.sidebar.radio("Navegación", ["Concepto General", "La Ciencia (Ameghinichnus)", "Diseño del Espacio", "Storyboarding Mapping", "Respuesta Fundación"])

# --- PAGE: Concepto General ---
if nav == "Concepto General":
    st.title("🛡️ La Batalla del Movimiento")
    st.subheader("Ichnología & Paleobiología del Movimiento en el Jurásico de la Patagonia")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### El Desafío de lo Inanimado
        ¿Cómo estudiamos el movimiento si los fósiles son inanimados? Esta es la pregunta central de nuestra propuesta. 
        A través de las huellas (*Icnitas*), transformamos una superficie de piedra en una ventana al comportamiento animal de hace 165 millones de años.
        
        **Componentes Clave:**
        - **Pieza Central**: Laja de 5 metros de extensión (incorporación estratégica).
        - **Tecnología**: Mapeo digital (Mapping) y reconstrucción 3D.
        - **Narrativa**: Un día registrado para siempre; lluvia, ceniza y huellas.
        """)
        
    with col2:
        st.info("**Estado del Proyecto:** Diseño conceptual avanzado con validación científica de la Dra. Veronika Krapovikas y técnica de Ethel Denning.")

# --- PAGE: La Ciencia ---
elif nav == "La Ciencia (Ameghinichnus)":
    st.title("🔬 El Rigor Científico")
    
    tab1, tab2 = st.columns(2)
    
    with tab1:
        st.metric(label="Huellas Registradas en Laja", value="> 2000", delta="Nuevo Hallazgo")
        st.markdown("""
        **Ameghinichnus patagonicus**
        - **Tipo**: Pequeño mammaliaforme (primitivo).
        - **Dimensiones**: ~100-200g (tamaño hámster).
        - **Mecánica**: Tronco de 6cm. Miembros anteriores erguidos, miembros posteriores esparrancados.
        """)
        
    with tab2:
        st.markdown("""
        **Comportamientos Dinámicos:**
        - **Caminata**: Secuencia rítmica mano-pie.
        - **Salto**: Transición en la misma rastrillada (indicador de huida o agilidad).
        - **Evidencia Ambiental**: Gotas de lluvia y marcas de cola preservadas en ceniza.
        """)

# --- PAGE: Diseño del Espacio ---
elif nav == "Diseño del Espacio":
    st.title("📐 Conceptualización del Espacio")
    
    # 3D Simulation of the 5m Slab
    x = np.linspace(0, 5, 50)
    y = np.linspace(0, 1.5, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X*2) * np.cos(Y*2) * 0.05  # Slight texture
    
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Earth', showscale=False)])
    fig.update_layout(
        title='Prototipo: Laja de 5 Metros (Scan 3D)',
        scene = dict(
            xaxis_title='Largo (m)',
            yaxis_title='Ancho (m)',
            zaxis=dict(nticks=4, range=[-0.2,0.2]),
        ),
        width=900, height=600
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Instalación Física:**
        - Laja horizontal elevada.
        - Aro de madera perimetral (Pantalla de Mapping).
        - Patas 3D interactivas.
        """)
    with col2:
        st.markdown("""
        **Experiencia Digital:**
        - Mapping sincronizado con el sonido.
        - Monitor interactivo (Comprado) con perfiles científicos.
        """)

# --- PAGE: Storyboarding Mapping ---
elif nav == "Storyboarding Mapping":
    st.title("🎭 Storyboard: El Suelo como Testigo")
    
    st.write("La secuencia de mapping narra la cronología capturada en la piedra:")
    
    with st.container():
        st.markdown("### 1. Atmósfera: Bosque Jurásico")
        st.write("El mapping proyecta sobre el aro y la laja un bosque de Araucarias. Los animales aparecen caminado en bucles sobre las huellas reales.")
        
        st.markdown("### 2. El Evento: La Lluvia")
        st.write("Efecto de lluvia y ceniza. El mapping resalta cómo el suelo se ablanda (distorsión de las huellas proyectadas).")
        
        st.markdown("### 3. Acción: El Salto")
        st.write("Los animales digitales 'saltan'. La iluminación sigue el sendero de las huellas de Ameghinichnus que muestran transiciones de velocidad.")
        
        st.markdown("### 4. Conclusión: El Refugio")
        st.write("Los animales se esconden bajo las raíces fosilizadas. ElMapping se desvanece dejando solo la piedra iluminada, conectando el pasado con el presente.")

# --- PAGE: Respuesta Fundación ---
elif nav == "Respuesta Fundación":
    st.title("📄 Dossier para Fundación Williams")
    st.info("Utilice estos puntos clave para la comunicación oficial.")
    
    st.subheader("Argumento del Valor Agregado")
    st.markdown("""
    1.  **Hito Museográfico**: La inclusión de una pieza de 5m posiciona la muestra como referente internacional.
    2.  **Optimización Técnica**: El uso de fondos para personal permitió capturar este hallazgo que antes era logísticamente imposible.
    3.  **Tecnología de Vanguardia**: El mapping sobre madera es una innovación estética y pedagógica.
    """)
    
    st.button("Copiar Modelo de Respuesta a Portapapeles (Simulado)")
    st.code("""
Asunto: Avance de Proyecto - La Batalla del Movimiento - MEF

Estimados, informamos que hemos incorporado una laja de 5m escaneada en campo (Dra. Krapovickas).
Esta pieza central, no contemplada originalmente, eleva el rigor científico y el impacto visual. 
El presupuesto se ha optimizado para integrar este hallazgo mediante mapping digital.
    """, language="markdown")

st.sidebar.markdown("---")
st.sidebar.caption("v1.0 - Dossier Interactivo")
