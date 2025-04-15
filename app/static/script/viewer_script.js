let selectedPoint = null;
let selectedPointType = null;

document.getElementById('add-start-btn').addEventListener('click', () => {
    startPointSelection('start');

    document.getElementById('add-start-btn').style.backgroundColor = 'lightgreen';
    clickedButton = true;
});

document.getElementById('add-point-btn').addEventListener('click', () => {
    startPointSelection('end');
    // Change button color to indicate selection
    document.getElementById('add-point-btn').style.backgroundColor = 'lightcoral';
    clickedButton = true;
});

function startPointSelection(type) {
    selectedPointType = type;
    document.getElementById('click-instruction').style.display = 'block';
    
    const plot = document.getElementById('plotContainer').getElementsByClassName('js-plotly-plot')[0];
    plot.on('plotly_click', handlePlotClick);
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
        if (data.success) {
            location.reload();
        } else {
            alert('Erreur lors de l\'ajout du point');
        }
    });
    
    closeDialog();
}

function cancelPointName() {
    closeDialog();
}

function resetButtonColors() {
    document.getElementById('add-start-btn').style.backgroundColor = '';
    document.getElementById('add-point-btn').style.backgroundColor = '';
}

function closeDialog() {
    document.getElementById('pointNameDialog').style.display = 'none';
    document.getElementById('pointName').value = '';
    selectedPoint = null;
    selectedPointType = null;
    document.getElementById('click-instruction').style.display = 'none';
    resetButtonColors();
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
