let selectedPoint = null;
let selectedPointType = null;
let hasStartPoint = false;
let clickedButton = false; // Ajout de cette variable manquante

// Variables pour le mode d'ajout d'obstacles
let obstacleMode = false;
let obstaclePoints = [];

document.getElementById('add-start-btn').addEventListener('click', () => {
    startPointSelection('start');
    document.getElementById('add-start-btn').style.backgroundColor = 'lightgreen';
    clickedButton = true;
});

document.getElementById('add-point-btn').addEventListener('click', () => {
    startPointSelection('end');
    document.getElementById('add-point-btn').style.backgroundColor = 'lightcoral';
    clickedButton = true;
});

document.getElementById('add-obstacle-btn').addEventListener('click', () => {
    if (obstacleMode) {
        // Si déjà en mode obstacle, confirmer les points sélectionnés
        confirmObstaclePoints();
    } else {
        // Sinon activer le mode obstacle
        startObstacleMode();
    }
});

function startPointSelection(type) {
    if (type === 'start' && hasStartPoint) {
        showError("Un point de départ existe déjà.");
        clickedButton = false; // Réinitialiser l'état du bouton
        resetButtonColors();
        return;
    }
    
    if (type === 'end' && !hasStartPoint) {
        showError("Vous devez d'abord placer un point de départ.");
        clickedButton = false; // Réinitialiser l'état du bouton
        resetButtonColors();
        return;
    }
    
    selectedPointType = type;
    document.getElementById('click-instruction').style.display = 'block';
    
    const plot = document.getElementById('plotContainer').getElementsByClassName('js-plotly-plot')[0];
    plot.on('plotly_click', handlePlotClick);
}

function startObstacleMode() {
    // Réinitialiser le mode de sélection de points
    selectedPointType = null;
    clickedButton = true;
    obstacleMode = true;
    obstaclePoints = [];
    
    // Changer le style du bouton et afficher les instructions
    document.getElementById('add-obstacle-btn').style.backgroundColor = 'orange';
    document.getElementById('click-instruction').style.display = 'none';
    document.getElementById('obstacle-instruction').style.display = 'block';
    
    // Écouter les clics sur le graphique
    const plot = document.getElementById('plotContainer').getElementsByClassName('js-plotly-plot')[0];
    plot.on('plotly_click', handleObstacleClick);
}

function handleObstacleClick(data) {
    const point = data.points[0];
    obstaclePoints.push({
        x: point.x,
        y: point.y
    });
    
    // Afficher les informations du point dans la console pour débogage
    console.log(`Point d'obstacle ajouté: (${point.x}, ${point.y})`);
    
    // Indiquer visuellement à l'utilisateur que le point a été ajouté
    alert(`Point d'obstacle #${obstaclePoints.length} ajouté aux coordonnées (${point.x.toFixed(2)}, ${point.y.toFixed(2)})`);
    
    if (obstaclePoints.length >= 2) {
        console.log("Vous pouvez maintenant cliquer à nouveau sur le bouton 'Ajouter des obstacles' pour confirmer");
    }
}

