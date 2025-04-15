import os

def list_npz_files(directory="data/NPZ-output/"):
    """
    Liste tous les fichiers NPZ dans le répertoire spécifié.

    Args:
        directory (str): Chemin du répertoire à scanner.

    Returns:
        list: Liste des noms de fichiers NPZ trouvés.
    """
    try:
        return [f for f in os.listdir(directory) if f.endswith('.npz')]
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
