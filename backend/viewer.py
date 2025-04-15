import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def visualize_occupancy_data(file_path):
    """
    Charge et visualise les données d'occupation à partir d'un fichier NPZ et génère un plot interactif avec Plotly.

    Args:
        file_path (str): Chemin vers le fichier NPZ contenant les données d'occupation.

    Returns:
        str: Contenu HTML du graphique interactif Plotly.
    """
    try:
        # Chargement des données
        data = np.load(file_path)
        obstacle_grid = data["obstacle_grid"]
        min_x = data["min_x"]
        max_x = data["max_x"]
        min_y = data["min_y"]
        max_y = data["max_y"]

        # Vérification et conversion des données pour Plotly
        if obstacle_grid.dtype != np.float64:
            obstacle_grid = obstacle_grid.astype(float)

        # Inverser l'axe Y pour correspondre à l'orientation de matplotlib
        obstacle_grid = np.flipud(obstacle_grid)

        # Création de la visualisation interactive avec Plotly
        fig = go.Figure(data=go.Heatmap(
            z=obstacle_grid,
            colorscale='Reds',
            colorbar=dict(title="Occupation")
        ))

        # Mise à jour des axes et du titre
        fig.update_layout(
            title="Visualisation interactive des obstacles",
            xaxis=dict(
                title=f"X ({min_x:.2f} to {max_x:.2f})",
                range=[min_x, max_x],
                autorange=True  # Activer l'autoscale pour l'axe X
            ),
            yaxis=dict(
                title=f"Y ({min_y:.2f} to {max_y:.2f})",
                range=[min_y, max_y],
                autorange=True  # Activer l'autoscale pour l'axe Y
            ),
            height=600,
            width=800
        )

        # Retourne le contenu HTML du graphique
        return fig.to_html(full_html=False)

    except Exception as e:
        print(f"Erreur lors de la visualisation: {str(e)}")
        return None

def generate_plot_preview(grid, bounds, output_path):
    """
    Génère et sauvegarde une preview PNG d'une matrice d'occupation sans échelle, titre, ou annotations.

    Args:
        grid (np.ndarray): Matrice d'occupation.
        bounds (tuple): Limites de la bounding box (min_x, max_x, min_y, max_y).
        output_path (str): Chemin où sauvegarder l'image PNG.
    """
    plt.figure(figsize=(8, 8))
    plt.imshow(grid, cmap='Greys', origin='lower')
    plt.axis('off')  # Supprime les axes
    plt.gca().set_xticks([])  # Supprime les ticks sur l'axe X
    plt.gca().set_yticks([])  # Supprime les ticks sur l'axe Y
    plt.gca().set_frame_on(False)  # Supprime le cadre autour du graphique
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0)  # Supprime les marges
    plt.close()

# Exemple d'utilisation
if __name__ == "__main__":
    file_path = "data/NPZ-output/occupancy_data.npz"
    result = visualize_occupancy_data(file_path)
    if result:
        print("Graphique interactif généré avec succès.")
    else:
        print("Échec de la visualisation.")