function confirmObstaclePoints() {
    if (obstaclePoints.length < 2) {
        showError("Veuillez sélectionner au moins deux points pour créer un obstacle.");
        return;
    }
    
    console.log(`Envoi de ${obstaclePoints.length} points d'obstacle au serveur:`);
    console.log(JSON.stringify(obstaclePoints));
    
    // Envoyer les points au serveur
    fetch(`/add_obstacle/${mapName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            points: obstaclePoints
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(`Réponse du serveur:`, data);
        if (data.success) {
            location.reload(); // Recharger la page pour afficher le nouvel obstacle
        } else {
            showError("Erreur lors de l'ajout de l'obstacle: " + (data.message || "Erreur inconnue"));
        }
    })
    .catch(error => {
        console.error(`Erreur lors de la requête:`, error);
        showError("Erreur de communication avec le serveur");
    });
    
    // Réinitialiser le mode obstacle
    resetObstacleMode();
}

function resetObstacleMode() {
    obstacleMode = false;
    obstaclePoints = [];
    document.getElementById('add-obstacle-btn').style.backgroundColor = '';
    document.getElementById('obstacle-instruction').style.display = 'none';
    resetButtonColors();
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorDialog').style.display = 'block';
}

function closeErrorDialog() {
    document.getElementById('errorDialog').style.display = 'none';
    clickedButton = false; // S'assurer que l'état du bouton est réinitialisé à la fermeture de la popup
    resetButtonColors();
    if (obstacleMode) {
        resetObstacleMode();
    }
}

function handlePlotClick(data) {
    if (!selectedPointType) return;
    
    const point = data.points[0];
    selectedPoint = {
        x: point.x,
        y: point.y,
        type: selectedPointType
    };
    
    document.getElementById('pointNameDialog').style.display = 'block';
}

function confirmPointName() {
    const name = document.getElementById('pointName').value.trim();
    if (!name) {
        alert('Veuillez entrer un nom pour le point');
        return;
    }
    
    selectedPoint.name = name;
    
    fetch(`/add_poi/${mapName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedPoint)
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success && data.message === "Aucun path trouvé. Le point est supprimé.") {
            showError(data.message);
            document.getElementById('errorDialog').addEventListener('click', () => location.reload());
        } else if (!data.success) {
            alert('Erreur lors de l\'ajout du point');
        } else {
            if (selectedPointType === 'start') {
                hasStartPoint = true;
            }
            location.reload();
        }
    });
    
    closeDialog();
}

function cancelPointName() {
    closeDialog();
}

function resetButtonColors() {
    if (!clickedButton) { // Ne réinitialiser les couleurs que si aucun bouton n'est actif
        document.getElementById('add-start-btn').style.backgroundColor = '';
        document.getElementById('add-point-btn').style.backgroundColor = '';
        document.getElementById('add-obstacle-btn').style.backgroundColor = '';
    }
}

function closeDialog() {
    document.getElementById('pointNameDialog').style.display = 'none';
    document.getElementById('pointName').value = '';
    selectedPoint = null;
    selectedPointType = null;
    document.getElementById('click-instruction').style.display = 'none';
    resetButtonColors();
    if (obstacleMode) {
        resetObstacleMode();
    }
}

let poiToDelete = null;

document.querySelectorAll('.delete-poi').forEach(button => {
    button.addEventListener('click', function() {
        poiToDelete = this.dataset.poiName;
        document.getElementById('deleteConfirmDialog').style.display = 'block';
    });
});

function confirmDelete() {
    if (!poiToDelete) return;
    
    fetch(`/delete_poi/${mapName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: poiToDelete
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erreur lors de la suppression du point');
        }
    });
    
    closeDeleteDialog();
}

function cancelDelete() {
    closeDeleteDialog();
}

function closeDeleteDialog() {
    document.getElementById('deleteConfirmDialog').style.display = 'none';
    poiToDelete = null;
}

let poiToRename = null;

document.querySelectorAll('.rename-poi').forEach(button => {
    button.addEventListener('click', function() {
        poiToRename = this.dataset.poiName;
        document.getElementById('newPointName').value = poiToRename;
        document.getElementById('renameDialog').style.display = 'block';
    });
});

function confirmRename() {
    if (!poiToRename) return;
    
    const newName = document.getElementById('newPointName').value.trim();
    if (!newName) {
        alert('Le nom ne peut pas être vide');
        return;
    }
    
    fetch(`/rename_poi/${mapName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            old_name: poiToRename,
            new_name: newName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erreur lors du renommage du point');
        }
    });
    
    closeRenameDialog();
}

function cancelRename() {
    closeRenameDialog();
}

function closeRenameDialog() {
    document.getElementById('renameDialog').style.display = 'none';
    document.getElementById('newPointName').value = '';
    poiToRename = null;
}

document.addEventListener('DOMContentLoaded', function() {
    const pois = document.querySelectorAll('table tbody tr');
    pois.forEach(poi => {
        const img = poi.querySelector('td:nth-child(2) img');
        if (img && img.alt === 'Point de départ') {
            hasStartPoint = true;
        }
    });
});
