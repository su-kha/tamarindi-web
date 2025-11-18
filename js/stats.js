let globalData = {};

document.addEventListener('DOMContentLoaded', function() {
    fetch('data/team_stats.json')
        .then(response => response.json())
        .then(data => {
            globalData = data;
            // Load default (Current Season)
            renderTable('season_24_25');
        })
        .catch(err => console.error("Error:", err));
});

function changeSeason() {
    const selected = document.getElementById('season-select').value;
    renderTable(selected);
}

function renderTable(key) {
    const tbody = document.getElementById('table-body');
    const thead = document.getElementById('table-head');
    const title = document.getElementById('table-title');
    
    tbody.innerHTML = '';
    const players = globalData[key] || [];

    // --- A. ALL TIME TABLE ---
    if (key === 'all_time') {
        title.textContent = "Hall of Fame (All Time)";
        thead.innerHTML = `
            <tr>
                <th>Player</th>
                <th>Role</th>
                <th>Apps</th>
                <th>Goals</th>
                <th>Assists</th>
            </tr>`;
        
        players.sort((a, b) => b.total_apps - a.total_apps); // Sort by Apps
        
        players.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td style="text-align:left; font-weight:bold;">${p.name}</td>
                    <td style="font-size:0.8rem;">${p.role}</td>
                    <td style="background:#fff0f5; font-weight:bold;">${p.total_apps}</td>
                    <td>${p.total_goals}</td>
                    <td>${p.total_assists}</td>
                </tr>`;
        });

    // --- B. SEASON TABLES ---
    } else {
        title.textContent = key.replace('season_', 'Season ').replace('_', '/');
        thead.innerHTML = `
            <tr>
                <th>Player</th>
                <th>#</th>
                <th>Apps</th>
                <th>Goals</th>
                <th>Assists</th>
                <th>Yel</th>
                <th>Red</th>
            </tr>`;

        players.sort((a, b) => b.goals - a.goals); // Sort by Goals
        
        players.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td style="text-align:left; font-weight:bold;">${p.name}</td>
                    <td>${p.number}</td>
                    <td>${p.apps}</td>
                    <td style="background:#fff0f5; font-weight:bold;">${p.goals}</td>
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