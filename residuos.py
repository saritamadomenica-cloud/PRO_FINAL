from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent

archivo = BASE / "Análisis_Residuos_Sólidos.csv"
archivo_salida = BASE / "dataset_residuos_limpio.csv"

df = pd.read_csv(archivo)

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)

print("==============================================")
print("LIMPIEZA Y PREPARACIÓN DE DATOS")
print("==============================================")
print("\nDataset cargado correctamente.")
print(f"Filas: {df.shape[0]}")
print(f"Columnas: {df.shape[1]}")

print("\n==============================================")
print("INFORMACIÓN INICIAL")
print("==============================================")
df.info()

print("\n==============================================")
print("VALORES NULOS")
print("==============================================")

nulos = df.isnull().sum()
print(nulos)

print("\nTotal de valores nulos:")
print(df.isnull().sum().sum())

print("\n==============================================")
print("REGISTROS DUPLICADOS")
print("==============================================")

duplicados = df.duplicated().sum()
print(f"Cantidad de registros duplicados: {duplicados}")

if duplicados > 0:
    df = df.drop_duplicates()
    print(f"Se eliminaron {duplicados} registros duplicados.")
else:
    print("No existen registros duplicados.")

columnas_numericas = [
    "ano",
    "toneladas_generadas_kg",
    "porcentaje_cumplimiento",
    "denuncias_atendidas",
    "buenas_resenas"
]

for columna in columnas_numericas:
    if columna in df.columns:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

        mediana = df[columna].median()

        if pd.isna(mediana):
            df[columna] = df[columna].fillna(0)
        else:
            df[columna] = df[columna].fillna(mediana)

columnas_categoricas = [
    "trimestre",
    "mes",
    "provincia",
    "canton",
    "administracion_zonal",
    "parroquia",
    "zona",
    "tipo_recoleccion",
    "frecuencia",
    "periodo_datos"
]

for columna in columnas_categoricas:
    if columna in df.columns:
        df[columna] = df[columna].fillna(
            "Desconocido"
        )

if "fecha" in df.columns:
    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce"
    )

if "toneladas_generadas_kg" in df.columns:
    df.loc[
        df["toneladas_generadas_kg"] <= 0,
        "toneladas_generadas_kg"
    ] = 0

if "denuncias_atendidas" in df.columns:
    df.loc[
        df["denuncias_atendidas"] <= 0,
        "denuncias_atendidas"
    ] = 0

if "porcentaje_cumplimiento" in df.columns:
    df.loc[
        (df["porcentaje_cumplimiento"] < 0) | (df["porcentaje_cumplimiento"] > 100),
        "porcentaje_cumplimiento"
    ] = df["porcentaje_cumplimiento"].median()

if "buenas_resenas" in df.columns:
    df.loc[
        (df["buenas_resenas"] < 0) | (df["buenas_resenas"] > 100),
        "buenas_resenas"
    ] = df["buenas_resenas"].median()

print("\n==============================================")
print("CALIDAD FINAL DE LOS DATOS")
print("==============================================")

print(f"Registros finales: {len(df)}")
print(f"Variables finales: {len(df.columns)}")

print("\nValores nulos:")
print(df.isnull().sum())

print("\nDuplicados:")
print(df.duplicated().sum())

df.to_csv(
    archivo_salida,
    index=False,
    encoding="utf-8-sig"
)

print("\n==============================================")
print("PROCESO FINALIZADO")
print("==============================================")

print(
    f"Dataset limpio guardado como: {archivo_salida}"
)