import pandas as pd
import matplotlib.pyplot as plt

# 1. Cargar dataset transformado
archivo = "dataset_residuos_transformado.csv"
df = pd.read_csv(archivo)

print("==============================================")
print(" ANALISIS DE TEMPORADAS Y GENERACIÓN DE RESIDUOS")
print("==============================================")

# Formato y extracción de datos de fecha
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df["anio"] = df['fecha'].dt.year
df["mes"] = df['fecha'].dt.month
print(f"Cantidad de registros: {len(df)}")

nombre_meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

df["nombre_mes"] = df["mes"].map(nombre_meses)

# ---------------------------------------------------------
# 1. Toneladas Mensuales
# ---------------------------------------------------------
toneladas_mes = df.groupby("mes")["toneladas_mensuales"].sum().reindex(range(1, 13))
toneladas_mes.index = [nombre_meses[i] for i in toneladas_mes.index]

print("\n===============================================")
print("TONELADAS MENSUALES RECOLECTADAS")
print("===============================================")
print(toneladas_mes.round(2))

# ---------------------------------------------------------
# 2. Denuncias Mensuales
# ---------------------------------------------------------
denuncias_mes = df.groupby("mes")["denuncias_mensuales"].sum().reindex(range(1, 13))
denuncias_mes.index = [nombre_meses[i] for i in denuncias_mes.index]

print("\n===============================================")
print("DENUNCIAS MENSUALES ATENDIDAS")
print("===============================================")
print(denuncias_mes.round(2))

# ---------------------------------------------------------
# 3. Cumplimiento Promedio
# ---------------------------------------------------------
cumplimiento_mes = df.groupby("mes")["porcentaje_cumplimiento"].mean().reindex(range(1, 13))
cumplimiento_mes.index = [nombre_meses[i] for i in cumplimiento_mes.index]

print("\n===============================================")
print("PORCENTAJE DE CUMPLIMIENTO PROMEDIO POR MES")
print("===============================================")
print(cumplimiento_mes.round(2))

# ---------------------------------------------------------
# 4. Agrupación Trimestral
# ---------------------------------------------------------
df["trimestre_nom"] = df["fecha"].dt.quarter.map({
    1: "Primer Trimestre",
    2: "Segundo Trimestre",
    3: "Tercer Trimestre",
    4: "Cuarto Trimestre"
})

toneladas_trimestre = df.groupby("trimestre_nom")["toneladas_mensuales"].sum().reindex([
    "Primer Trimestre", "Segundo Trimestre", "Tercer Trimestre", "Cuarto Trimestre"
])

print("\n===============================================")
print("TONELADAS POR TRIMESTRE")
print("===============================================")
print(toneladas_trimestre.round(2))

# ---------------------------------------------------------
# 5. Mes con Mayor y Menor Generación
# ---------------------------------------------------------
mes_mayor_ton = toneladas_mes.idxmax()
cantidad_mayor = toneladas_mes.max()
mes_menor_ton = toneladas_mes.idxmin()
cantidad_menor = toneladas_mes.min()

print("\n===============================================")
print("MES CON MAYOR Y MENOR GENERACIÓN DE RESIDUOS")
print("===============================================")
print(f"Mes con mayor cantidad: {mes_mayor_ton} ({cantidad_mayor:.2f} Tn)")
print(f"Mes con menor cantidad: {mes_menor_ton} ({cantidad_menor:.2f} Tn)")

promedio_mensual = toneladas_mes.mean()
print(f"\nPromedio mensual de toneladas: {promedio_mensual:.2f} Tn")

# ---------------------------------------------------------
# 6. Clasificación de Temporadas
# ---------------------------------------------------------
def clasificar_temporada(valor, promedio):
    if valor > promedio * 1.10:
        return "Alta"
    elif valor < promedio * 0.90:
        return "Baja"
    else:
        return "Media"

temporadas = toneladas_mes.apply(lambda x: clasificar_temporada(x, promedio_mensual))

print("\n===============================================")
print("CLASIFICACIÓN DE TEMPORADAS")
print("===============================================")
print(temporadas)

