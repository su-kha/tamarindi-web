// handle fetching Excel/JSON data

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
});