import numpy as np
import sys
from svgpathtools import svg2paths

# Cette partie traitement du svg faudra repasser dessus, c'est la structure de base avec ChatGPT pour le moment
def svg_to_occupancy(svg_filename, resolution=20.0, samples_per_segment=500):
    """
    Lit le fichier SVG et produit une matrice (obstacle_grid)
    qui indique où se trouvent les obstacles (True) et où c'est libre (False).
    
    Paramètres
    ----------
    svg_filename : str
        Chemin vers le fichier SVG.
    resolution : float
        Nombre de 'pixels' par unité SVG. Plus c'est grand, plus la grille est fine.
    samples_per_segment : int
        Nombre d'échantillons par segment de chemin (pour discrétiser le dessin).
    
    Retourne
    --------
    obstacle_grid : np.ndarray (2D, bool)
    bounds : tuple (min_x, max_x, min_y, max_y)
    """

    paths, _ = svg2paths(svg_filename)

    # 1) Déterminer la bounding box globale
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    for path in paths:
        for segment in path:
            seg_min_x, seg_max_x, seg_min_y, seg_max_y = segment.bbox()
            min_x = min(min_x, seg_min_x)
            max_x = max(max_x, seg_max_x)
            min_y = min(min_y, seg_min_y)
            max_y = max(max_y, seg_max_y)

    # 2) Créer la matrice d’occupation
    width  = int((max_x - min_x) * resolution) + 1
    height = int((max_y - min_y) * resolution) + 1
    obstacle_grid = np.zeros((height, width), dtype=bool)

    # 3) Échantillonner les chemins et remplir obstacle_grid
    for path in paths:
        for segment in path:
            for i in range(samples_per_segment + 1):
                t = i / samples_per_segment
                point = segment.point(t)
                x = point.real
                y = point.imag

                # Convertir en indices de la matrice
                grid_x = int((x - min_x) * resolution)
                grid_y = int((y - min_y) * resolution)
                # Sécuriser les bornes
                if 0 <= grid_x < width and 0 <= grid_y < height:
                    obstacle_grid[grid_y, grid_x] = True

    return obstacle_grid, (min_x, max_x, min_y, max_y)

def save_occupancy_data(grid, bounds, output_filename):
    """
    Sauvegarde la matrice d’occupation et les limites de la bounding box dans un fichier .npz.
    """
    min_x, max_x, min_y, max_y = bounds
    np.savez(
        output_filename,
        obstacle_grid=grid,
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y
    )
    print(f"Matrice d’occupation sauvegardée dans {output_filename}.")


if __name__ == "__main__":
    """
    Exécution en ligne de commande :
      python svg-convertor.py input.svg output.npz [resolution]
      
    Exemple :
      python svg-convertor.py mon_scan_lidar.svg occupancy_data.npz 20.0
    """
    if len(sys.argv) < 3:
        print("Usage : python svg-convertor.py input.svg output.npz [resolution]")
        sys.exit(1)
        
    svg_filename = sys.argv[1]
    output_filename = sys.argv[2]
    
    # Si la résolution est donnée, on la prend. Sinon, on met une valeur par défaut.
    if len(sys.argv) >= 4:
        resolution = float(sys.argv[3])
    else:
        resolution = 20.0  # Valeur par défaut
    
    # Production de la matrice d’obstacle
    grid, bounds = svg_to_occupancy(svg_filename, resolution=resolution)
    print("Dimensions de la matrice :", grid.shape, "(height, width)")
    
    # Sauvegarde dans un fichier .npz
    save_occupancy_data(grid, bounds, output_filename)
