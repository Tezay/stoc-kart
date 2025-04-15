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
