import os
import numpy as np

def list_npz_files(directory="data/NPZ-output/"):
    """
    Liste tous les fichiers NPZ dans le répertoire spécifié sans l'extension .npz.

    Args:
        directory (str): Chemin du répertoire à scanner.

    Returns:
        list: Liste des noms de fichiers NPZ trouvés sans l'extension .npz.
    """
    try:
        return [os.path.splitext(f)[0] for f in os.listdir(directory) if f.endswith('.npz')]
    except FileNotFoundError:
        print(f"Le répertoire {directory} n'existe pas.")
        return []

def get_latest_file(directory, extension=".svg"):
    """
    Récupère le dernier fichier modifié dans un répertoire donné avec une extension spécifique.

    Args:
        directory (str): Chemin du répertoire.
        extension (str): Extension des fichiers à rechercher.

    Returns:
        str: Chemin du dernier fichier modifié ou None si aucun fichier trouvé.
    """
    try:
        files = [f for f in os.listdir(directory) if f.endswith(extension)]
        if not files:
            return None
        latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(directory, f)))
        return os.path.join(directory, latest_file)
    except FileNotFoundError:
        print(f"Le répertoire {directory} n'existe pas.")
        return None

def delete_map_files(map_name):
    """
    Supprime les fichiers associés à une map dans les répertoires SVG-input, NPZ-output et map_previews.

    Args:
        map_name (str): Nom de la map (sans extension).
    """
    directories = {
        "SVG-input": f"data/SVG-input/{map_name}.svg",
        "NPZ-output": f"data/NPZ-output/{map_name}.npz",
        "map_previews": f"app/static/map_previews/{map_name}.png"
    }

    for dir_name, file_path in directories.items():
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Fichier supprimé : {file_path}")
        else:
            print(f"Fichier introuvable dans {dir_name} : {file_path}")

def add_poi_to_map(map_path, x, y, poi_type='start', poi_name='Point'):
    """
    Ajoute un point d'intérêt à la carte.
    
    Args:
        map_path (str): Chemin vers le fichier NPZ
        x (float): Coordonnée X du point
        y (float): Coordonnée Y du point
        poi_type (str): Type du point d'intérêt
        poi_name (str): Nom du point d'intérêt
    """
    try:
        data = dict(np.load(map_path, allow_pickle=True))
        
        if 'poi_x' not in data:
            data['poi_x'] = np.array([], dtype=float)
            data['poi_y'] = np.array([], dtype=float)
            data['poi_types'] = np.array([], dtype='<U10')
            data['poi_names'] = np.array([], dtype='<U50')  # Pour stocker les noms
        
        data['poi_x'] = np.append(data['poi_x'], x)
        data['poi_y'] = np.append(data['poi_y'], y)
        data['poi_types'] = np.append(data['poi_types'], poi_type)
        data['poi_names'] = np.append(data['poi_names'], poi_name)
        
        np.savez(map_path, **data)
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'ajout du POI: {str(e)}")
        return False

def get_poi_map(map_path):
    """
    Récupère tous les points d'intérêt d'une carte.
    
    Args:
        map_path (str): Chemin vers le fichier NPZ

    Returns:
        list: Liste de dictionnaires contenant les infos de chaque POI
              [{'name': str, 'type': str, 'x': float, 'y': float}, ...]
    """
    try:
        data = np.load(map_path, allow_pickle=True)
        if all(key in data for key in ['poi_x', 'poi_y', 'poi_types', 'poi_names']):
            return [
                {
                    'name': name,
                    'type': poi_type,
                    'x': float(x),
                    'y': float(y)
                }
                for name, poi_type, x, y in zip(
                    data['poi_names'],
                    data['poi_types'],
                    data['poi_x'],
                    data['poi_y']
                )
            ]
        return []
    except Exception as e:
        print(f"Erreur lors de la récupération des POIs: {str(e)}")
        return []

