import os
from flask import Blueprint, redirect, url_for, render_template, request, send_from_directory
from backend.viewer import visualize_occupancy_data

# Créeation du blueprint pour les routes principales
bp = Blueprint('main', __name__)

# Route à la racine
@bp.route('/')
def home():
    return render_template('index.html')

# Ajout d'une route pour servir les images générées
@bp.route('/generated/<filename>')
def serve_generated_file(filename):
    return send_from_directory('static/generated', filename)

@bp.route('/viewer')
def viewer():
    # Chemin du fichier NPZ et du dossier pour les images générées (ghetto pour le moment, juste pour test)
    file_path = "data/NPZ-output/occupancy_data.npz"
    output_dir = "app/static/generated"
    os.makedirs(output_dir, exist_ok=True)

    # Génération de l'image
    output_image_path = os.path.join(output_dir, "occupancy_plot.png")
    image_path = visualize_occupancy_data(file_path, output_image_path)

    # Passer le chemin de l'image à la page HTML
    if image_path:
        image_url = url_for('main.serve_generated_file', filename="occupancy_plot.png")
        return render_template('viewer.html', image_url=image_url)
    else:
        return "Erreur lors de la génération de l'image", 500
    
@bp.route('/new_map')
def new_map():
    return render_template('new_map.html')