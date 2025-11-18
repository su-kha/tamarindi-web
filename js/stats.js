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
            // Ensure this matches the "value" in your HTML select dropdown
            renderTable('season_25_26'); 
        })
        .catch(err => console.error("Error loading stats:", err));
});

// Triggered when user changes the dropdown
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

// Triggered when user clicks a table header
function handleSort(column) {
    // If clicking the same column, toggle direction
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'desc' ? 'asc' : 'desc';
    } else {
        // New column? Default to High-to-Low
        currentSort.column = column;
        currentSort.direction = 'desc';
    }
    
    // Re-render the current view
    const currentView = document.getElementById('season-select').value;
    renderTable(currentView);
}

function renderTable(key) {
    const tbody = document.getElementById('table-body');
    const thead = document.getElementById('table-head');
    const title = document.getElementById('table-title');
    
    // Safety check
    if (!globalData[key]) return;

    const players = [...globalData[key]]; // Create a copy to sort safely

    // --- 1. SORTING LOGIC ---
    players.sort((a, b) => {
        let valA = a[currentSort.column];
        let valB = b[currentSort.column];

        // Helper to clean values for sorting
        const clean = (v) => {
            if (v === '-') return -1; // Treat '-' as lowest possible number
            if (typeof v === 'string') return v.toLowerCase();
            return v;
        };

        valA = clean(valA);
        valB = clean(valB);

        if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
        if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
    });


    // --- 2. BUILD HEADERS (With Arrows) ---
    // Helper function to create clickable headers
    const createHeader = (label, colName) => {
        let arrow = '';
        if (currentSort.column === colName) {
            arrow = currentSort.direction === 'asc' ? ' ▲' : ' ▼';
        }
        // Note: We pass the column name to handleSort()
        return `<th onclick="handleSort('${colName}')">${label} <span class="sort-icon${currentSort.column === colName ? ' active' : ''}">${arrow}</span></th>`;
    };

    // Render All Time Headers
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

    // Render Season Headers
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