let globalData = {};

// State to track sorting
let currentSort = {
    column: 'goals', 
    direction: 'desc' 
};

document.addEventListener('DOMContentLoaded', function() {
    console.log("Stats page loaded");
    
    fetch('data/website_data_cache.json')
        .then(response => response.json())
        .then(data => {
            globalData = data;
            renderTable('season_25_26'); 
        })
        .catch(err => console.error("Error loading stats:", err));
});

function changeSeason() {
    const selected = document.getElementById('season-select').value;
    
    if (selected === 'all_time') {
        currentSort = { column: 'total_apps', direction: 'desc' };
    } else {
        currentSort = { column: 'goals', direction: 'desc' };
    }
    
    renderTable(selected);
}

function handleSort(column) {
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'desc' ? 'asc' : 'desc';
    } else {
        currentSort.column = column;
        // Names and Numbers usually sort Low-to-High (A-Z, 1-99)
        // Stats usually sort High-to-Low (Most goals first)
        currentSort.direction = (column === 'name' || column === 'number' || column === 'role') ? 'asc' : 'desc';
    }
    
    const currentView = document.getElementById('season-select').value;
    renderTable(currentView);
}

function renderTable(key) {
    const tbody = document.getElementById('table-body');
    const thead = document.getElementById('table-head');
    const title = document.getElementById('table-title');
    
    if (!globalData[key]) return;

    const players = [...globalData[key]]; 

    // 1. SORTING LOGIC
    players.sort((a, b) => {
        let valA = a[currentSort.column];
        let valB = b[currentSort.column];

        const clean = (v, colName) => {
            if (v === '-' || v === null || v === undefined) return -999;
            if (colName === 'number') return parseInt(v, 10) || 0;
            if (typeof v === 'string') {
                 if (!isNaN(v) && v.trim() !== '') return parseFloat(v);
                 return v.toLowerCase();
            }
            return v;
        };

        valA = clean(valA, currentSort.column);
        valB = clean(valB, currentSort.column);

        if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
        if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
    });

    // --- HELPER: Merges base styles with the "Active Pink" style ---
    const getStyle = (colName, baseCss = '') => {
        let css = baseCss;
        if (currentSort.column === colName) {
            // Add the pink background
            css += ' background:#fff0f5;';
            
            // If it's a stats column (not name/role/number), make it bold too
            if (!['name', 'role', 'number'].includes(colName)) {
                css += ' font-weight:bold;';
            }
        }
        return css ? `style="${css}"` : '';
    };

    // --- HELPER: Creates Header with Arrow ---
    const createHeader = (label, colName) => {
        let arrow = '';
        if (currentSort.column === colName) {
            arrow = currentSort.direction === 'asc' ? ' ▲' : ' ▼';
        }
        return `<th onclick="handleSort('${colName}')" ${getStyle(colName)}>${label} <span class="sort-icon${currentSort.column === colName ? ' active' : ''}">${arrow}</span></th>`;
    };

    // 2. BUILD TABLE
    if (key === 'all_time') {
        title.textContent = "Hall of Fame (All Time)";
        thead.innerHTML = `
            <tr>
                ${createHeader('Giocatore', 'name')}
                ${createHeader('Ruolo', 'role')}
                ${createHeader('Presenze Totali', 'total_apps')}
                ${createHeader('Goal Totali', 'total_goals')}
                ${createHeader('Assist Totali', 'total_assists')}
            </tr>`;
        
        tbody.innerHTML = '';
        players.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td ${getStyle('name', 'text-align:left; font-weight:bold;')}>${p.name}</td>
                    <td ${getStyle('role', 'font-size:0.8rem; font-style:italic;')}>${p.role}</td>
                    
                    <td ${getStyle('total_apps')}>${p.total_apps}</td>
                    <td ${getStyle('total_goals')}>${p.total_goals}</td>
                    <td ${getStyle('total_assists')}>${p.total_assists}</td>
                </tr>`;
        });

    } else {
        title.textContent = key.replace('season_', 'Stagione ').replace('_', '/');
        thead.innerHTML = `
            <tr>
                ${createHeader('Giocatore', 'name')}
                ${createHeader('#', 'number')}
                ${createHeader('Presenze', 'apps')}
                ${createHeader('Goal', 'goals')}
                ${createHeader('Assist', 'assists')}
                ${createHeader('Gialli', 'yellow_cards')}
                ${createHeader('Rossi', 'red_cards')}
            </tr>`;

        tbody.innerHTML = '';
        players.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td ${getStyle('name', 'text-align:left; font-weight:bold;')}>${p.name}</td>
                    <td ${getStyle('number')}>${p.number}</td>
                    
                    <td ${getStyle('apps')}>${p.apps}</td>
                    <td ${getStyle('goals')}>${p.goals}</td>
                    <td ${getStyle('assists')}>${p.assists}</td>
                    <td ${getStyle('yellow_cards')}>${p.yellow_cards}</td>
                    <td ${getStyle('red_cards')}>${p.red_cards}</td>
                </tr>`;
        });
    }
    
    if (players.length === 0) {
        tbody.innerHTML = "<tr><td colspan='7'>No data available for this season.</td></tr>";
    }
}