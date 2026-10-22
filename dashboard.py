import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import HeatMap
import branca.colormap as cm

# ============================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard residuos sólidos - Quito",
    page_icon=":material/recycling:",
    layout="wide"
)


# ============================================================
# 1.b TRADUCCIÓN DE LA INTERFAZ (MENÚ DE STREAMLIT) AL ESPAÑOL
# ============================================================
# Streamlit no ofrece una opción de idioma ni en .streamlit/config.toml
# ni en st.set_page_config: los textos del menú (Rerun, Clear cache,
# Print, Record screen, Settings, System/Light/Dark, etc.) están fijos
# en inglés. Para mostrarlos en español se inyecta un script que
# traduce esos textos en el DOM a medida que el menú se construye.

st.html(
    """
    <div style="display:none">
    <script>
    (function () {
        const traducciones = {
            "Rerun": "Volver a ejecutar",
            "Auto rerun": "Reejecución automática",
            "Clear cache": "Limpiar caché",
            "Print": "Imprimir",
            "Record screen": "Grabar pantalla",
            "Record a screencast": "Grabar pantalla",
            "Stop recording": "Detener grabación",
            "Settings": "Configuración",
            "About": "Acerca de",
            "Report a bug": "Reportar un error",
            "Get help": "Obtener ayuda",
            "System": "Sistema",
            "Light": "Claro",
            "Dark": "Oscuro",
            "Deploy": "Implementar",
            "Manage app": "Administrar aplicación"
        };

        const selectores = [
            '[data-testid="stMainMenuList"] *',
            '[data-testid="stAppDeployButton"] *',
            '[data-testid="stToolbar"] *'
        ].join(",");

        function traducirNodosDeTexto(elemento) {
            elemento.childNodes.forEach(function (hijo) {
                if (hijo.nodeType === Node.TEXT_NODE) {
                    const original = hijo.nodeValue.trim();
                    if (Object.prototype.hasOwnProperty.call(traducciones, original)) {
                        hijo.nodeValue = hijo.nodeValue.replace(
                            original,
                            traducciones[original]
                        );
                    }
                }
            });
        }

        function traducirMenu() {
            document.querySelectorAll(selectores).forEach(function (nodo) {
                traducirNodosDeTexto(nodo);
            });

            document
                .querySelectorAll('[data-testid="stMainMenuButton"]')
                .forEach(function (el) {
                    el.setAttribute("aria-label", "Menú principal");
                });

            document
                .querySelectorAll('[data-testid="stThemeSwitcher"]')
                .forEach(function (el) {
                    el.setAttribute("aria-label", "Tema");
                });
        }

        let pendiente = false;

        function programarTraduccion() {
            if (pendiente) {
                return;
            }
            pendiente = true;
            requestAnimationFrame(function () {
                pendiente = false;
                traducirMenu();
            });
        }

        const observador = new MutationObserver(programarTraduccion);

        observador.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true
        });

        traducirMenu();
    })();
    </script>
    </div>
    """,
    unsafe_allow_javascript=True,
)


st.title(
    "Dashboard de análisis de residuos sólidos de Quito",
    icon=":material/recycling:"
)

st.markdown(
    "Análisis de toneladas generadas, denuncias, cumplimiento "
    "y reseñas por administración zonal."
)


# ============================================================
# 2. FUNCIONES AUXILIARES
# ============================================================
# Compatibles con versiones antiguas y nuevas de Streamlit
# (use_container_width fue reemplazado por width="stretch").

def mostrar_grafico(figura, alt):
    try:
        st.plotly_chart(figura, width="stretch", alt=alt)
    except TypeError:
        st.plotly_chart(figura, use_container_width=True)


def mostrar_tabla(tabla, alt):
    try:
        st.dataframe(
            tabla,
            width="stretch",
            hide_index=True,
            alt=alt
        )
    except TypeError:
        st.dataframe(tabla, use_container_width=True)


@st.cache_data(ttl="1h")
def cargar_dataset(ruta):
    datos = pd.read_csv(ruta)
    datos["fecha"] = pd.to_datetime(
        datos["fecha"],
        errors="coerce"
    )
    return datos


# ------------------------------------------------------------
# Coordenadas aproximadas de la parroquia representativa de cada
# administración zonal (latitud, longitud).
# ------------------------------------------------------------

