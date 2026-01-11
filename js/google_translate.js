function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'it', // The language you wrote the site in
        includedLanguages: 'en,it,es,fr,de', // Languages you want to offer
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
}

// Auto-load the Google script
(function() {
    var googleScript = document.createElement('script');
    googleScript.type = 'text/javascript';
    googleScript.async = true;
    googleScript.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(googleScript);
})();