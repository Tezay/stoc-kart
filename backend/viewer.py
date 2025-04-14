import os
import numpy as np
import matplotlib.pyplot as plt

def visualize_occupancy_data(file_path, output_image_path):
    """
    Charge et visualise les données d'occupation à partir d'un fichier NPZ et sauvegarde le plot en tant qu'image.

    Args:
        file_path (str): Chemin vers le fichier NPZ contenant les données d'occupation
        output_image_path (str): Chemin pour sauvegarder l'image générée
    """
    try:
        # Chargement des données
        data = np.load(file_path)
        obstacle_grid = data["obstacle_grid"]
        min_x = data["min_x"]
        max_x = data["max_x"]
        min_y = data["min_y"]
        max_y = data["max_y"]

        # Création de la visualisation
        plt.figure(figsize=(10, 8))
        plt.imshow(obstacle_grid, cmap='Reds', origin='lower')
        plt.title("Visualisation des obstacles")
        plt.colorbar(label='Occupation')
        plt.xlabel(f'X ({min_x:.2f} to {max_x:.2f})')
        plt.ylabel(f'Y ({min_y:.2f} to {max_y:.2f})')

        # Sauvegarde du plot en tant qu'image
        plt.savefig(output_image_path)
        plt.close()

        return output_image_path

    except Exception as e:
        print(f"Erreur lors de la visualisation: {str(e)}")
        return None

# Exemple d'utilisation
if __name__ == "__main__":
    file_path = "data/NPZ-output/occupancy_data.npz"
    output_image_path = "output/occupancy_plot.png"
    result = visualize_occupancy_data(file_path, output_image_path)
    if result:
        print(f"Image sauvegardée à : {result}")
    else:
        print("Échec de la visualisation.")