COORDENADAS_ZONALES = {
    "Eugenio Espejo": [-0.1750, -78.4850],   # Iñaquito
    "Eloy Alfaro": [-0.2530, -78.5280],      # Solanda
    "Quitumbe": [-0.2985, -78.5480],         # Quitumbe
    "La Delicia": [-0.1050, -78.4930],       # Cotocollao
    "Calderón": [-0.0980, -78.4150],         # Calderón
    "Manuela Sáenz": [-0.2200, -78.5120],    # Centro Histórico
    "Los Chillos": [-0.2900, -78.4780],      # Conocoto
    "Tumbaco": [-0.2120, -78.4000]           # Tumbaco
}

CENTRO_QUITO = [-0.1950, -78.4800]

# Indicadores disponibles para los mapas.
# Cada uno define la columna del resumen y su etiqueta legible.
INDICADORES_MAPA = {
    "Toneladas": ("toneladas", "Toneladas mensuales (prom.)"),
    "Denuncias": ("denuncias", "Denuncias mensuales (prom.)"),
    "Cumplimiento": ("cumplimiento", "Cumplimiento (%)"),
    "Buenas reseñas": ("resenas", "Buenas reseñas (%)")
}


def resumen_zonal(datos):
    resumen = (
        datos.groupby("administracion_zonal")
        .agg(
            parroquia=("parroquia", "first"),
            zona=("zona", "first"),
            toneladas=("toneladas_mensuales", "mean"),
            denuncias=("denuncias_mensuales", "mean"),
            cumplimiento=("porcentaje_cumplimiento", "mean"),
            resenas=("buenas_resenas", "mean")
        )
        .reset_index()
    )

    resumen["latitud"] = resumen["administracion_zonal"].map(
        lambda zonal: COORDENADAS_ZONALES.get(zonal, [None, None])[0]
    )
    resumen["longitud"] = resumen["administracion_zonal"].map(
        lambda zonal: COORDENADAS_ZONALES.get(zonal, [None, None])[1]
    )

    return resumen.dropna(subset=["latitud", "longitud"])


def crear_mapa_base():
    # OpenStreetMap bloquea archivos locales (403) y CARTO exige API
    # key, por eso se usan mosaicos de Esri. El botón de capas permite
    # cambiar el fondo del mapa.
    mapa = folium.Map(
        location=CENTRO_QUITO,
        zoom_start=11,
        tiles=None
    )

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
        name="Calles (Esri)"
    ).add_to(mapa)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
        name="Satélite (Esri)",
        show=False
    ).add_to(mapa)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
        name="Gris claro (Esri)",
        show=False
    ).add_to(mapa)

    folium.LayerControl().add_to(mapa)

    return mapa


def construir_mapa_zonas(resumen, columna, etiqueta):
    mapa = crear_mapa_base()

    valores = resumen[columna]
    minimo = float(valores.min())
    maximo = float(valores.max())
    rango = maximo - minimo

    escala = cm.LinearColormap(
        colors=["#e5f5e0", "#74c476", "#238b45", "#00441b"],
        vmin=minimo,
        vmax=maximo if rango else minimo + 1,
        caption=etiqueta
    )

    for _, fila in resumen.iterrows():

        valor = float(fila[columna])
        proporcion = (valor - minimo) / rango if rango else 0.5
        radio = 8 + proporcion * 24
        color = escala(valor)

        popup = (
            f"<b>{fila['administracion_zonal']}</b><br>"
            f"Parroquia: {fila['parroquia']} ({fila['zona']})<br>"
            f"Toneladas mensuales (prom.): {fila['toneladas']:,.2f}<br>"
            f"Denuncias mensuales (prom.): {fila['denuncias']:,.2f}<br>"
            f"Cumplimiento (prom.): {fila['cumplimiento']:,.2f}%<br>"
            f"Buenas reseñas (prom.): {fila['resenas']:,.2f}%"
        )

        folium.CircleMarker(
            location=[fila["latitud"], fila["longitud"]],
            radius=radio,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup, max_width=300),
            tooltip=(
                f"{fila['administracion_zonal']} · {fila['zona']} · "
                f"{etiqueta}: {valor:,.2f}"
            )
        ).add_to(mapa)

    escala.add_to(mapa)

    return mapa


