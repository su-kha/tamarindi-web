// 1. Initialize Google Translate
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'it',
        includedLanguages: 'en,it,es,fr,de',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
}

// 2. The Trigger Function (with 20 retries max)
let attempts = 0;

function triggerGoogleTranslate(langCode) {
    // Look for the dropdown
    const googleCombo = document.querySelector('.goog-te-combo');
    const container = document.getElementById('google_translate_element');

    if (googleCombo) {
        console.log("Success: Widget found!");
        googleCombo.value = langCode;
        googleCombo.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
        // Debugging info
        attempts++;
        if (attempts > 20) {
            console.error("Gave up finding Google Translate. Check if 'google_translate_element' div exists in HTML.");
            return; 
        }

        console.log(`Attempt ${attempts}: Widget not ready yet...`);
        
        // Check if the container itself exists (to rule out HTML errors)
        if (!container) {
            console.error("CRITICAL ERROR: <div id='google_translate_element'> is missing from the page!");
        }

        // Retry in 500ms
        setTimeout(() => triggerGoogleTranslate(langCode), 500);
    }
}

// 3. Auto-load Script
(function() {
    if (!document.getElementById('google-translate-script')) {
        var googleScript = document.createElement('script');
        googleScript.id = 'google-translate-script';
        googleScript.type = 'text/javascript';
        googleScript.async = true;
        googleScript.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(googleScript);
    }
})();