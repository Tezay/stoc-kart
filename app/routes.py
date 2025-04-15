import os
from flask import Blueprint, redirect, url_for, render_template, request, send_from_directory
from backend.viewer import visualize_occupancy_data
from backend.utils import list_npz_files

# Créeation du blueprint pour les routes principales
bp = Blueprint('main', __name__)

# Route à la racine
@bp.route('/')
def home():
    maps = list_npz_files("data/NPZ-output/")
    print("maps :", maps)
    return render_template('index.html', maps=maps)

# Ajout d'une route pour servir les images générées
@bp.route('/generated/<filename>')
def serve_generated_file(filename):
    return send_from_directory('static/generated', filename)

@bp.route('/viewer/<map_name>')
def viewer(map_name):
    # Chemin du fichier NPZ
    file_path = os.path.join("data/NPZ-output", map_name)

    # Génération du graphique interactif
    plot_html = visualize_occupancy_data(file_path)

    # Passer le contenu HTML du graphique à la page HTML
    if plot_html:
        return render_template('viewer.html', plot_html=plot_html)
    else:
        return "Erreur lors de la génération du graphique", 500

@bp.route('/new_map')
def new_map():
    return render_template("new_map.html")