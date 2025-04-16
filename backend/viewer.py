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
        print(f"Chargement des données pour la visualisation: {file_path}")
        data = np.load(file_path, allow_pickle=True)
        obstacle_grid = data["obstacle_grid"]
        min_x = data["min_x"]
        max_x = data["max_x"]
        min_y = data["min_y"]
        max_y = data["max_y"]
        
        print(f"Dimensions de la grille d'obstacles: {obstacle_grid.shape}")
        print(f"Nombre d'obstacles: {np.sum(obstacle_grid)}")
        print(f"Limites: X({min_x}, {max_x}), Y({min_y}, {max_y})")

        # Vérification et conversion des données pour Plotly
        if obstacle_grid.dtype != np.float64:
            obstacle_grid = obstacle_grid.astype(float)

        # Création de la visualisation interactive avec Plotly
        fig = go.Figure()

        # Ajout de la heatmap des obstacles
        fig.add_trace(go.Heatmap(
            z=obstacle_grid,
            colorscale='Reds',
            showscale=False  # Cette ligne désactive la barre de couleur
        ))

        # Définir les couleurs pour chaque type de POI
        poi_colors = {
            'start': 'blue',
            'end': 'green'
        }

        # Ajout des POIs s'ils existent
        if 'poi_x' in data:
            poi_x = data['poi_x']
            poi_y = data['poi_y']
            poi_types = data['poi_types']
            poi_names = data.get('poi_names', [f'Point {i+1}' for i in range(len(poi_x))])
            
            # Créer un scatter plot pour chaque type de POI
            for poi_type in np.unique(poi_types):
                mask = poi_types == poi_type
                fig.add_trace(go.Scatter(
                    x=poi_x[mask],
                    y=poi_y[mask],
                    mode='markers+text',
                    marker=dict(
                        symbol='square',
                        size=10,
                        color=poi_colors.get(poi_type, 'gray')
                    ),
                    text=[name for name, m in zip(poi_names, mask) if m],
                    textposition="top center",
                    name=f'POI ({poi_type})',
                    hoverinfo='text',
                    hovertext=[f'Nom: {name}<br>Type: {poi_type}<br>X: {x:.2f}<br>Y: {y:.2f}' 
                              for name, x, y, m in zip(poi_names, poi_x[mask], poi_y[mask], mask) if m]
                ))

        # Ajout des chemins s'ils existent
        if 'paths' in data:
            paths = data['paths'].item()  # Convertir l'array numpy en dictionnaire Python
            for path_name, path_data in paths.items():
                fig.add_trace(go.Scatter(
                    x=path_data['x'],
                    y=path_data['y'],
                    mode='lines',
                    line=dict(
                        color='red',
                        width=2
                    ),
                    name=path_name,
                    visible=True
                ))

        # Mise à jour des axes et du titre
        fig.update_layout(
            title="Visualisation de la map",
            xaxis=dict(
                range=[min_x, max_x],
                autorange=True
            ),
            yaxis=dict(
                range=[min_y, max_y],
                autorange=True
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

def get_map_data(file_path, start_name=None, end_name=None):
    """
    Extrait les données de la carte et les points spécifiques à partir d'un fichier NPZ.

    Args:
        file_path (str): Chemin vers le fichier NPZ contenant les données d'occupation.
        start_name (str): Nom du point de départ à rechercher.
        end_name (str): Nom du point d'arrivée à rechercher.

    Returns:
        tuple: (grid, start_point, end_point) où:
            - grid: np.ndarray - Matrice binaire (0 = libre, 1 = obstacle)
            - start_point: tuple - Coordonnées (x, y) du point de départ ou None
            - end_point: tuple - Coordonnées (x, y) du point d'arrivée ou None
    """
    try:
        data = np.load(file_path, allow_pickle=True)
        
        # Convertir la grille en matrice binaire (0 et 1)
        grid = data["obstacle_grid"].astype(int)
        
        start_point = None
        end_point = None
        
        if all(key in data for key in ['poi_x', 'poi_y', 'poi_names']):
            poi_x = data['poi_x']
            poi_y = data['poi_y']
            poi_names = data['poi_names']
            
            # Rechercher le point de départ par son nom
            if start_name:
                start_indices = np.where(poi_names == start_name)[0]
                if len(start_indices) > 0:
                    idx = start_indices[0]
                    start_point = (int(round(poi_x[idx])), int(round(poi_y[idx])))
            
            # Rechercher le point d'arrivée par son nom
            if end_name:
                end_indices = np.where(poi_names == end_name)[0]
                if len(end_indices) > 0:
                    idx = end_indices[0]
                    end_point = (int(round(poi_x[idx])), int(round(poi_y[idx])))
        
        return grid, start_point, end_point
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des données: {str(e)}")
        return None, None, None

# Exemple d'utilisation
if __name__ == "__main__":
    file_path = "data/NPZ-output/occupancy_data.npz"
    result = visualize_occupancy_data(file_path)
    if result:
        print("Graphique interactif généré avec succès.")
    else:
        print("Échec de la visualisation.")
