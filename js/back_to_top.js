document.addEventListener('DOMContentLoaded', () => {
    console.log("Back to Top script loaded!"); // Debug message

    // 1. Create the Button
    const button = document.createElement('button');
    button.innerHTML = '↑ TOP'; 
    button.id = 'backToTopBtn';
    button.setAttribute('aria-label', 'Back to Top');
    
    // 2. Add Styles directly
    Object.assign(button.style, {
        display: 'none',
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: '9999',
        backgroundColor: '#ff00aa', // Team Pink
        color: 'white',
        border: '2px solid black',
        boxShadow: '3px 3px 0px black',
        fontFamily: "'Courier New', Courier, monospace",
        fontWeight: 'bold',
        fontSize: '14px',
        padding: '10px 15px',
        cursor: 'pointer',
        transition: 'transform 0.1s'
    });

    // Hover effects need to be handled via events in JS since we are using inline styles
    button.onmouseenter = () => {
        button.style.backgroundColor = 'black';
        button.style.color = '#ff00aa';
        button.style.borderColor = '#ff00aa';
        button.style.transform = 'translate(-1px, -1px)';
        button.style.boxShadow = '4px 4px 0px #ff00aa';
    };
    button.onmouseleave = () => {
        button.style.backgroundColor = '#ff00aa';
        button.style.color = 'white';
        button.style.borderColor = 'black';
        button.style.transform = 'none';
        button.style.boxShadow = '3px 3px 0px black';
    };

    document.body.appendChild(button);

    // 3. Scroll Logic (Using addEventListener is safer)
    window.addEventListener('scroll', () => {
        // Show after 100px of scrolling
        if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
    });

    // 4. Click Logic
    button.addEventListener('click', () => {
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
});