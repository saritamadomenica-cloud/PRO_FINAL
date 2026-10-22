import pandas as pd
from sklearn.preprocessing import StandardScaler

# ============================================================
# 1. CARGAR DATASET
# ============================================================

archivo = "dataset_residuos_transformado.csv"

df = pd.read_csv(archivo)

print("==============================================")
print("PREPARACIÓN PARA CLUSTERING - RESIDUOS SÓLIDOS")
print("==============================================")

print(f"Registros originales: {len(df)}")


# ============================================================
# 2. SELECCIONAR VARIABLES PARA CLUSTERING
# ============================================================
# Se usan las variables MENSUALES (toneladas_mensuales y
# denuncias_mensuales) porque ya están homologadas en una misma
# escala temporal. Las columnas originales (toneladas_generadas_kg
# y denuncias_atendidas) mezclan acumulados anuales (2021-2024),
# mensuales (2025) y trimestrales (2026), por lo que no son
# comparables entre registros y además son redundantes
# (r = 0.97 con sus versiones mensuales).
#
# Se excluyen también las variables sin variación en el dataset
# (mes, trimestre, dia, nivel_cumplimiento_num), ya que al
# estandarizarse quedarían en 0 y no aportarían al clustering.

variables_clustering = [
    "toneladas_mensuales",
    "denuncias_mensuales",
    "porcentaje_cumplimiento",
    "buenas_resenas"
]

# Columnas de identificación (NO entran al clustering, pero sirven
# para interpretar los clusters después)
columnas_identificacion = [
    "anio",
    "administracion_zonal",
    "parroquia",
    "zona",
    "tipo_recoleccion",
    "frecuencia"
]

# Verificar qué variables existen
variables_disponibles = [
    columna
    for columna in variables_clustering
    if columna in df.columns
]

identificacion_disponible = [
    columna
    for columna in columnas_identificacion
    if columna in df.columns
]

print("\n==============================================")
print("VARIABLES SELECCIONADAS")
print("==============================================")

for columna in variables_disponibles:
    print("-", columna)

print("\nColumnas de identificación (no se usan en el clustering):")

for columna in identificacion_disponible:
    print("-", columna)


# ============================================================
# 3. CREAR DATASET PARA CLUSTERING
# ============================================================

datos_clustering = df[variables_disponibles].copy()
datos_identificacion = df[identificacion_disponible].copy()


# ============================================================
# 4. CONVERTIR A NUMÉRICO
# ============================================================

for columna in variables_disponibles:

    datos_clustering[columna] = pd.to_numeric(
        datos_clustering[columna],
        errors="coerce"
    )


# ============================================================
# 5. REVISAR VALORES FALTANTES
# ============================================================

print("\n==============================================")
print("VALORES FALTANTES")
print("==============================================")

print(
    datos_clustering.isnull().sum()
)


# ============================================================
# 6. ELIMINAR REGISTROS CON VALORES FALTANTES
# ============================================================

registros_antes = len(datos_clustering)

datos_clustering = datos_clustering.dropna()

# Mantener la identificación alineada con los registros conservados
datos_identificacion = datos_identificacion.loc[datos_clustering.index]

registros_despues = len(datos_clustering)

print("\n==============================================")
print("LIMPIEZA")
print("==============================================")

print(
    f"Registros antes: {registros_antes}"
)

print(
    f"Registros después: {registros_despues}"
)

print(
    f"Registros eliminados: "
    f"{registros_antes - registros_despues}"
)


# ============================================================
# 7. VERIFICAR QUE NINGUNA VARIABLE SEA CONSTANTE
# ============================================================

constantes = [
    columna
    for columna in variables_disponibles
    if datos_clustering[columna].nunique() <= 1
]

if constantes:
    print("\nAVISO: variables constantes (se eliminan):", constantes)
    variables_disponibles = [
        columna
        for columna in variables_disponibles
        if columna not in constantes
    ]
    datos_clustering = datos_clustering[variables_disponibles]


# ============================================================
# 8. ESTANDARIZAR VARIABLES
# ============================================================
# Necesario porque las variables tienen escalas muy distintas
# (toneladas ~1-15, denuncias ~19-285, porcentajes ~75-97).

scaler = StandardScaler()

datos_estandarizados = scaler.fit_transform(
    datos_clustering
)


# ============================================================
# 9. CONVERTIR A DATAFRAME
# ============================================================

df_estandarizado = pd.DataFrame(
    datos_estandarizados,
    columns=variables_disponibles,
    index=datos_clustering.index
)


# ============================================================
# 10. MOSTRAR DATOS ESTANDARIZADOS
# ============================================================

print("\n==============================================")
print("DATOS ESTANDARIZADOS")
print("==============================================")

print(
    df_estandarizado.head()
)


# ============================================================
# 11. COMPROBAR MEDIA Y DESVIACIÓN ESTÁNDAR
# ============================================================
# StandardScaler usa desviación poblacional (ddof=0), por eso
# se comprueba con ddof=0 (con ddof=1 daría ~1.008).

print("\n==============================================")
print("COMPROBACIÓN DE ESTANDARIZACIÓN")
print("==============================================")

print("\nMedia:")
print(
    df_estandarizado.mean().round(4)
)

print("\nDesviación estándar:")
print(
    df_estandarizado.std(ddof=0).round(4)
)


# ============================================================
# 12. GUARDAR DATOS PREPARADOS
# ============================================================

df_estandarizado.to_csv(
    "datos_clustering_estandarizados.csv",
    index=False,
    encoding="utf-8-sig"
)

datos_clustering.to_csv(
    "datos_clustering_originales.csv",
    index=False,
    encoding="utf-8-sig"
)

# Identificación de cada registro (mismo orden de filas que los
# archivos anteriores) para interpretar los clusters al final
datos_identificacion.to_csv(
    "datos_clustering_identificacion.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 13. GUARDAR INFORMACIÓN DE LAS VARIABLES
# ============================================================

informacion_variables = pd.DataFrame({
    "variable": variables_disponibles,
    "media_original": [
        datos_clustering[columna].mean()
        for columna in variables_disponibles
    ],
    "desviacion_original": [
        datos_clustering[columna].std()
        for columna in variables_disponibles
    ],
    "minimo": [
        datos_clustering[columna].min()
        for columna in variables_disponibles
    ],
    "maximo": [
        datos_clustering[columna].max()
        for columna in variables_disponibles
    ]
})

informacion_variables = informacion_variables.round(2)

informacion_variables.to_csv(
    "informacion_variables_clustering.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 14. FINAL
# ============================================================

print("\n==============================================")
print("PREPARACIÓN PARA CLUSTERING FINALIZADA")
print("==============================================")

print("\nArchivos generados:")

print("- datos_clustering_estandarizados.csv")
print("- datos_clustering_originales.csv")
print("- datos_clustering_identificacion.csv")
print("- informacion_variables_clustering.csv")

print("\nLos datos están preparados para aplicar")
print("el algoritmo de clustering (K-Means).")