def delete_poi_from_map(map_path, poi_name):
    """
    Supprime un point d'intérêt de la carte.
    
    Args:
        map_path (str): Chemin vers le fichier NPZ
        poi_name (str): Nom du point à supprimer

    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    try:
        data = dict(np.load(map_path, allow_pickle=True))
        
        if all(key in data for key in ['poi_x', 'poi_y', 'poi_types', 'poi_names']):
            # Trouver l'index du POI à supprimer
            idx = np.where(data['poi_names'] == poi_name)[0]
            if len(idx) > 0:
                # Supprimer le POI de tous les arrays
                data['poi_x'] = np.delete(data['poi_x'], idx)
                data['poi_y'] = np.delete(data['poi_y'], idx)
                data['poi_types'] = np.delete(data['poi_types'], idx)
                data['poi_names'] = np.delete(data['poi_names'], idx)
                
                # Sauvegarder les modifications
                np.savez(map_path, **data)
                return True
                
        return False
    except Exception as e:
        print(f"Erreur lors de la suppression du POI: {str(e)}")
        return False

def rename_poi_in_map(map_path, old_name, new_name):
    """
    Renomme un point d'intérêt dans la carte.
    
    Args:
        map_path (str): Chemin vers le fichier NPZ
        old_name (str): Ancien nom du point
        new_name (str): Nouveau nom du point

    Returns:
        bool: True si le renommage a réussi, False sinon
    """
    try:
        data = dict(np.load(map_path, allow_pickle=True))
        
        if all(key in data for key in ['poi_names']):
            idx = np.where(data['poi_names'] == old_name)[0]
            if len(idx) > 0:
                data['poi_names'][idx[0]] = new_name
                np.savez(map_path, **data)
                return True
        return False
    except Exception as e:
        print(f"Erreur lors du renommage du POI: {str(e)}")
        return False

def add_new_path_to_map(map_path, path_points, path_name="path"):
    """
    Ajoute un nouveau chemin à la carte.
    
    Args:
        map_path (str): Chemin vers le fichier NPZ
        path_points (list): Liste de tuples (x,y) définissant les points du chemin
        path_name (str): Nom du chemin à ajouter

    Returns:
        bool: True si l'ajout a réussi, False sinon
    """
    try:
        # Charger les données existantes
        with np.load(map_path, allow_pickle=True) as npz:
            data = dict(npz)
        
        # Initialiser le dictionnaire paths s'il n'existe pas
        if 'paths' not in data:
            data['paths'] = np.array(dict(), dtype=object)
        
        # Convertir le dictionnaire paths en dictionnaire Python standard
        paths_dict = data['paths'].item() if isinstance(data['paths'], np.ndarray) else {}
        
        # Convertir les points en arrays numpy
        path_x = np.array([float(p[0]) for p in path_points])
        path_y = np.array([float(p[1]) for p in path_points])
        
        # Mettre à jour le dictionnaire avec le nouveau chemin
        paths_dict[path_name] = {
            'x': path_x,
            'y': path_y
        }
        
        # Convertir le dictionnaire mis à jour en array numpy
        data['paths'] = np.array(paths_dict)
        
        # Sauvegarder les données mises à jour
        np.savez(map_path, **data)
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'ajout du chemin: {str(e)}")
        return False

def add_obstacle_to_map(map_path, points):
    """
    Ajoute un obstacle linéaire constitué d'une séquence de points à la carte.
    
    Args:
        map_path (str): Chemin vers le fichier NPZ
        points (list): Liste de dictionnaires {x: float, y: float} définissant les points de l'obstacle

    Returns:
        bool: True si l'ajout a réussi, False sinon
    """
    try:
        # Charger les données existantes
        print(f"Chargement du fichier NPZ: {map_path}")
        with np.load(map_path, allow_pickle=True) as npz_file:
            # Convertir en dictionnaire Python standard pour modifications
            data = dict(npz_file)
        
        # Récupérer la grille d'obstacles et les limites
        obstacle_grid = data['obstacle_grid'].copy()  # Créer une copie pour la modification
        min_x = data['min_x']
        max_x = data['max_x']
        min_y = data['min_y']
        max_y = data['max_y']
        
        # Afficher l'état initial
        height, width = obstacle_grid.shape
        print(f"Dimensions de la grille: {width}x{height}")
        print(f"Limites: X({min_x}, {max_x}), Y({min_y}, {max_y})")
        print(f"Nombre d'obstacles avant: {np.sum(obstacle_grid)}")
        
        # Pour chaque paire de points consécutifs, tracer une ligne
        total_pixels_modified = 0
        
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i+1]
            
            # Convertir les coordonnées en indices de grille
            # Attention: les coordonnées y peuvent être inversées selon convention
            x1 = float(p1['x'])
            y1 = float(p1['y'])
            x2 = float(p2['x'])
            y2 = float(p2['y'])
            
            print(f"Segment {i+1}: de ({x1}, {y1}) à ({x2}, {y2})")
            
            # Convertir en coordonnées de grille
            grid_x1 = int((x1 - min_x) * width / (max_x - min_x))
            grid_y1 = int((y1 - min_y) * height / (max_y - min_y))
            grid_x2 = int((x2 - min_x) * width / (max_x - min_x))
            grid_y2 = int((y2 - min_y) * height / (max_y - min_y))
            
            print(f"Coordonnées grille: de ({grid_x1}, {grid_y1}) à ({grid_x2}, {grid_y2})")
            
            # Algorithme de tracé de ligne simplifié (algorithme de Bresenham)
            pixels_modified = 0
            
            # Calculer les différences et les pas
            dx = abs(grid_x2 - grid_x1)
            dy = abs(grid_y2 - grid_y1)
            sx = 1 if grid_x1 < grid_x2 else -1
            sy = 1 if grid_y1 < grid_y2 else -1
            
            if dx > dy:
                # Pente < 1
                err = dx / 2
                x, y = grid_x1, grid_y1
                for _ in range(dx + 1):
                    if 0 <= x < width and 0 <= y < height:
                        obstacle_grid[y, x] = True
                        pixels_modified += 1
                    err -= dy
                    if err < 0:
                        y += sy
                        err += dx
                    x += sx
            else:
                # Pente >= 1
                err = dy / 2
                x, y = grid_x1, grid_y1
                for _ in range(dy + 1):
                    if 0 <= x < width and 0 <= y < height:
                        obstacle_grid[y, x] = True
                        pixels_modified += 1
                    err -= dx
                    if err < 0:
                        x += sx
                        err += dy
                    y += sy
            
            print(f"Pixels modifiés dans ce segment: {pixels_modified}")
            total_pixels_modified += pixels_modified
        
        # Vérifier s'il y a eu des modifications
        print(f"Total des pixels modifiés: {total_pixels_modified}")
        print(f"Nombre d'obstacles après: {np.sum(obstacle_grid)}")
        
        if total_pixels_modified == 0:
            print("Aucun pixel n'a été modifié!")
            return False
        
        # Mettre à jour le dictionnaire avec la nouvelle grille
        data['obstacle_grid'] = obstacle_grid
        
        # Sauvegarder le dictionnaire mis à jour dans le fichier NPZ
        print(f"Sauvegarde des modifications dans {map_path}")
        np.savez(map_path, **data)
        
        # Vérifier que la sauvegarde a bien fonctionné
        with np.load(map_path, allow_pickle=True) as check_file:
            check_grid = check_file['obstacle_grid']
            check_count = np.sum(check_grid)
            print(f"Vérification: {check_count} obstacles dans le fichier sauvegardé")
            
            if check_count == np.sum(obstacle_grid):
                print("Sauvegarde réussie!")
                return True
            else:
                print("ERREUR: La sauvegarde ne contient pas le bon nombre d'obstacles!")
                return False
        
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'obstacle: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
