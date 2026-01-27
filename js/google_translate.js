// 1. Force the function to be Global so Google can find it
window.googleTranslateElementInit = function() {
    console.log("🚀 Google Translate Script Loaded & Initializing...");
    new google.translate.TranslateElement({
        pageLanguage: 'it', // Matches your <html lang="it">
        includedLanguages: 'en,it,es,fr,de',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
}

// 2. The Trigger Function (Retries up to 20 times)
let attempts = 0;

function triggerGoogleTranslate(langCode) {
    const googleCombo = document.querySelector('.goog-te-combo');
    
    if (googleCombo) {
        // Widget Found! Change language.
        console.log("✅ Widget found. Changing language to:", langCode);
        googleCombo.value = langCode;
        googleCombo.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
        // Widget Not Found yet. Retry.
        attempts++;
        if (attempts > 20) {
            console.error("❌ Gave up finding Google Translate widget.");
            return; 
        }
        
        // Retry in 500ms
        setTimeout(() => triggerGoogleTranslate(langCode), 500);
    }
}

// 3. Load the Script (if not already loaded)
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