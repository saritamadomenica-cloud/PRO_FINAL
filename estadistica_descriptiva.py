import pandas as pd
import matplotlib.pyplot as plt

# Cargar el dataset de residuos
archivo = "dataset_residuos_transformado.csv"
df = pd.read_csv(archivo)

print("==============================================")
print("ESTADÍSTICA DESCRIPTIVA")
print("==============================================")
print(f"Registros : {len(df)}")
print(f"Variables : {len(df.columns)}")

print("\n==============================================")
print("Informacion General")
print("==============================================")
print(df.info())

print("\n==============================================")
print("Estadistica Descriptiva")
print("==============================================")
estadisticas = df.describe()
print(estadisticas)

print("\n==============================================")
print("Mediana")
print("==============================================")
columnas_numericas = [
    "toneladas_generadas_kg",
    "porcentaje_cumplimiento",
    "denuncias_atendidas",
    "buenas_resenas",
    "anio",
    "mes",
    "trimestre",
    "dia",
    "dia_semana_num",
    "fin_de_semana_num"
]

for columna in columnas_numericas:
    if columna in df.columns:
        print(f"{columna}: {df[columna].median():.2f}")

print("\n==============================================")
print("Promedio")
print("==============================================")
for columna in columnas_numericas:
    if columna in df.columns:
        print(f"{columna}: {df[columna].mean():.2f}")

print("\n==============================================")
print("Moda")
print("==============================================")
columnas_categoricas = [
    "provincia",
    "canton",
    "administracion_zonal",
    "parroquia",
    "zona",
    "tipo_recoleccion",
    "frecuencia",
    "categoria_toneladas",
    "nivel_cumplimiento"
]

for columna in columnas_categoricas:
    if columna in df.columns:
        moda = df[columna].mode()
        if not moda.empty:
            print(f"{columna}: {moda.iloc[0]}")

print("\n==============================================")
print("Toneladas por Zona")
print("==============================================")
toneladas_por_zona = df.groupby("zona")["toneladas_generadas_kg"].sum().sort_values(ascending=False)
print(toneladas_por_zona)

print("\n==============================================")
print("Cumplimiento Promedio por Zona (%)")
print("==============================================")
cumplimiento_por_zona = df.groupby("zona")["porcentaje_cumplimiento"].mean().sort_values(ascending=False)
print(cumplimiento_por_zona)

print("\n==============================================")
print("Denuncias Atendidas por Zona")
print("==============================================")
denuncias_por_zona = df.groupby("zona")["denuncias_atendidas"].sum().sort_values(ascending=False)
print(denuncias_por_zona)

print("\n==============================================")
print("Tipo de Recolección")
print("==============================================")
tipo_recoleccion = df["tipo_recoleccion"].value_counts()
print(tipo_recoleccion)

# Resumen Estadístico Numérico Correcto
cols_num_presentes = [c for c in columnas_numericas if c in df.columns]
resumen = pd.DataFrame({
    "promedio": df[cols_num_presentes].mean(),
    "mediana": df[cols_num_presentes].median(),
    "minimo": df[cols_num_presentes].min(),
    "maximo": df[cols_num_presentes].max(),
    "desviacion_estandar": df[cols_num_presentes].std()
})

print("\n==============================================")
print("RESUMEN ESTADÍSTICO")
print("==============================================")
print(resumen)

# Guardar reportes en CSV
resumen.to_csv("resumen_estadistico.csv", encoding="utf-8-sig", index=True)
toneladas_por_zona.to_csv("toneladas_por_zona.csv", encoding="utf-8-sig", index=True)
cumplimiento_por_zona.to_csv("cumplimiento_por_zona.csv", encoding="utf-8-sig", index=True)

# Gráfica 1: Toneladas por Zona
plt.figure(figsize=(8, 5))
toneladas_por_zona.plot(kind="bar", color="#1565C0")
plt.title("Toneladas Generadas por Zona")
plt.xlabel("Zona")
plt.ylabel("Toneladas Generadas (kg)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("1_toneladas_por_zona.png", dpi=300)

# Gráfica 2: Cumplimiento por Zona
plt.figure(figsize=(8, 5))
cumplimiento_por_zona.plot(kind="bar", color="#2E7D32")
plt.title("Porcentaje de Cumplimiento Promedio por Zona")
plt.xlabel("Zona")
plt.ylabel("Porcentaje de Cumplimiento (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("2_cumplimiento_por_zona.png", dpi=300)

# Gráfica 3: Histograma de Toneladas Generadas
plt.figure(figsize=(8, 5))
plt.hist(df["toneladas_generadas_kg"], bins=20, color="#1565C0", edgecolor="black", alpha=0.8)
plt.title("Distribución de Toneladas Generadas (kg)")
plt.xlabel("Toneladas Generadas (kg)")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.savefig("3_distribucion_toneladas_generadas.png", dpi=300)

# Gráfica 4: Pie Chart Tipo de Recolección
plt.figure(figsize=(7, 5))
tipo_recoleccion.plot(kind="pie", autopct='%1.1f%%', colors=["#1565C0", "#2E7D32", "#FF8F00", "#D32F2F"])
plt.title("Distribución por Tipo de Recolección")
plt.ylabel("")
plt.tight_layout()
plt.savefig("4_distribucion_tipo_recoleccion.png", dpi=300)

print("\n==============================================")
print("Análisis exploratorio completado.")
print("==============================================")