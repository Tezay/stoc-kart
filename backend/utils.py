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
