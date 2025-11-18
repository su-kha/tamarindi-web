document.addEventListener('DOMContentLoaded', function() {
    fetch('data/team_stats.json')
        .then(response => response.json())
        .then(data => {
            if(data.matches) {
                renderMatches(data.matches);
            } else {
                document.getElementById('match-list').innerHTML = "<p>No match data found in Excel.</p>";
            }
        });
});

function renderMatches(matches) {
    const container = document.getElementById('match-list');
    container.innerHTML = '';

    matches.forEach((match, index) => {
        // Create list of scorers HTML
        let scorersHtml = match.scorers.length > 0 
            ? '⚽ ' + match.scorers.join(', ') 
            : 'No goals scored';

        const card = document.createElement('div');
        card.className = 'match-card';
        card.innerHTML = `
            <div class="match-date">${match.date}</div>
            <div style="text-align:center; font-weight:bold; font-size:1.2rem;">
                Tamarindi FC vs <br> ${match.opponent}
            </div>
            <div class="match-score">${match.score}</div>
            <div class="scorers">${scorersHtml}</div>
            
            <div class="yt-button" onclick="loadVideo(this, '${match.opponent}', '${match.date}')">
                ▶ WATCH HIGHLIGHTS
            </div>
            <div class="video-container"></div>
        `;
        container.appendChild(card);
    });
}

// Called when you click "Watch Highlights"
function loadVideo(btn, opponent, date) {
    const container = btn.nextElementSibling; // The .video-container div
    
    // 1. Check if we already loaded it
    if (container.innerHTML !== '') {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
        return;
    }

    // 2. Build Search Query
    const query = `Tamarindi FC vs ${opponent}`;
    console.log("Searching YouTube for:", query);

    // 3. Call API
    const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&key=${CONFIG.YT_KEY}&type=video&maxResults=1`;
    btn.textContent = "Loading...";

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.items && data.items.length > 0) {
                const videoId = data.items[0].id.videoId;
                
                // Embed the video
                container.innerHTML = `
                    <iframe 
                        src="https://www.youtube.com/embed/${videoId}" 
                        allowfullscreen>
                    </iframe>`;
                container.style.display = 'block';
                btn.textContent = "▼ Hide Video";
            } else {
                btn.textContent = "Video not found on YouTube";
                btn.style.background = "#555";
            }
        })
        .catch(err => {
            console.error(err);
            btn.textContent = "Error loading API";
        });
}