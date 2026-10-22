import pandas as pd
import matplotlib.pyplot as plt

# 1. Cargar dataset transformado
archivo = "dataset_residuos_transformado.csv"
df = pd.read_csv(archivo)

print("==============================================")
print("VARIABLES OPERATIVAS Y CORRELACIONALES")
print("==============================================")

# Selección de variables numéricas para análisis operacional
variables_operativas = [
    "toneladas_generadas_kg",
    "porcentaje_cumplimiento",
    "denuncias_atendidas",
    "buenas_resenas",
    "toneladas_mensuales",
    "denuncias_mensuales",
    "nivel_cumplimiento_num"
]

variables_disponibles = [
    columna for columna in df.columns if columna in variables_operativas
]

print("\n===============================================")
print("VARIABLES ANALIZADAS")
print("===============================================")
for columna in variables_disponibles:
    print(f"- {columna}")

# Matriz de Correlaciones
correlaciones = df[variables_disponibles].corr()

print("\n===============================================")
print("MATRIZ DE CORRELACIONES")
print("===============================================")
print(correlaciones.round(2))

# Guardar matriz de correlaciones
correlaciones.round(4).to_csv("matriz_correlaciones.csv", encoding="utf-8-sig")

# Correlación específica con las denuncias mensuales
if "denuncias_mensuales" in correlaciones.columns:
    correlacion_denuncias = correlaciones["denuncias_mensuales"].sort_values(ascending=False)
    print("\n===============================================")
    print("CORRELACIONES CON DENUNCIAS MENSUALES")
    print("===============================================")
    print(correlacion_denuncias.round(2))

# Cálculo de correlaciones clave
corr_toneladas_denuncias = df["toneladas_mensuales"].corr(df["denuncias_mensuales"])
corr_cumplimiento_resenas = df["porcentaje_cumplimiento"].corr(df["buenas_resenas"])
corr_cumplimiento_denuncias = df["porcentaje_cumplimiento"].corr(df["denuncias_mensuales"])

print("\n===============================================")
print("CORRELACIONES CLAVE CALCULADAS")
print("===============================================")
print(f"Toneladas vs Denuncias Mensuales : {corr_toneladas_denuncias:.2f}")
print(f"Cumplimiento vs Buenas Reseñas   : {corr_cumplimiento_resenas:.2f}")
print(f"Cumplimiento vs Denuncias        : {corr_cumplimiento_denuncias:.2f}")

# Función para interpretar la fuerza y dirección del coeficiente
def interpretar_correlacion(valor):
    valor_abs = abs(valor)
    if valor_abs >= 0.80:
        fuerza = "Muy fuerte"
    elif valor_abs >= 0.60:
        fuerza = "Fuerte"
    elif valor_abs >= 0.40:
        fuerza = "Moderada"
    elif valor_abs >= 0.20:
        fuerza = "Débil"
    else:
        fuerza = "Muy débil o inexistente"

    if valor > 0:
        direccion = "positiva"
    elif valor < 0:
        direccion = "negativa"
    else:
        direccion = "sin dirección"

    return f"{fuerza} y {direccion}"

print("\n===============================================")
print("INTERPRETACIÓN DE CORRELACIONES")
print("===============================================")
print(f"Toneladas vs Denuncias Mensuales : {interpretar_correlacion(corr_toneladas_denuncias)}")
print(f"Cumplimiento vs Buenas Reseñas   : {interpretar_correlacion(corr_cumplimiento_resenas)}")
print(f"Cumplimiento vs Denuncias        : {interpretar_correlacion(corr_cumplimiento_denuncias)}")

# Construcción de la tabla resumen de relaciones
relaciones = pd.DataFrame({
    "variable_1": ["toneladas_mensuales", "porcentaje_cumplimiento", "porcentaje_cumplimiento"],
    "variable_2": ["denuncias_mensuales", "buenas_resenas", "denuncias_mensuales"],
    "correlacion": [corr_toneladas_denuncias, corr_cumplimiento_resenas, corr_cumplimiento_denuncias]
})

relaciones["correlacion"] = relaciones["correlacion"].round(4)
relaciones["interpretacion"] = relaciones["correlacion"].apply(interpretar_correlacion)

print("\n===============================================")
print("TABLA RESUMEN DE RELACIONES")
print("===============================================")
print(relaciones)

# Guardar resumen en CSV
relaciones.to_csv("relaciones_variables.csv", index=False, encoding="utf-8-sig")

# =========================================================
# GENERACIÓN DE GRÁFICOS DE DISPERSIÓN (SCATTER PLOTS)
# =========================================================

# Gráfico 1: Toneladas vs Denuncias Mensuales
plt.figure(figsize=(10, 6))
plt.scatter(df["toneladas_mensuales"], df["denuncias_mensuales"], alpha=0.6, color="#1565C0")
plt.xlabel("Toneladas Mensuales")
plt.ylabel("Denuncias Mensuales")
plt.title("Relación entre Toneladas Mensuales y Denuncias Atendidas", fontweight='bold')
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("21_relacion_toneladas_denuncias.png", dpi=300)
plt.close()

# Gráfico 2: Cumplimiento vs Buenas Reseñas
plt.figure(figsize=(10, 6))
plt.scatter(df["porcentaje_cumplimiento"], df["buenas_resenas"], alpha=0.6, color="#1565C0")
plt.xlabel("Porcentaje de Cumplimiento (%)")
plt.ylabel("Buenas Reseñas (%)")
plt.title("Relación entre Cumplimiento Operativo y Buenas Reseñas", fontweight='bold')
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("20_relacion_cumplimiento_resenas.png", dpi=300)
plt.close()

# Gráfico 3: Cumplimiento vs Denuncias Atendidas
plt.figure(figsize=(10, 6))
plt.scatter(df["porcentaje_cumplimiento"], df["denuncias_mensuales"], alpha=0.6, color="#1565C0")
plt.xlabel("Porcentaje de Cumplimiento (%)")
plt.ylabel("Denuncias Mensuales")
plt.title("Relación entre Cumplimiento Operativo y Denuncias Mensuales", fontweight='bold')
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("19_relacion_cumplimiento_denuncias.png", dpi=300)
plt.close()

print("\n===============================================")
print("ANÁLISIS DE CORRELACIÓN COMPLETADO")
print("===============================================")
print("Archivos CSV generados:")
print(" - matriz_correlaciones.csv")
print(" - relaciones_variables.csv")
print("\nGráficos PNG generados:")
print(" - 21_relacion_toneladas_denuncias.png")
print(" - 20_relacion_cumplimiento_resenas.png")
print(" - 19_relacion_cumplimiento_denuncias.png")