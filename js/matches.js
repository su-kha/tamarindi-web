document.addEventListener('DOMContentLoaded', function() {
    fetch('data/website_data_cache.json')
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
        // --- 1. Score and Result HTML ---
        let resultClass = '';
        if (match.result.startsWith('W')) resultClass = 'win-bg';
        else if (match.result.startsWith('D')) resultClass = 'draw-bg';
        else if (match.result.startsWith('L')) resultClass = 'loss-bg';

        let scoreDisplay = match.score;
        let shootoutDisplay = '';
        
        if (match.shootout_score) {
            scoreDisplay = `${match.score}`;
            
            // Split the string by '+'
            const parts = match.shootout_score.split('+');
            // Get the last part using .pop() or index logic, and use .trim()
            const soScore = parts[parts.length - 1].trim();
            
            shootoutDisplay = `<div style="font-size:0.9rem; color:#444; margin-top:4px;">${soScore}</div>`;
        }

        // --- 2. Scorer HTML (Penalties/Goals) ---
        let scorersHtml = '';
        
        // --- 2a. Goals & Penalties ---
        let normalGoals = match.scorers.filter(s => !s.includes('(Pen)')).join(', ');
        let penalties = match.scorers.filter(s => s.includes('(Pen)')).map(s => s.replace(' (Pen)', '')).join(', ');
        
        if (normalGoals) {
            scorersHtml += '<div style="font-weight:bold;">⚽ Goals:</div>';
            scorersHtml += `<div style="margin-left: 10px; margin-bottom: 5px;">${normalGoals}</div>`;
        }
        if (penalties) {
            scorersHtml += '<div style="font-weight:bold; color:#ff00aa;">🎯 Penalties:</div>';
            scorersHtml += `<div style="margin-left: 10px; font-size:0.9rem; margin-bottom: 5px;">${penalties}</div>`;
        }
        
        // --- 2b. Saved Penalties (NEW DISPLAY) ---
        if (match.saved_penalty_goalkeepers.length > 0) {
             scorersHtml += '<div style="font-weight:bold; color:#0056b3;">🧤 Penalty Saved:</div>';
             scorersHtml += `<div style="margin-left: 10px; font-size:0.9rem; margin-bottom: 5px;">${match.saved_penalty_goalkeepers.join(', ')}</div>`;
        }


        // --- 3. Card HTML ---
        let cardsHtml = '';
        if (match.yellow_cards_recipients.length > 0) {
            cardsHtml += '<div style="font-weight:bold; color:#A1881B;">🟡 Yellow Cards:</div>';
            cardsHtml += `<div style="margin-left: 10px; font-size:0.9rem; margin-bottom: 5px;">${match.yellow_cards_recipients.join(', ')}</div>`;
        }
        
        let redCardsHtml = '';
        if (match.red_cards_recipients.length > 0) {
            redCardsHtml += '<div style="font-weight:bold; color:#CC0000;">🔴 Red Cards:</div>';
            redCardsHtml += `<div style="margin-left: 10px; font-size:0.9rem;">${match.red_cards_recipients.join(', ')}</div>`;
        }
        
        // --- 4. Title Logic ---
        let matchTitle = '';
        if (match.home_status === 'Home') {
            matchTitle = `Tamarindi F.C. vs <br> ${match.opponent}`;
        } else {
            matchTitle = `${match.opponent} vs <br> Tamarindi F.C.`;
        }

        const card = document.createElement('div');
        card.className = `match-card ${resultClass}`;
        card.innerHTML = `
            <div class="match-date">${match.date} (${match.home_status})</div>
            <div style="text-align:center; font-weight:bold; font-size:1.2rem;">
                ${matchTitle}
            </div>
            <div class="match-score">
            ${scoreDisplay}
            ${shootoutDisplay}
            </div>
            
            <div class="scorers" style="min-height: 40px; margin-bottom: 10px;">
                ${scorersHtml}
                ${cardsHtml}
                ${redCardsHtml}
            </div>
            
            <div 
                class="yt-button" 
                onclick="loadVideo(this, '${match.opponent}', '${match.date}')"
                data-opponent="${match.opponent}"
                data-date="${match.date}"
                data-video-id="${match.videoId}">>
                ▶ Search Highlights
            </div>
            <div class="video-container"></div>
        `;
        container.appendChild(card);
    });
}

// --- NEW LOAD VIDEO FUNCTION (No API Call, just Embed) ---
function loadVideo(btn, opponent, date) {
    const container = btn.nextElementSibling;
    const videoId = btn.getAttribute('data-video-id'); // Get the ID saved from the JSON

    if (container.innerHTML !== '') {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
        btn.textContent = container.style.display === 'none' ? "▶ Show Video" : "▼ Hide Video";
        return;
    }

    if (videoId && videoId !== 'None') {
        // Embed the video
        container.innerHTML = `
            <iframe 
                src="https://www.youtube-nocookie.com/embed/${videoId}" 
                allow="autoplay; encrypted-media" 
                allowfullscreen>
            </iframe>`;
        container.style.display = 'block';
        btn.textContent = "▼ Hide Video";
        btn.style.background = '#ff0000';
    } else {
        btn.textContent = "Video Not Found";
        btn.style.background = "#555";
        btn.onclick = null;
    }
}