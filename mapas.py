import pandas as pd
import folium
from folium.plugins import HeatMap

# ============================================================
# 1. CARGAR DATASET
# ============================================================

archivo = "dataset_residuos_transformado.csv"

df = pd.read_csv(archivo)

print("==============================================")
print("ANÁLISIS GEOGRÁFICO DE RESIDUOS SÓLIDOS - QUITO")
print("==============================================")

print(f"Registros: {len(df)}")


# ============================================================
# 2. COORDENADAS POR ADMINISTRACIÓN ZONAL
# ============================================================
# Coordenadas aproximadas de la parroquia representativa de cada
# administración zonal (latitud, longitud).

coordenadas = {
    "Eugenio Espejo": [-0.1750, -78.4850],   # Iñaquito
    "Eloy Alfaro": [-0.2530, -78.5280],      # Solanda
    "Quitumbe": [-0.2985, -78.5480],         # Quitumbe
    "La Delicia": [-0.1050, -78.4930],       # Cotocollao
    "Calderón": [-0.0980, -78.4150],         # Calderón
    "Manuela Sáenz": [-0.2200, -78.5120],    # Centro Histórico
    "Los Chillos": [-0.2900, -78.4780],      # Conocoto
    "Tumbaco": [-0.2120, -78.4000]           # Tumbaco
}

centro_mapa = [-0.1950, -78.4800]   # Centro aproximado de Quito


# ------------------------------------------------------------
# Función para crear el mapa base (sin claves de API)
# ------------------------------------------------------------
# OpenStreetMap bloquea archivos abiertos desde el disco (403) y
# CARTO ahora exige API key, por eso se usan mosaicos de Esri.
# El botón de capas (arriba a la derecha) permite cambiar de fondo.

def crear_mapa():

    mapa_base = folium.Map(
        location=centro_mapa,
        zoom_start=11,
        tiles=None
    )

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
        name="Calles (Esri)"
    ).add_to(mapa_base)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
        name="Satélite (Esri)",
        show=False
    ).add_to(mapa_base)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
        name="Gris claro (Esri)",
        show=False
    ).add_to(mapa_base)

    folium.LayerControl().add_to(mapa_base)

    return mapa_base



# ============================================================
# 3. REGISTROS POR ADMINISTRACIÓN ZONAL
# ============================================================

print("\n==============================================")
print("ADMINISTRACIONES ZONALES")
print("==============================================")

print(
    df["administracion_zonal"].value_counts()
)


# ============================================================
# 4. RESUMEN POR ADMINISTRACIÓN ZONAL
# ============================================================
# Se usan promedios mensuales (y no sumas) porque las columnas
# *_mensuales ya están homologadas y los años 2025-2026 tienen
# más registros que 2021-2024, lo que distorsionaría una suma.

zonas = (
    df.groupby("administracion_zonal")
    .agg(
        parroquia=("parroquia", "first"),
        zona=("zona", "first"),
        toneladas_mensuales_promedio=("toneladas_mensuales", "mean"),
        denuncias_mensuales_promedio=("denuncias_mensuales", "mean"),
        cumplimiento_promedio=("porcentaje_cumplimiento", "mean"),
        resenas_promedio=("buenas_resenas", "mean")
    )
    .reset_index()
)

columnas_numericas = [
    "toneladas_mensuales_promedio",
    "denuncias_mensuales_promedio",
    "cumplimiento_promedio",
    "resenas_promedio"
]

zonas[columnas_numericas] = zonas[columnas_numericas].round(2)

print("\n==============================================")
print("RESUMEN POR ADMINISTRACIÓN ZONAL")
print("==============================================")

print(zonas)


# ============================================================
# 5. VERIFICAR ZONAS SIN COORDENADAS
# ============================================================

zonas_sin_coordenadas = [
    zona
    for zona in zonas["administracion_zonal"]
    if zona not in coordenadas
]

print("\n==============================================")
print("ZONAS SIN COORDENADAS")
print("==============================================")

if zonas_sin_coordenadas:
    for zona in zonas_sin_coordenadas:
        print("-", zona)
else:
    print("Todas las zonas tienen coordenadas")


# ============================================================
# 6. AGREGAR LATITUD Y LONGITUD
# ============================================================

zonas["latitud"] = zonas["administracion_zonal"].map(
    lambda x: coordenadas.get(x, [None, None])[0]
)

zonas["longitud"] = zonas["administracion_zonal"].map(
    lambda x: coordenadas.get(x, [None, None])[1]
)

zonas_mapa = zonas.dropna(
    subset=["latitud", "longitud"]
).copy()


# ============================================================
# 7. GUARDAR DATOS GEOGRÁFICOS
# ============================================================

zonas.to_csv(
    "zonas_geograficas.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. MAPA DE BURBUJAS
# ============================================================
# Tamaño del círculo = toneladas mensuales promedio
# Color = nivel de cumplimiento (verde: sobre el promedio,
# naranja: bajo el promedio)

mapa = crear_mapa()

toneladas_max = zonas_mapa["toneladas_mensuales_promedio"].max()
cumplimiento_medio = zonas_mapa["cumplimiento_promedio"].mean()

for _, fila in zonas_mapa.iterrows():

    zona_admin = fila["administracion_zonal"]
    toneladas = fila["toneladas_mensuales_promedio"]
    denuncias = fila["denuncias_mensuales_promedio"]
    cumplimiento = fila["cumplimiento_promedio"]
    resenas = fila["resenas_promedio"]

    radio = max(
        6,
        min(
            30,
            toneladas / toneladas_max * 30
        )
    )

    color = "green" if cumplimiento >= cumplimiento_medio else "orange"

    popup = f"""
    <b>Administración Zonal:</b> {zona_admin}<br>
    <b>Parroquia:</b> {fila["parroquia"]} ({fila["zona"]})<br>
    <b>Toneladas mensuales (prom.):</b> {toneladas:,.2f}<br>
    <b>Denuncias mensuales (prom.):</b> {denuncias:,.2f}<br>
    <b>Cumplimiento (prom.):</b> {cumplimiento:.2f}%<br>
    <b>Buenas reseñas (prom.):</b> {resenas:.2f}%
    """

    folium.CircleMarker(
        location=[
            fila["latitud"],
            fila["longitud"]
        ],
        radius=radio,
        color=color,
        popup=folium.Popup(popup, max_width=300),
        tooltip=zona_admin,
        fill=True,
        fill_color=color,
        fill_opacity=0.7
    ).add_to(mapa)

mapa.save("zonas_mapa.html")


# ============================================================
# 9. MAPA DE CALOR DE TONELADAS
# ============================================================

datos_calor = []

for _, fila in zonas_mapa.iterrows():

    datos_calor.append([
        fila["latitud"],
        fila["longitud"],
        fila["toneladas_mensuales_promedio"]
    ])

mapa_calor = crear_mapa()

HeatMap(
    datos_calor,
    radius=30,
    blur=20,
    min_opacity=0.4
).add_to(mapa_calor)

mapa_calor.save("mapa_calor_toneladas.html")


# ============================================================
# 10. FINAL
# ============================================================

print("\n==============================================")
print("MAPAS GENERADOS")
print("==============================================")

print("\nArchivos generados:")

print("- zonas_geograficas.csv")
print("- zonas_mapa.html")
print("- mapa_calor_toneladas.html")

print("\nAbre en tu navegador:")

print("- zonas_mapa.html")
print("- mapa_calor_toneladas.html")