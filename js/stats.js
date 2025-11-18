document.addEventListener('DOMContentLoaded', function() {
    console.log("Stats page loaded");
    
    // 1. Fetch the JSON data
    fetch('data/team_stats.json')
        .then(response => response.json())
        .then(data => {
            console.log("Data loaded:", data);
            renderSeasonTable(data.season_24_25);
            renderAllTimeTable(data.all_time);
        })
        .catch(error => {
            console.error("Error loading stats:", error);
            document.getElementById('season-body').innerHTML = "<tr><td colspan='7'>Error loading data. Please check console.</td></tr>";
        });
});

// Function to build the Current Season table
function renderSeasonTable(players) {
    const tbody = document.getElementById('season-body');
    tbody.innerHTML = ''; // Clear "Loading..."

    // Sort by Goals (highest first) by default
    players.sort((a, b) => b.goals - a.goals);

    players.forEach(player => {
        const row = `
            <tr>
                <td>${player.name}</td>
                <td>${player.number}</td>
                <td>${player.apps}</td>
                <td style="font-weight:bold; background:#fff0f5;">${player.goals}</td>
                <td>${player.assists}</td>
                <td>${player.yellow_cards}</td>
                <td>${player.red_cards}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Function to build the All Time table
function renderAllTimeTable(players) {
    const tbody = document.getElementById('alltime-body');
    tbody.innerHTML = ''; 

    // Sort by Total Apps by default
    players.sort((a, b) => b.total_apps - a.total_apps);

    players.forEach(player => {
        const row = `
            <tr>
                <td>${player.name}</td>
                <td style="font-size:0.8rem; font-style:italic;">${player.role}</td>
                <td style="font-weight:bold; background:#fff0f5;">${player.total_apps}</td>
                <td>${player.total_goals}</td>
                <td>${player.total_assists}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Tab Switching Logic
window.showTab = function(tabName) {
    // Hide all
    document.getElementById('season-view').classList.add('hidden');
    document.getElementById('alltime-view').classList.add('hidden');
    
    // Remove active class from buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    // Show selected
    if (tabName === 'season') {
        document.getElementById('season-view').classList.remove('hidden');
        document.querySelector('button[onclick="showTab(\'season\')"]').classList.add('active');
    } else {
        document.getElementById('alltime-view').classList.remove('hidden');
        document.querySelector('button[onclick="showTab(\'alltime\')"]').classList.add('active');
    }
}