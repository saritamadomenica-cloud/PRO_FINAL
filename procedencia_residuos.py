import pandas as pd
import matplotlib.pyplot as plt

# 1. Cargar dataset transformado
archivo = "dataset_residuos_transformado.csv"
df = pd.read_csv(archivo)

# Asegurar formato de fechas
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

# ---------------------------------------------------------
# Gráfico 1: Evolución Temporal de Toneladas Mensuales
# ---------------------------------------------------------
plt.figure(figsize=(10, 5))
df_tiempo = df.groupby('fecha')['toneladas_mensuales'].sum().reset_index()
plt.plot(df_tiempo['fecha'], df_tiempo['toneladas_mensuales'], marker='o', color='#1565C0', linewidth=2)
plt.title("Evolución Temporal de Toneladas Mensuales Recolectadas", fontsize=12, fontweight='bold')
plt.xlabel("Fecha")
plt.ylabel("Toneladas Mensuales")
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("10_evolucion_toneladas_mensuales.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# Gráfico 2: Comparativa de Toneladas: Fin de Semana vs. Día Laborable
# ---------------------------------------------------------
plt.figure(figsize=(7, 5))
df_fds = df.groupby('fin_de_semana')['toneladas_mensuales'].mean().reset_index()
bars = plt.bar(df_fds['fin_de_semana'], df_fds['toneladas_mensuales'], color='#1565C0')
plt.title("Promedio de Toneladas Mensuales: Fin de Semana vs. Laborables", fontsize=12, fontweight='bold')
plt.xlabel("¿Es Fin de Semana?")
plt.ylabel("Promedio Toneladas Mensuales")

# Agregar etiquetas de valor sobre cada barra
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f}", ha='center', va='bottom')

plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("11_comparativa_fin_de_semana.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# Gráfico 3: Distribución por Frecuencia de Recolección
# ---------------------------------------------------------
plt.figure(figsize=(8, 5))
frecuencia_counts = df['frecuencia'].value_counts()
frecuencia_counts.plot(kind='bar', color='#1565C0')
plt.title("Distribución de Registros según Frecuencia de Recolección", fontsize=12, fontweight='bold')
plt.xlabel("Frecuencia")
plt.ylabel("Cantidad de Registros")
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("12_distribucion_frecuencia.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# Gráfico 4: Relación entre Porcentaje de Cumplimiento y Buenas Reseñas
# ---------------------------------------------------------
plt.figure(figsize=(8, 5))
plt.scatter(df['porcentaje_cumplimiento'], df['buenas_resenas'], color='#1565C0', alpha=0.7, edgecolors='black')
plt.title("Relación entre Cumplimiento Operativo y Buenas Reseñas", fontsize=12, fontweight='bold')
plt.xlabel("Porcentaje de Cumplimiento (%)")
plt.ylabel("Buenas Reseñas (%)")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("13_relacion_cumplimiento_resenas.png", dpi=300)
plt.close()

print("¡Nuevos gráficos generados con éxito")