def construir_mapa_calor(resumen, columna):
    mapa = crear_mapa_base()

    valores = resumen[columna]
    minimo = float(valores.min())
    maximo = float(valores.max())
    rango = maximo - minimo

    datos_calor = [
        [
            fila["latitud"],
            fila["longitud"],
            0.5 + 0.5 * ((fila[columna] - minimo) / rango if rango else 1)
        ]
        for _, fila in resumen.iterrows()
    ]

    HeatMap(
        datos_calor,
        radius=55,
        blur=35,
        min_opacity=0.1,
        max=1,
        gradient={
            "0.2": "#2e7d32",
            "0.4": "#66bb6a",
            "0.6": "#ffd54f",
            "0.8": "#fb8c00",
            "1.0": "#d32f2f"
        }
    ).add_to(mapa)

    return mapa


# ============================================================
# 3. CARGAR DATASET
# ============================================================

archivo = "dataset_residuos_transformado.csv"

df = cargar_dataset(archivo)


# ============================================================
# 4. FILTROS
# ============================================================

st.sidebar.header("Filtros", icon=":material/tune:")

zonales = sorted(
    df["administracion_zonal"]
    .dropna()
    .unique()
)

zonas = sorted(
    df["zona"]
    .dropna()
    .unique()
)

recolecciones = sorted(
    df["tipo_recoleccion"]
    .dropna()
    .unique()
)

anios = sorted(
    df["anio"]
    .dropna()
    .unique()
)

st.session_state.setdefault("filtro_zonal", zonales)
st.session_state.setdefault("filtro_zona", zonas)
st.session_state.setdefault("filtro_recoleccion", recolecciones)
st.session_state.setdefault("filtro_anio", anios)


def restablecer_filtros():
    st.session_state.filtro_zonal = zonales
    st.session_state.filtro_zona = zonas
    st.session_state.filtro_recoleccion = recolecciones
    st.session_state.filtro_anio = anios


zonal_seleccionada = st.sidebar.multiselect(
    "Administración zonal",
    zonales,
    key="filtro_zonal"
)

zona_seleccionada = st.sidebar.pills(
    "Zona (urbana / rural)",
    zonas,
    selection_mode="multi",
    key="filtro_zona"
)

recoleccion_seleccionada = st.sidebar.multiselect(
    "Tipo de recolección",
    recolecciones,
    key="filtro_recoleccion"
)

anio_seleccionado = st.sidebar.pills(
    "Año",
    anios,
    selection_mode="multi",
    key="filtro_anio"
)

st.sidebar.button(
    "Restablecer filtros",
    icon=":material/restart_alt:",
    width="stretch",
    on_click=restablecer_filtros
)

df_filtrado = df[
    df["administracion_zonal"].isin(zonal_seleccionada)
    & df["zona"].isin(zona_seleccionada)
    & df["tipo_recoleccion"].isin(recoleccion_seleccionada)
    & df["anio"].isin(anio_seleccionado)
].copy()

if df_filtrado.empty:
    st.warning(
        "No hay datos con los filtros seleccionados.",
        icon=":material/filter_alt_off:"
    )
    st.stop()


# ============================================================
# 4.b SERIE ANUAL (para indicadores y evolución temporal)
# ============================================================
# Se usan promedios de las variables mensuales porque son
# comparables entre años (las columnas originales mezclan
# acumulados anuales, mensuales y trimestrales).

serie_anual = (
    df_filtrado.groupby("anio")
    .agg(
        toneladas=("toneladas_mensuales", "mean"),
        denuncias=("denuncias_mensuales", "mean"),
        cumplimiento=("porcentaje_cumplimiento", "mean"),
        resenas=("buenas_resenas", "mean")
    )
    .sort_index()
)


def tarjeta_kpi(columna, etiqueta, valor, es_porcentaje=False):
    serie = serie_anual[columna]

    if len(serie) >= 2:
        anio_referencia = int(serie.index[-2])
        if es_porcentaje:
            delta = round(serie.iloc[-1] - serie.iloc[-2], 1)
        else:
            previo = serie.iloc[-2]
            delta = (
                round((serie.iloc[-1] - previo) / previo * 100, 1)
                if previo
                else None
            )
        unidad = "pp" if es_porcentaje else "%"
        descripcion = (
            f"vs. {anio_referencia} ({unidad})"
            if delta is not None
            else None
        )
    else:
        delta = None
        descripcion = None

    st.metric(
        etiqueta,
        valor,
        delta=delta,
        delta_description=descripcion,
        chart_data=serie.tolist() if len(serie) >= 2 else None,
        chart_type="line",
        border=True,
        height="stretch"
    )


