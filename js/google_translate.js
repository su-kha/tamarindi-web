function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'it', // Your site's original language
        includedLanguages: 'en,it,es,fr,de',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
}

function triggerGoogleTranslate(langCode) {
    // 1. Find the hidden Google dropdown
    const googleCombo = document.querySelector('.goog-te-combo');
    
    if (googleCombo) {
        // 2. Set the value
        googleCombo.value = langCode;
        
        // 3. Fire the event loudly (bubbles: true is key!)
        googleCombo.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
        console.error("Error: Google Translate widget is not loaded yet.");
    }
}

// Auto-load the Google script
(function() {
    var googleScript = document.createElement('script');
    googleScript.type = 'text/javascript';
    googleScript.async = true;
    // FIXED: Added 'https:' to ensure it loads everywhere
    googleScript.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(googleScript);
})();