document.addEventListener('DOMContentLoaded', function() {
    fetch('data/website_data_cache.json')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('gallery-grid');
            
            if (data.gallery && data.gallery.length > 0) {
                container.innerHTML = ''; // Clear loading message
                
                data.gallery.forEach(filename => {
                    const imgPath = `images/gallery/${filename}`;
                    
                    const div = document.createElement('div');
                    div.className = 'gallery-item';
                    div.innerHTML = `
                        <img src="${imgPath}" alt="Team Photo" loading="lazy" onclick="openLightbox('${imgPath}')">
                    `;
                    container.appendChild(div);
                });
            } else {
                container.innerHTML = '<p>No photos found in the archive.</p>';
            }
        })
        .catch(err => console.error(err));
});

// Lightbox Logic
function openLightbox(src) {
    const lightbox = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');
    
    img.src = src;
    lightbox.style.display = "flex";
}

function closeLightbox() {
    document.getElementById('lightbox').style.display = "none";
}