# ---------------------------------------------------------
# 7. Consolidado de Estacionalidad y Exportación CSV
# ---------------------------------------------------------
estacionalidad = pd.DataFrame({
    "toneladas_mensuales": toneladas_mes,
    "denuncias_totales": denuncias_mes,
    "cumplimiento_promedio": cumplimiento_mes,
    "Temporada": temporadas
})

estacionalidad["variacion_vs_promedio_pct"] = ((estacionalidad["toneladas_mensuales"] - promedio_mensual) / promedio_mensual) * 100

print("\n===============================================")
print("TABLA DE ESTACIONALIDAD DE RESIDUOS")
print("===============================================")
print(estacionalidad.round(2))

# Exportación de archivos CSV
estacionalidad.to_csv("estacionalidad_residuos.csv", encoding="utf-8-sig")
toneladas_trimestre.to_csv("toneladas_trimestre.csv", encoding="utf-8-sig")

# =========================================================
# GENERACIÓN DE GRÁFICOS
# =========================================================

# Gráfico 1: Evolución Toneladas por Mes
plt.figure(figsize=(10, 5))
plt.plot(toneladas_mes.index, toneladas_mes.values, marker="o", color="#1565C0", linewidth=2)
plt.title("Evolución Temporal de Toneladas Recolectadas por Mes", fontweight='bold')
plt.xlabel("Mes")
plt.ylabel("Toneladas Mensuales")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.5, linestyle="--")
plt.tight_layout()
plt.savefig("14_toneladas_por_mes.png", dpi=300)
plt.close()

# Gráfico 2: Evolución Denuncias por Mes
plt.figure(figsize=(10, 5))
plt.plot(denuncias_mes.index, denuncias_mes.values, marker="o", color="#1565C0", linewidth=2)
plt.title("Evolución Temporal de Denuncias Atendidas por Mes", fontweight='bold')
plt.xlabel("Mes")
plt.ylabel("Denuncias Atendidas")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("15_denuncias_por_mes.png", dpi=300)
plt.close()

# Gráfico 3: Cumplimiento por Mes
plt.figure(figsize=(10, 5))
plt.plot(cumplimiento_mes.index, cumplimiento_mes.values, marker="o", color="#1565C0", linewidth=2)
plt.title("Evolución Temporal de Cumplimiento Promedio por Mes", fontweight='bold')
plt.xlabel("Mes")
plt.ylabel("Cumplimiento Promedio (%)")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("16_cumplimiento_por_mes.png", dpi=300)
plt.close()

# Gráfico 4: Toneladas por Trimestre
plt.figure(figsize=(8, 5))
toneladas_trimestre.plot(kind="bar", color="#1565C0")
plt.title("Cantidad de Toneladas Recolectadas por Trimestre", fontweight='bold')
plt.xlabel("Trimestre")
plt.ylabel("Toneladas Mensuales")
plt.xticks(rotation=0)
plt.grid(axis='y', alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("17_toneladas_por_trimestre.png", dpi=300)
plt.close()

# Gráfico 5: Estacionalidad con Código de Colores
colores = []
for temp in temporadas:
    if temp == "Alta":
        colores.append("#D32F2F")  # Rojo
    elif temp == "Baja":
        colores.append("#2E7D32")  # Verde
    else:
        colores.append("#1565C0")  # Azul corporativo

plt.figure(figsize=(10, 5))
plt.bar(toneladas_mes.index, toneladas_mes.values, color=colores)
plt.axhline(promedio_mensual, color="black", linestyle="--", label="Promedio Mensual")
plt.title("Estacionalidad de Generación de Residuos por Mes", fontweight='bold')
plt.xlabel("Mes")
plt.ylabel("Toneladas Mensuales")
plt.xticks(rotation=45)
plt.legend()
plt.grid(axis='y', alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("18_estacionalidad_residuos.png", dpi=300)
plt.close()

print("\n===============================================")
print("PROCESO COMPLETADO EXITOSAMENTE")
print("===============================================")
print("Archivos CSV creados:")
print(" - estacionalidad_residuos.csv")
print(" - toneladas_trimestre.csv")
print("\nGráficos PNG guardados:")
print(" - 14_toneladas_por_mes.png")
print(" - 15_denuncias_por_mes.png")
print(" - 16_cumplimiento_por_mes.png")
print(" - 17_toneladas_por_trimestre.png")
print(" - 18_estacionalidad_residuos.png")