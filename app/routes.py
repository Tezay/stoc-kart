import os

import numpy as np
from flask import Blueprint, redirect, url_for, render_template, request, send_from_directory, jsonify
from plotly.callbacks import Points
from scipy.interpolate import griddata

from backend.pathfinding.a_star import astar_pathfinding
from backend.viewer import visualize_occupancy_data, get_map_data
from backend.utils import list_npz_files, delete_map_files, add_poi_to_map, get_poi_map, delete_poi_from_map, rename_poi_in_map, add_new_path_to_map
from backend.svg_convertor import svg_to_occupancy, save_occupancy_data

# Créeation du blueprint pour les routes principales
bp = Blueprint('main', __name__)

# Route à la racine
@bp.route('/')
def home():
    return render_template('index.html')

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
    pois = get_poi_map(file_path)  # Récupérer les POIs

    # Passer le contenu HTML du graphique à la page HTML
    if plot_html:
        return render_template('viewer.html', plot_html=plot_html, map_name=map_name, pois=pois)
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
        poi_type=data['type'],
        poi_name=data.get('name', 'Point')
    )

    # Process l'algo de pathfinding uniquement sur un point de type "end"
    if data['type'] == 'end':
        points = get_poi_map(file_path)
        start_point = None
        
        # Récupère le point de départ
        for point in points:
            if point["type"] == np.str_('start'):
                start_point = point
                break
        print(f"Point de départ trouvé : {start_point}")
        
        # Si on a un point de départ, on effectue le pathfinding
        if start_point is not None:
            grid, start_coords, end_coords = get_map_data(file_path, start_point["name"], data.get('name', 'Point'))
            path = astar_pathfinding(grid, start_coords, end_coords)
            if not path:
                delete_poi_from_map(file_path, data.get('name', 'Point'))
                return jsonify({'success': False, 'message': "Aucun path trouvé. Le point est supprimé."})
            path_name = "path_to_" + data.get('name', 'Point')
            # Ajoute le chemin à la map
            add_new_path_to_map(file_path, path, path_name)
    
    return jsonify({'success': success})

@bp.route('/delete_poi/<map_name>', methods=['POST'])
def delete_poi(map_name):
    data = request.get_json()
    file_path = os.path.join("data/NPZ-output", f"{map_name}.npz")
    
    success = delete_poi_from_map(file_path, data['name'])
    return jsonify({'success': success})

@bp.route('/rename_poi/<map_name>', methods=['POST'])
def rename_poi(map_name):
    data = request.get_json()
    file_path = os.path.join("data/NPZ-output", f"{map_name}.npz")
    
    success = rename_poi_in_map(
        file_path,
        old_name=data['old_name'],
        new_name=data['new_name']
    )
    return jsonify({'success': success})

@bp.route('/select_map')
def select_map():
    maps = list_npz_files("data/NPZ-output/")
    return render_template('select_map.html', maps=maps)

@bp.route('/create_course/<map_name>')
def create_course(map_name):
    # Chemin du fichier NPZ
    file_path = os.path.join("data/NPZ-output", f"{map_name}.npz")

    # Génération du graphique interactif
    plot_html = visualize_occupancy_data(file_path)

    # Récupérer les POIs
    pois = get_poi_map(file_path)
    
    # Filtrer pour obtenir seulement les points de départ et d'arrivée
    start_points = [poi for poi in pois if poi['type'] == 'start']
    end_points = [poi for poi in pois if poi['type'] == 'end']
    
    # Créer toutes les combinaisons possibles
    routes = []
    for start in start_points:
        for end in end_points:
            routes.append({
                'start': start['name'],
                'end': end['name']
            })
    
    return render_template('create_course.html', plot_html=plot_html, map_name=map_name, routes=routes)