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