# ============================================================
# 5. INDICADORES PRINCIPALES
# ============================================================

st.header("Indicadores principales", icon=":material/insights:")

toneladas_promedio = df_filtrado["toneladas_mensuales"].mean()
denuncias_promedio = df_filtrado["denuncias_mensuales"].mean()
cumplimiento_promedio = df_filtrado["porcentaje_cumplimiento"].mean()
resenas_promedio = df_filtrado["buenas_resenas"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    tarjeta_kpi(
        "toneladas",
        "Toneladas mensuales (promedio)",
        f"{toneladas_promedio:,.1f} t"
    )

with col2:
    tarjeta_kpi(
        "denuncias",
        "Denuncias mensuales (promedio)",
        f"{denuncias_promedio:,.0f}"
    )

with col3:
    tarjeta_kpi(
        "cumplimiento",
        "Cumplimiento (promedio)",
        f"{cumplimiento_promedio:.1f}%",
        es_porcentaje=True
    )

with col4:
    tarjeta_kpi(
        "resenas",
        "Buenas reseñas (promedio)",
        f"{resenas_promedio:.1f}%",
        es_porcentaje=True
    )


# ============================================================
# 6. TONELADAS POR ADMINISTRACIÓN ZONAL
# ============================================================

st.header("Residuos por administración zonal", icon=":material/scale:")

with st.container(border=True):
    st.subheader("Toneladas mensuales promedio")
    st.caption(
        "Promedio de toneladas mensuales generadas "
        "por cada administración zonal."
    )

    toneladas_zonal = (
        df_filtrado.groupby("administracion_zonal")["toneladas_mensuales"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_toneladas = px.bar(
        toneladas_zonal,
        x="administracion_zonal",
        y="toneladas_mensuales",
        labels={
            "administracion_zonal": "Administración zonal",
            "toneladas_mensuales": "Toneladas mensuales (prom.)"
        },
        color="toneladas_mensuales"
    )

    mostrar_grafico(
        fig_toneladas,
        alt=(
            "Barras de toneladas mensuales promedio por "
            "administración zonal, ordenadas de mayor a menor"
        )
    )


# ============================================================
# 7. DENUNCIAS Y TIPO DE RECOLECCIÓN
# ============================================================

st.header("Denuncias y tipo de recolección", icon=":material/report:")

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):
        st.subheader("Denuncias mensuales promedio")

        denuncias_zonal = (
            df_filtrado.groupby("administracion_zonal")["denuncias_mensuales"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_denuncias = px.bar(
            denuncias_zonal,
            x="administracion_zonal",
            y="denuncias_mensuales",
            labels={
                "administracion_zonal": "Administración zonal",
                "denuncias_mensuales": "Denuncias mensuales (prom.)"
            },
            color="denuncias_mensuales"
        )

        mostrar_grafico(
            fig_denuncias,
            alt=(
                "Barras de denuncias mensuales promedio por "
                "administración zonal, ordenadas de mayor a menor"
            )
        )

with col2:

    with st.container(border=True):
        st.subheader("Tipo de recolección")

        tipo_recoleccion = (
            df_filtrado.groupby("tipo_recoleccion")
            .size()
            .reset_index(name="registros")
        )

        fig_recoleccion = px.pie(
            tipo_recoleccion,
            values="registros",
            names="tipo_recoleccion",
            hole=0.45
        )

        mostrar_grafico(
            fig_recoleccion,
            alt="Gráfico circular de la distribución de registros por tipo de recolección"
        )


# ============================================================
# 8. EVOLUCIÓN TEMPORAL
# ============================================================
# Las fechas del dataset corresponden a un registro por año
# (1 de enero), por eso la evolución se muestra por año.

st.header("Evolución anual", icon=":material/trending_up:")

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):
        st.subheader("Toneladas mensuales promedio")

        fig_temporal = px.line(
            serie_anual.reset_index(),
            x="anio",
            y="toneladas",
            markers=True,
            labels={
                "anio": "Año",
                "toneladas": "Toneladas mensuales (prom.)"
            }
        )

        fig_temporal.update_xaxes(dtick=1)

        mostrar_grafico(
            fig_temporal,
            alt="Evolución anual de las toneladas mensuales promedio"
        )

with col2:

    with st.container(border=True):
        st.subheader("Cumplimiento promedio")

        fig_cumplimiento_anual = px.line(
            serie_anual.reset_index(),
            x="anio",
            y="cumplimiento",
            markers=True,
            labels={
                "anio": "Año",
                "cumplimiento": "Cumplimiento (%)"
            }
        )

        fig_cumplimiento_anual.update_xaxes(dtick=1)

        mostrar_grafico(
            fig_cumplimiento_anual,
            alt="Evolución anual del porcentaje de cumplimiento promedio"
        )


# ============================================================
# 9. CUMPLIMIENTO Y RESEÑAS
# ============================================================

st.header("Cumplimiento y satisfacción", icon=":material/verified:")

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):
        st.subheader("Cumplimiento y buenas reseñas por zonal")

        calidad_zonal = (
            df_filtrado.groupby("administracion_zonal")
            .agg(
                Cumplimiento=("porcentaje_cumplimiento", "mean"),
                Resenas=("buenas_resenas", "mean")
            )
            .reset_index()
            .melt(
                id_vars="administracion_zonal",
                var_name="indicador",
                value_name="porcentaje"
            )
        )

        fig_calidad = px.bar(
            calidad_zonal,
            x="administracion_zonal",
            y="porcentaje",
            color="indicador",
            barmode="group",
            labels={
                "administracion_zonal": "Administración zonal",
                "porcentaje": "Porcentaje",
                "indicador": "Indicador"
            }
        )

        mostrar_grafico(
            fig_calidad,
            alt=(
                "Barras agrupadas de cumplimiento y buenas reseñas "
                "por administración zonal"
            )
        )

with col2:

    with st.container(border=True):
        st.subheader("Relación cumplimiento y reseñas")

        fig_relacion = px.scatter(
            df_filtrado,
            x="porcentaje_cumplimiento",
            y="buenas_resenas",
            color="administracion_zonal",
            labels={
                "porcentaje_cumplimiento": "Cumplimiento (%)",
                "buenas_resenas": "Buenas reseñas (%)",
                "administracion_zonal": "Administración zonal"
            }
        )

        mostrar_grafico(
            fig_relacion,
            alt=(
                "Diagrama de dispersión entre cumplimiento y buenas "
                "reseñas, con un color por administración zonal"
            )
        )


# ============================================================
# 10. PERFIL URBANO / RURAL Y FRECUENCIA
# ============================================================

st.header(
    "Perfil por zona y frecuencia de recolección",
    icon=":material/route:"
)

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):
        st.subheader("Distribución de toneladas mensuales")

        fig_hist = px.histogram(
            df_filtrado,
            x="toneladas_mensuales",
            nbins=15,
            color="zona",
            labels={
                "toneladas_mensuales": "Toneladas mensuales",
                "count": "Cantidad",
                "zona": "Zona"
            }
        )

        mostrar_grafico(
            fig_hist,
            alt="Histograma de la distribución de toneladas mensuales por zona"
        )

with col2:

    with st.container(border=True):
        st.subheader("Toneladas promedio por frecuencia")

        frecuencia = (
            df_filtrado.groupby("frecuencia")["toneladas_mensuales"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_frecuencia = px.bar(
            frecuencia,
            x="frecuencia",
            y="toneladas_mensuales",
            labels={
                "frecuencia": "Frecuencia de recolección",
                "toneladas_mensuales": "Toneladas mensuales (prom.)"
            },
            color="toneladas_mensuales"
        )

        mostrar_grafico(
            fig_frecuencia,
            alt="Barras de toneladas mensuales promedio por frecuencia de recolección"
        )


# ============================================================
# 11. ANÁLISIS GEOGRÁFICO
# ============================================================

st.header("Análisis geográfico", icon=":material/public:")

resumen_geo = resumen_zonal(df_filtrado)

if resumen_geo.empty:
    st.info(
        "No hay administraciones zonales con coordenadas para "
        "los filtros seleccionados.",
        icon=":material/map:"
    )
else:
    indicador_mapa = st.segmented_control(
        "Indicador de los mapas",
        options=list(INDICADORES_MAPA.keys()),
        default="Toneladas",
        key="mapa_indicador"
    )

    if indicador_mapa is None:
        indicador_mapa = "Toneladas"

    columna_mapa, etiqueta_mapa = INDICADORES_MAPA[indicador_mapa]

    pestana_zonas, pestana_calor = st.tabs(
        ["Mapa de zonas", "Mapa de calor"]
    )

    with pestana_zonas:
        st.caption(
            f"Tamaño y color de cada burbuja: {etiqueta_mapa.lower()}. "
            "Pasa el cursor o haz clic en un punto para ver el detalle "
            "y si la zona es urbana o rural."
        )
        st.iframe(
            construir_mapa_zonas(
                resumen_geo, columna_mapa, etiqueta_mapa
            ).get_root().render(),
            height=540,
            alt=(
                f"Mapa de burbujas de {etiqueta_mapa.lower()} "
                "por administración zonal de Quito"
            )
        )

    with pestana_calor:
        st.caption(
            "Intensidad del mapa de calor: "
            f"{etiqueta_mapa.lower()} por administración zonal."
        )
        st.iframe(
            construir_mapa_calor(
                resumen_geo, columna_mapa
            ).get_root().render(),
            height=540,
            alt=(
                f"Mapa de calor de {etiqueta_mapa.lower()} "
                "por administración zonal de Quito"
            )
        )


# ============================================================
# 12. PERFILES (CLUSTERING)
# ============================================================
# Requiere un archivo "dataset_clustering.csv" que contenga una
# columna "cluster" (resultado del algoritmo de clustering).

st.header("Perfiles de zonas (clustering)", icon=":material/hub:")

archivo_cluster = "dataset_clustering.csv"

try:
    df_cluster = pd.read_csv(archivo_cluster)

    if "cluster" in df_cluster.columns:

        with st.container(border=True):
            st.subheader("Cantidad de registros por cluster")

            clusters = (
                df_cluster["cluster"]
                .value_counts()
                .sort_index()
                .reset_index()
            )

            clusters.columns = ["cluster", "registros"]
            clusters["cluster"] = clusters["cluster"].astype(str)

            fig_cluster = px.bar(
                clusters,
                x="cluster",
                y="registros",
                labels={
                    "cluster": "Cluster",
                    "registros": "Registros"
                }
            )

            mostrar_grafico(
                fig_cluster,
                alt="Barras de la cantidad de registros en cada cluster"
            )

        variables_perfil = [
            columna
            for columna in [
                "toneladas_mensuales",
                "denuncias_mensuales",
                "porcentaje_cumplimiento",
                "buenas_resenas"
            ]
            if columna in df_cluster.columns
        ]

        if variables_perfil:
            with st.container(border=True):
                st.subheader("Promedio de cada variable por cluster")

                perfil = (
                    df_cluster.groupby("cluster")[variables_perfil]
                    .mean()
                    .round(2)
                    .reset_index()
                )
                mostrar_tabla(
                    perfil,
                    alt="Tabla con el promedio de cada variable por cluster"
                )

    else:
        st.write(
            "El archivo dataset_clustering.csv no contiene "
            "la columna 'cluster'."
        )

except FileNotFoundError:
    st.info(
        "No se encontró dataset_clustering.csv. "
        "Ejecuta primero el algoritmo de clustering.",
        icon=":material/info:"
    )


# ============================================================
# 13. DATOS Y DESCARGA
# ============================================================

st.header("Datos filtrados", icon=":material/table_view:")

with st.expander(f"Ver tabla de datos ({len(df_filtrado)} registros)"):
    mostrar_tabla(
        df_filtrado,
        alt="Tabla con los registros de residuos sólidos filtrados"
    )

csv = df_filtrado.to_csv(
    index=False
).encode(
    "utf-8-sig"
)

st.download_button(
    label="Descargar datos filtrados (CSV)",
    data=csv,
    file_name="datos_residuos_filtrados.csv",
    mime="text/csv",
    icon=":material/download:"
)

st.caption(
    "Proyecto de Ciencia y Análisis de Datos | "
    "Dashboard de análisis de residuos sólidos realizado por: "
    "Saritama Domenica, "
    "Nuñez Oscar, "
    "Chamorro Erika"
)
