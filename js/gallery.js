let allImages = []; // Stores the list of image paths
let currentIndex = 0; // Tracks the open image

document.addEventListener('DOMContentLoaded', function() {
    fetch('data/website_data_cache.json')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('gallery-grid');
            
            if (data.gallery && data.gallery.length > 0) {
                container.innerHTML = ''; 
                
                // 1. Save all paths to the global array
                allImages = data.gallery.map(filename => `images/gallery/${filename}`);
                
                // 2. Build the grid
                allImages.forEach((imgPath, index) => {
                    const div = document.createElement('div');
                    div.className = 'gallery-item';
                    // Pass the INDEX instead of the path
                    div.innerHTML = `
                        <img src="${imgPath}" alt="Team Photo" loading="lazy" onclick="openLightbox(${index})">
                    `;
                    container.appendChild(div);
                });
            } else {
                container.innerHTML = '<p>No photos found in the archive.</p>';
            }
        })
        .catch(err => console.error(err));
});

// --- LIGHTBOX LOGIC ---

function openLightbox(index) {
    currentIndex = index;
    updateLightboxImage();
    document.getElementById('lightbox').style.display = "flex";
}

function closeLightbox() {
    document.getElementById('lightbox').style.display = "none";
}

// Called by the arrows (n is -1 or +1)
function changeSlide(n) {
    currentIndex += n;
    
    // Loop back to start/end if needed
    if (currentIndex >= allImages.length) {
        currentIndex = 0;
    } else if (currentIndex < 0) {
        currentIndex = allImages.length - 1;
    }
    
    updateLightboxImage();
}

function updateLightboxImage() {
    const img = document.getElementById('lightbox-img');
    img.src = allImages[currentIndex];
}

// Optional: Add Keyboard Navigation (Left/Right Arrow)
document.addEventListener('keydown', function(event) {
    if (document.getElementById('lightbox').style.display === "flex") {
        if (event.key === "ArrowLeft") {
            changeSlide(-1);
        } else if (event.key === "ArrowRight") {
            changeSlide(1);
        } else if (event.key === "Escape") {
            closeLightbox();
        }
    }
});