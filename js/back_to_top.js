document.addEventListener('DOMContentLoaded', () => {
    // 1. Create the Button Element
    const button = document.createElement('button');
    button.innerHTML = '↑ TOP'; // Retro text
    button.id = 'backToTopBtn';
    
    // 2. Create and Inject CSS (Pink & Black Retro Style)
    const style = document.createElement('style');
    style.innerHTML = `
        #backToTopBtn {
            display: none; /* Hidden by default */
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            
            /* Retro Styling */
            background-color: #ff00aa; /* Team Pink */
            color: white;
            border: 2px solid black;
            box-shadow: 3px 3px 0px black; /* Hard shadow */
            
            /* Font & Text */
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            font-size: 14px;
            padding: 10px 15px;
            cursor: pointer;
            transition: transform 0.1s;
        }

        #backToTopBtn:hover {
            background-color: black;
            color: #ff00aa;
            border-color: #ff00aa;
            transform: translate(-1px, -1px);
            box-shadow: 4px 4px 0px #ff00aa;
        }
        
        #backToTopBtn:active {
            transform: translate(2px, 2px);
            box-shadow: 1px 1px 0px black;
        }
    `;
    document.head.appendChild(style);
    document.body.appendChild(button);

    // 3. Scroll Logic (Show when scrolled down 300px)
    window.onscroll = function() {
        if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
            button.style.display = "block";
        } else {
            button.style.display = "none";
        }
    };

    // 4. Click Logic (Smooth scroll up)
    button.onclick = function() {
        window.scrollTo({top: 0, behavior: 'smooth'});
    };
});