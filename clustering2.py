import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA 

# 1. Cargar dataset estandarizado para clustering
archivo = "datos_clustering_estandarizados.csv"
df = pd.read_csv(archivo)

print("==============================================")
print("  MODELO DE CLUSTERING - RESIDUOS SÓLIDOS QUITO")
print("==============================================")
print(f"Registros : {len(df)}")
print(f"Variables : {len(df.columns)}")
print("Variables analizadas:")
for columna in df.columns:
    print("-", columna)

x = df.copy()

# 2. Evaluación de K (Inercia y Silhouette de 2 a 6 clusters)
resultados = []
for k in range(2, 7):
    modelo = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )
    etiquetas = modelo.fit_predict(x)
    silhouette = silhouette_score(x, etiquetas)
    inercia = modelo.inertia_
    resultados.append([k, inercia, silhouette])

evaluacion = pd.DataFrame(
    resultados,
    columns=["n_clusters", "inercia", "silhouette"]
)
evaluacion.to_csv("evaluacion_kmeans.csv", index=False)

# 3. Selección del K óptimo (según mayor coeficiente de silhouette)
k_optimo = int(
    evaluacion.loc[evaluacion["silhouette"].idxmax(), "n_clusters"]
)
print(f"\nK óptimo seleccionado según Coeficiente Silhouette: {k_optimo}")

# 4. Ajuste del modelo K-Means final
kmeans = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(x)

# 5. Estadísticas y porcentajes de los clusters
porcentaje_clusters = (
    df["cluster"]
    .value_counts(normalize=True)
    .sort_index() * 100
)
print("\nPorcentaje de registros por cluster:")
print(porcentaje_clusters.round(2))

perfil_clusters = df.groupby("cluster").mean().round(2)
perfil_clusters.to_csv("perfil_clusters.csv", encoding="utf-8-sig")
df.to_csv("dataset_clustering.csv", encoding="utf-8-sig", index=False)

# 6. Gráficos de Evaluación (Inercia / Codo y Silhouette)
plt.figure(figsize=(9, 6))
plt.plot(
    evaluacion["n_clusters"],
    evaluacion["inercia"],
    marker="o",
    color="#1565C0",
    linewidth=2
)
plt.title("Método del Codo (Inercia vs K) - Residuos Quito", fontweight='bold')
plt.xlabel("Número de Clusters (K)")
plt.ylabel("Inercia")
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("22_inercia_vs_k.png", dpi=300)
plt.close()

plt.figure(figsize=(9, 6))
plt.plot(
    evaluacion["n_clusters"],
    evaluacion["silhouette"],
    marker="o",
    color="#1565C0",
    linewidth=2
)
plt.title("Coeficiente Silhouette según Número de Clusters", fontweight='bold')
plt.xlabel("Número de Clusters (K)")
plt.ylabel("Silhouette Score")
plt.xticks(evaluacion["n_clusters"])
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("23_silueta_vs_k.png", dpi=300)
plt.close()

# 7. Reducción de dimensionalidad con PCA (2 componentes) para visualización
pca = PCA(n_components=2, random_state=42)
x_pca = pca.fit_transform(x)
pca_df = pd.DataFrame(x_pca, columns=["pca1", "pca2"])
pca_df["cluster"] = df["cluster"].values

plt.figure(figsize=(10, 6))
for cluster in sorted(pca_df["cluster"].unique()):
    datos = pca_df[pca_df["cluster"] == cluster]
    plt.scatter(
        datos["pca1"],
        datos["pca2"],
        label=f"Cluster {cluster}",
        alpha=0.7,
        edgecolors='black',
        s=50
    )

plt.title("Representación Gráfica de Clusters de Residuos (PCA)", fontweight='bold')
plt.xlabel("Componente Principal 1 (PCA 1)")
plt.ylabel("Componente Principal 2 (PCA 2)")
plt.grid(True, alpha=0.3, linestyle="--")
plt.legend()
plt.tight_layout()
plt.savefig("24_pca_clusters.png", dpi=300)
plt.close()

# 8. Cálculo de Centroides y Exportación
centroides = pd.DataFrame(
    kmeans.cluster_centers_,
    columns=x.columns
)
centroides.index.name = "cluster"
centroides = centroides.round(2)

print("\n==============================================")
print("CENTROIDES FINALES DE LOS CLUSTERS")
print("==============================================")
print(centroides)
centroides.to_csv("centroides.csv", encoding="utf-8-sig")

print("\n==============================================")
print("CLUSTERING DE RESIDUOS FINALIZADO EXITOSAMENTE")
print("==============================================")
print("Archivos CSV generados:")
print(" - evaluacion_kmeans.csv")
print(" - perfil_clusters.csv")
print(" - dataset_clustering.csv")
print(" - centroides.csv")
print("\nGráficos PNG generados:")
print(" - 22_inercia_vs_k.png")
print(" - 23_silueta_vs_k.png")
print(" - 24_pca_clusters.png")