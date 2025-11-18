document.addEventListener('DOMContentLoaded', function() {
    fetch('data/team_stats.json')
        .then(response => response.json())
        .then(data => {
            if(data.matches) {
                renderMatches(data.matches);
            } else {
                document.getElementById('match-list').innerHTML = "<p>No match data found in archive.</p>";
            }
        });
});

function renderMatches(matches) {
    const container = document.getElementById('match-list');
    container.innerHTML = '';

    matches.forEach((match) => {
        // Create list of scorers HTML
        let scorersHtml = match.scorers.length > 0 
            ? '⚽ ' + match.scorers.join(', ') 
            : 'No goals scored';
            
        // Determine color based on result
        let resultClass = '';
        if (match.result === 'W') resultClass = 'win-bg';
        else if (match.result === 'D') resultClass = 'draw-bg';
        else if (match.result === 'L') resultClass = 'loss-bg';

        const card = document.createElement('div');
        card.className = `match-card ${resultClass}`;
        card.innerHTML = `
            <div class="match-date">${match.date}</div>
            <div style="text-align:center; font-weight:bold; font-size:1.2rem;">
                Tamarindi FC vs <br> ${match.opponent}
            </div>
            <div class="match-score">${match.score}</div>
            <div class="scorers">${scorersHtml}</div>
            
            <div 
                class="yt-button" 
                onclick="loadVideo(this, '${match.opponent}', '${match.date}')"
                data-opponent="${match.opponent}"
                data-date="${match.date}">
                ▶ Search Highlights
            </div>
            <div class="video-container"></div>
        `;
        container.appendChild(card);
    });
}

// Called when you click "Watch Highlights"
function loadVideo(btn, opponent, date) {
    const container = btn.nextElementSibling;
    
    if (container.innerHTML !== '') {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
        btn.textContent = container.style.display === 'none' ? "▶ Show Video" : "▼ Hide Video";
        return;
    }

    // --- YOUTUBE API CONFIGURATION ---
    // The key is injected from the environment variable (js/config.js)
    const API_KEY = CONFIG.YT_KEY;
    
    // We are combining the search query with the channel name to limit results
    // Example: "Tamarindi vs Corinthians 2025-03-12 torneiconti"
    const query = `Tamarindi vs ${opponent} ${date} torneiconti`; 
    
    // We also use the channel handle in the search URL for better filtering
    const channelHandle = '@torneiconti359'; 
    const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&key=${API_KEY}&type=video&maxResults=1&channelId=${channelHandle}`;

    btn.textContent = "Searching...";

    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.items && data.items.length > 0 && data.items[0].snippet.channelTitle.includes('Tornei Conti')) {
                const videoId = data.items[0].id.videoId;
                
                container.innerHTML = `
                    <iframe 
                        src="https://www.youtube.com/embed/${videoId}" 
                        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen>
                    </iframe>`;
                container.style.display = 'block';
                btn.textContent = "▼ Hide Video";
                btn.style.background = '#ff0000'; // Make it YouTube Red
            } else {
                btn.textContent = "Video Not Found";
                btn.style.background = "#555"; // Grey out
                btn.onclick = null; // Disable future clicks
            }
        })
        .catch(err => {
            console.error("API Error:", err);
            btn.textContent = "API Error";
            btn.style.background = "black";
        });
}