import os
from flask import Blueprint, redirect, url_for, render_template, request, send_from_directory, jsonify
from backend.viewer import visualize_occupancy_data
from backend.utils import list_npz_files, delete_map_files, add_poi_to_map
from backend.svg_convertor import svg_to_occupancy, save_occupancy_data

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

@bp.route('/maps_list')
def maps_list():
    maps = list_npz_files("data/NPZ-output/")
    return render_template('maps_list.html', maps=maps)

@bp.route('/viewer/<map_name>')
def viewer(map_name):
    # Chemin du fichier NPZ
    file_path = os.path.join("data/NPZ-output", f"{map_name}.npz")

    # Génération du graphique interactif
    plot_html = visualize_occupancy_data(file_path)

    # Passer le contenu HTML du graphique à la page HTML
    if plot_html:
        return render_template('viewer.html', plot_html=plot_html, map_name=map_name)
    else:
        return "Erreur lors de la génération du graphique", 500

@bp.route('/new_map')
def new_map():
    return render_template("new_map.html")


@bp.route('/upload_and_process_svg', methods=['POST'])
def upload_and_process_svg():
    # Vérifie si un fichier a été envoyé
    if 'svg_file' not in request.files:
        return "No file uploaded", 400
    file = request.files['svg_file']
    if file.filename == '':
        return "No file selected", 400

    # Sauvegarde le fichier dans le dossier dédié
    svg_directory = "data/SVG-input"
    npz_directory = "data/NPZ-output"
    preview_directory = "app/static/map_previews"
    os.makedirs(svg_directory, exist_ok=True)
    os.makedirs(npz_directory, exist_ok=True)
    os.makedirs(preview_directory, exist_ok=True)

    try:
        upload_path = os.path.join(svg_directory, file.filename)
        file.save(upload_path)

        # Traite le fichier SVG
        grid, bounds = svg_to_occupancy(upload_path)
        output_path = os.path.join(npz_directory, os.path.splitext(file.filename)[0] + ".npz")
        save_occupancy_data(grid, bounds, output_path)

        # Génère et sauvegarde une preview PNG
        from backend.viewer import generate_plot_preview  # Import local pour éviter les dépendances circulaires
        preview_path = os.path.join(preview_directory, os.path.splitext(file.filename)[0] + ".png")
        generate_plot_preview(grid, bounds, preview_path)

        # Redirige vers la page d'accueil après le traitement
        return redirect(url_for('main.home'))
    except Exception as e:
        return f"Error processing SVG: {str(e)}", 500

@bp.route('/delete_map/<map_name>', methods=['POST'])
def delete_map(map_name):
    try:
        # Call the utility function to delete the map files
        delete_map_files(map_name)
        return redirect(url_for('main.home'))
    except Exception as e:
        return f"Error deleting map: {str(e)}", 500

@bp.route('/add_poi/<map_name>', methods=['POST'])
def add_poi(map_name):
    data = request.get_json()
    file_path = os.path.join("data/NPZ-output", f"{map_name}.npz")
    
    success = add_poi_to_map(
        file_path,
        x=data['x'],
        y=data['y'],
        poi_type=data['type']
    )
    
    return jsonify({'success': success})