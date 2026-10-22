import pandas as pd
import numpy as np

# 1. Carga del archivo inicial
df = pd.read_csv("dataset_residuos_limpio.csv")

print("==============================================")
print("TRANSFORMACIÓN Y REPARACIÓN DE DATOS")
print("==============================================")
print(f"Registros iniciales: {len(df)}")
print(f"Variables iniciales: {len(df.columns)}")

# 2. Tratamiento y extracción de fechas
df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
df["trimestre"] = df["fecha"].dt.quarter
df["dia"] = df["fecha"].dt.day
df["dia_semana_num"] = df["fecha"].dt.dayofweek

# Indicador numérico de fin de semana (1 = Fin de semana, 0 = Día laborable)
df["fin_de_semana_num"] = np.where(df["dia_semana_num"] >= 5, 1, 0)
df["fin_de_semana"] = np.where(df["dia_semana_num"] >= 5, "SI", "NO")

print("\nVariables de fechas creadas correctamente.")

# 3. Estandarización de columnas de texto
columnas_texto = [
    "provincia",        
    "canton",
    "administracion_zonal",
    "parroquia",
    "zona",
    "tipo_recoleccion",
    "frecuencia",
    "periodo_datos"
]

for columna in columnas_texto:
    if columna in df.columns:
        df[columna] = (
            df[columna]
            .astype(str)
            .str.strip()
            .str.title()
        )
        print(f"Categorías estandarizadas: {columna}")

# 4. Ajuste de Coherencia Numérica (Escala temporal y unidades homogéneas)
# Se homologan los pesos a toneladas métricas mensuales
condiciones_anios = [
    df["anio"] <= 2024,  # Acumulado anual en kg
    df["anio"] == 2025,  # Acumulado mensual en kg
    df["anio"] >= 2026   # Acumulado trimestral en kg
]

calculo_toneladas_mensuales = [
    (df["toneladas_generadas_kg"] / 1000.0) / 12.0,
    df["toneladas_generadas_kg"] / 1000.0,
    (df["toneladas_generadas_kg"] / 1000.0) / 3.0
]

calculo_denuncias_mensuales = [
    df["denuncias_atendidas"] / 12.0,
    df["denuncias_atendidas"].astype(float),
    df["denuncias_atendidas"] / 3.0
]

df["toneladas_mensuales"] = np.select(condiciones_anios, calculo_toneladas_mensuales, default=df["toneladas_generadas_kg"])
df["denuncias_mensuales"] = np.select(condiciones_anios, calculo_denuncias_mensuales, default=df["denuncias_atendidas"])

# 5. Funciones de Clasificación (Texto y Numérica)
def clasificar_toneladas(valor):
    if valor < 5.0:
        return "Bajo"
    elif 5.0 <= valor < 10.0:
        return "Medio"
    else:
        return "Alto"

df["categoria_toneladas"] = df["toneladas_mensuales"].apply(clasificar_toneladas)

def clasificar_cumplimiento(valor):
    if valor < 50:
        return "Bajo"
    elif 50 <= valor < 80:
        return "Medio"
    else:
        return "Alto"

df["nivel_cumplimiento"] = df["porcentaje_cumplimiento"].apply(clasificar_cumplimiento)

# Codificación ordinal numérica para nivel de cumplimiento (1=Bajo, 2=Medio, 3=Alto)
mapeo_cumplimiento_num = {"Bajo": 1, "Medio": 2, "Alto": 3}
df["nivel_cumplimiento_num"] = df["nivel_cumplimiento"].map(mapeo_cumplimiento_num)

# 6. Estandarización de categorías textuales específicas
df["tipo_recoleccion"] = df["tipo_recoleccion"].replace({
    "Recolección De Residuos Sólidos": "Recolección de residuos sólidos",
    "Recolección De Residuos Sólidos Y Orgánicos": "Recolección de residuos sólidos y orgánicos",
    "Recolección De Residuos Sólidos Y Orgánicos Y Voluminosos": "Recolección de residuos sólidos, orgánicos y voluminosos",
    "Recolección De Residuos Sólidos Y Voluminosos": "Recolección de residuos sólidos y voluminosos"
})

df["frecuencia"] = df["frecuencia"].replace({
    "Diaria": "Diaria",
    "Semanal": "Semanal",
    "Quincenal": "Quincenal",
    "Mensual": "Mensual"
})

df["administracion_zonal"] = df["administracion_zonal"].replace({
    "Administración Zonal 1": "Administración Zonal 1",
    "Administración Zonal 2": "Administración Zonal 2",
    "Administración Zonal 3": "Administración Zonal 3",
    "Administración Zonal 4": "Administración Zonal 4",
    "Administración Zonal 5": "Administración Zonal 5",
    "Administración Zonal 6": "Administración Zonal 6"
})

# Ordenar cronológicamente por fecha
df = df.sort_values(by="fecha").reset_index(drop=True)

print("\n==============================================")
print("DATASET TRANSFORMADO Y COHERENTE")
print("==============================================")
print(f"Registros finales: {len(df)}")
print(f"Variables finales: {len(df.columns)}")

# Exportar a CSV corregido
archivo_salida = "dataset_residuos_transformado.csv"
df.to_csv(archivo_salida, index=False, encoding="utf-8")

print("\n===============================================")
print("TRANSFORMACIÓN Y REPARACIÓN COMPLETA")
print("===============================================")
print(f"Archivo guardado como: {archivo_salida}")