from flask import Blueprint, redirect, url_for, render_template, request

# Créeation du blueprint pour les routes principales
bp = Blueprint('main', __name__)


# Route à la racine
@bp.route('/')
def home():
    return render_template('index.html')
