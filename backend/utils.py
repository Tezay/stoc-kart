import os

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
