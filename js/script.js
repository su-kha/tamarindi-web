console.log("chi pianta tamarindi, non raccoglie tamarindi");

// Wait for the DOM (HTML) to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    console.log("DOM fully loaded and parsed");

    // 1. Find the elements
    const menuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.querySelector('.sidebar');

    // 2. Check if they exist
    if (menuBtn && sidebar) {
        console.log("Button and Sidebar found!"); // Debugging message

        // 3. Add click event
        menuBtn.addEventListener('click', function() {
            
            // Toggle the class
            sidebar.classList.toggle('open');
            
            // Update button text
            if (sidebar.classList.contains('open')) {
                menuBtn.textContent = "✕ Close Team Menu";
            } else {
                menuBtn.textContent = "☰ Open Team Menu";
            }
        });
    } else {
        console.error("Error: Could not find button or sidebar elements.");
    }

    fetch('data/website_data_cache.json')
    .then(response => response.json())
    .then(data => {
        if (data.declarations && data.declarations.length > 0) {
            const latest = data.declarations[0]; // First one is the newest
            
            const container = document.getElementById('latest-news-container');
            if (container) {
                container.style.display = 'block';
                document.getElementById('news-title').textContent = latest.title;
                document.getElementById('news-date').textContent = latest.date;
                
                // Show first 100 characters as preview
                const snippet = latest.content.substring(0, 100) + '...';
                document.getElementById('news-snippet').textContent = snippet;
            }
        }
    })
    .catch(err => console.log('No news found'));
});