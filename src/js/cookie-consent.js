
// Cookie Consent Logic
document.addEventListener('DOMContentLoaded', () => {
    const consent = localStorage.getItem('cookie_consent');

    if (consent === 'accepted') {
        loadGoogleAds();
    } else if (consent === 'declined') {
        // Do nothing, tracking declined
    } else {
        showCookieBanner();
    }
});

function loadGoogleAds() {
    console.log("Consent erteilt: Google Ads Tracking wird geladen.");

    // Google Tag Manager Script dynamisch einfügen
    var script = document.createElement('script');
    script.src = 'https://www.googletagmanager.com/gtag/js?id=AW-17579535705';
    script.async = true;
    document.head.appendChild(script);

    // Config
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    gtag('js', new Date());
    gtag('config', 'AW-17579535705');
}

function showCookieBanner() {
    // Create Banner Element
    const banner = document.createElement('div');
    banner.id = 'cookie-consent-banner';
    banner.style.position = 'fixed';
    banner.style.bottom = '20px';
    banner.style.right = '20px';
    banner.style.width = '350px';
    banner.style.maxWidth = '90%';
    banner.style.backgroundColor = '#FFFFFF';
    banner.style.padding = '20px';
    banner.style.borderRadius = '12px';
    banner.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
    banner.style.zIndex = '9999';
    banner.style.fontFamily = '"Manrope", sans-serif'; // Assuming site font
    banner.style.display = 'flex';
    banner.style.flexDirection = 'column';
    banner.style.gap = '15px';
    banner.style.border = '1px solid #f0f0f0';

    // HTML Content
    banner.innerHTML = `
        <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #111121;">Datenschutz & Cookies</h3>
        <p style="margin: 0; font-size: 14px; color: #4B5563; line-height: 1.5;">
            Wir nutzen Cookies und Google Ads, um unsere Vereinsarbeit (Google Ad Grant) bekannter zu machen. Deine Zustimmung hilft uns dabei.
        </p>
        <div style="display: flex; gap: 10px; margin-top: 5px;">
            <button id="cookie-decline" style="flex: 1; padding: 10px; border: 1px solid #D1D5DB; background: transparent; color: #4B5563; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s;">
                Ablehnen
            </button>
            <button id="cookie-accept" style="flex: 1; padding: 10px; border: none; background: #0E4B94; color: #FFFFFF; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s;">
                Akzeptieren
            </button>
        </div>
        <div style="display: flex; gap: 15px; font-size: 12px;">
            <a href="datenschutzerklarung.html" style="color: #6B7280; text-decoration: none; hover: text-decoration: underline;">Datenschutz</a>
            <a href="impressum.html" style="color: #6B7280; text-decoration: none; hover: text-decoration: underline;">Impressum</a>
        </div>
    `;

    document.body.appendChild(banner);

    // Event Listeners
    document.getElementById('cookie-accept').addEventListener('click', () => {
        localStorage.setItem('cookie_consent', 'accepted');
        banner.remove();
        loadGoogleAds();
    });

    document.getElementById('cookie-decline').addEventListener('click', () => {
        localStorage.setItem('cookie_consent', 'declined');
        banner.remove();
    });
}
