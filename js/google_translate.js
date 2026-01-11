// 1. Initialize Google Translate
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'it', 
        includedLanguages: 'en,it,es,fr,de',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
}

// 2. The Safe Trigger Function
function triggerGoogleTranslate(langCode) {
    const googleCombo = document.querySelector('.goog-te-combo');
    
    if (googleCombo) {
        googleCombo.value = langCode;
        googleCombo.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
        console.warn("Google Translate is not ready yet. Retrying...");
        // If not ready, wait 500ms and try again
        setTimeout(() => triggerGoogleTranslate(langCode), 500);
    }
}

// 3. Load the Script
(function() {
    var googleScript = document.createElement('script');
    googleScript.type = 'text/javascript';
    googleScript.async = true;
    googleScript.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(googleScript);
})();