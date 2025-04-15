let addingPoi = false;
let currentPoiType = '';
const addStartBtn = document.getElementById('addStartBtn');
const addPoiBtn = document.getElementById('addPoiBtn');
const clickInstruction = document.getElementById('clickInstruction');

function setupPoiButton(button, poiType) {
    button.addEventListener('click', function() {
        if (addingPoi && currentPoiType === poiType) {
            // Désactiver si on clique sur le même bouton
            addingPoi = false;
            currentPoiType = '';
            addStartBtn.style.backgroundColor = '';
            addPoiBtn.style.backgroundColor = '';
            clickInstruction.style.display = 'none';
        } else {
            // Activer le nouveau type
            addingPoi = true;
            currentPoiType = poiType;
            addStartBtn.style.backgroundColor = poiType === 'start' ? '#ffcccc' : '';
            addPoiBtn.style.backgroundColor = poiType === 'end' ? '#ccffcc' : '';
            clickInstruction.style.display = 'inline';
        }
    });
}

setupPoiButton(addStartBtn, 'start');
setupPoiButton(addPoiBtn, 'end');

document.getElementById('plotContainer').addEventListener('click', function(event) {
    if (!addingPoi) return;

    const plotElement = document.querySelector('.js-plotly-plot');
    if (!plotElement) return;

    // Récupérer les coordonnées relatives au graphique
    const rect = plotElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Obtenir le layout et les marges
    const layout = plotElement._fullLayout;
    const margin = layout.margin;
    
    // Calculer les dimensions effectives du graphique
    const plotArea = {
        width: rect.width - margin.l - margin.r,
        height: rect.height - margin.t - margin.b,
        left: margin.l,
        top: margin.t
    };

    // Calculer les coordonnées relatives à la zone de tracé
    const xInPlot = x - plotArea.left;
    const yInPlot = y - plotArea.top;

    // Convertir en coordonnées du graphique
    const xRange = layout.xaxis.range;
    const yRange = layout.yaxis.range;

    const xCoord = xRange[0] + (xRange[1] - xRange[0]) * (xInPlot / plotArea.width);
    const yCoord = yRange[1] - (yRange[1] - yRange[0]) * (yInPlot / plotArea.height);

    // Envoyer les coordonnées au serveur avec le type actuel
    fetch(`/add_poi/${mapName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            x: xCoord,
            y: yCoord,
            type: currentPoiType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });

    addingPoi = false;
    currentPoiType = '';
    addStartBtn.style.backgroundColor = '';
    addPoiBtn.style.backgroundColor = '';
    clickInstruction.style.display = 'none';
});
