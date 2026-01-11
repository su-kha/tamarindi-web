// 1. Initialize Google Translate
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'it', // Your site language
        includedLanguages: 'en,it,es,fr,de',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
}

// 2. The Trigger Function with "Polling" (Retry Logic)
function triggerGoogleTranslate(langCode) {
    const googleCombo = document.querySelector('.goog-te-combo');
    
    if (googleCombo) {
        // SUCCESS: It exists! Change the value.
        googleCombo.value = langCode;
        googleCombo.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
        // FAIL: It's not ready yet. Wait 500ms and try again.
        console.log("Google Translate widget not ready... retrying.");
        setTimeout(() => triggerGoogleTranslate(langCode), 500);
    }
}

// 3. Auto-load the Google Script (HTTPS forced)
(function() {
    // Check if script is already added to prevent duplicates
    if (!document.getElementById('google-translate-script')) {
        var googleScript = document.createElement('script');
        googleScript.id = 'google-translate-script';
        googleScript.type = 'text/javascript';
        googleScript.async = true;
        googleScript.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(googleScript);
    }
})();