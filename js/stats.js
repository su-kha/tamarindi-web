let globalData = {};

// State to track sorting
let currentSort = {
    column: 'goals', // Default sort column
    direction: 'desc' // 'desc' = High to Low, 'asc' = Low to High
};

document.addEventListener('DOMContentLoaded', function() {
    console.log("Stats page loaded");
    
    fetch('data/team_stats.json')
        .then(response => response.json())
        .then(data => {
            globalData = data;
            
            // Default to Current Season (25/26)
            renderTable('season_25_26'); 
        })
        .catch(err => console.error("Error loading stats:", err));
});

function changeSeason() {
    const selected = document.getElementById('season-select').value;
    
    // Reset sort defaults when switching views
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
        // If sorting by Name, default to A-Z (asc). Numbers default to High-to-Low (desc)
        currentSort.direction = column === 'name' || column === 'number' ? 'asc' : 'desc';
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

    // --- SORTING LOGIC ---
    players.sort((a, b) => {
        let valA = a[currentSort.column];
        let valB = b[currentSort.column];

        // Helper to clean values for sorting
        const clean = (v, colName) => {
            if (v === '-' || v === null || v === undefined) return -999; // Treat '-' as lowest
            
            // IF it's the Shirt Number, force it to be a real number for sorting
            if (colName === 'number') {
                return parseInt(v, 10) || 0;
            }

            // If string, make lowercase for fair comparison
            if (typeof v === 'string') {
                 // Check if it's actually a number string like "10"
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


    // --- RENDER HEADERS ---
    const createHeader = (label, colName) => {
        let arrow = '';
        if (currentSort.column === colName) {
            arrow = currentSort.direction === 'asc' ? ' ▲' : ' ▼';
        }
        return `<th onclick="handleSort('${colName}')">${label} <span class="sort-icon${currentSort.column === colName ? ' active' : ''}">${arrow}</span></th>`;
    };

    if (key === 'all_time') {
        title.textContent = "Hall of Fame (All Time)";
        thead.innerHTML = `
            <tr>
                ${createHeader('Player', 'name')}
                ${createHeader('Role', 'role')}
                ${createHeader('Total Apps', 'total_apps')}
                ${createHeader('Total Goals', 'total_goals')}
                ${createHeader('Total Assists', 'total_assists')}
            </tr>`;
        
        tbody.innerHTML = '';
        players.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td style="text-align:left; font-weight:bold;">${p.name}</td>
                    <td style="font-size:0.8rem;">${p.role}</td>
                    <td style="font-weight:bold; background:#fff0f5;">${p.total_apps}</td>
                    <td>${p.total_goals}</td>
                    <td>${p.total_assists}</td>
                </tr>`;
        });

    } else {
        title.textContent = key.replace('season_', 'Season ').replace('_', '/');
        thead.innerHTML = `
            <tr>
                ${createHeader('Player', 'name')}
                ${createHeader('#', 'number')}
                ${createHeader('Apps', 'apps')}
                ${createHeader('Goals', 'goals')}
                ${createHeader('Assists', 'assists')}
                ${createHeader('Yel', 'yellow_cards')}
                ${createHeader('Red', 'red_cards')}
            </tr>`;

        tbody.innerHTML = '';
        players.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td style="text-align:left; font-weight:bold;">${p.name}</td>
                    <td>${p.number}</td>
                    <td>${p.apps}</td>
                    <td style="font-weight:bold; background:#fff0f5;">${p.goals}</td>
                    <td>${p.assists}</td>
                    <td>${p.yellow_cards}</td>
                    <td>${p.red_cards}</td>
                </tr>`;
        });
    }
    
    if (players.length === 0) {
        tbody.innerHTML = "<tr><td colspan='7'>No data available for this season.</td></tr>";
    }
}