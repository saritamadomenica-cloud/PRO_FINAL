import matplotlib.pyplot as plt
import pandas as pd

archivo = "dataset_residuos_transformado.csv"
df = pd.read_csv(archivo)

# 1. Toneladas generadas por Administración Zonal
plt.figure(figsize=(10, 6))
df.groupby("administracion_zonal")["toneladas_generadas_kg"].sum().sort_values(
    ascending=False
).plot(kind="bar", color="#1565C0")
plt.title("Cantidad de Toneladas Generadas por Administración Zonal")
plt.xlabel("Administración Zonal")
plt.ylabel("Toneladas Generadas (kg)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("5_toneladas_por_administracion_zonal.png", dpi=300)
plt.close()

# 2. Total de denuncias atendidas
plt.figure(figsize=(10, 6))
df.groupby("administracion_zonal")["denuncias_atendidas"].sum().sort_values(
    ascending=False
).plot(kind="bar", color="#FF8F00")
plt.title("Denuncias Atendidas por Administración Zonal")
plt.xlabel("Administración Zonal")
plt.ylabel("Denuncias Atendidas")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("6_denuncias_por_administracion_zonal.png", dpi=300)
plt.close()

# 3. Promedio de denuncias
plt.figure(figsize=(10, 6))
df.groupby("administracion_zonal")["denuncias_atendidas"].mean().sort_values(
    ascending=False
).plot(kind="bar", color="#2E7D32")
plt.title("Promedio de Denuncias por Administración Zonal")
plt.xlabel("Administración Zonal")
plt.ylabel("Promedio de Denuncias")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("7_denuncias_promedio_por_administracion_zonal.png", dpi=300)
plt.close()

# 4. Cumplimiento promedio
plt.figure(figsize=(10, 6))
df.groupby("administracion_zonal")[
    "porcentaje_cumplimiento"
].mean().sort_values(ascending=False).plot(kind="bar", color="#D32F2F")
plt.title("Porcentaje de Cumplimiento Promedio por Administración Zonal")
plt.xlabel("Administración Zonal")
plt.ylabel("Cumplimiento (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("8_cumplimiento_por_administracion_zonal.png", dpi=300)
plt.close()

# 5. Buenas reseñas promedio
plt.figure(figsize=(10, 6))
df.groupby("administracion_zonal")["buenas_resenas"].mean().sort_values(
    ascending=False
).plot(kind="bar", color="#7B1FA2")
plt.title("Buenas Reseñas Promedio por Administración Zonal")
plt.xlabel("Administración Zonal")
plt.ylabel("Buenas Reseñas (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("9_resenas_por_administracion_zonal.png", dpi=300)
plt.close()