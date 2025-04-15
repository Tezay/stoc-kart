let selectedPoint = null;
let selectedPointType = null;

let clickedButton = false;

// Remove button color on click anywhere else
document.addEventListener('click', (event) => {
    const target = event.target;
    if (!target.closest('#add-start-btn') && !target.closest('#add-point-btn')) {
        if (clickedButton) {
            document.getElementById('add-start-btn').style.backgroundColor = '';
            document.getElementById('add-point-btn').style.backgroundColor = '';
            clickedButton = false;

            // Close the dialog to avoid being stuck in selection mode
            closeDialog();
        }
    }
});

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

function closeDialog() {
    document.getElementById('pointNameDialog').style.display = 'none';
    document.getElementById('pointName').value = '';
    selectedPoint = null;
    selectedPointType = null;
    document.getElementById('click-instruction').style.display = 'none';
}
