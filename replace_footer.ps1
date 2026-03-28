$files = Get-ChildItem -Path ".\*.html" -Recurse | Where-Object { $_.Name -ne "karriere.html" -and $_.Name -notlike "*about_head.html" }

$oldFooterRegex = '(?si)<footer[^>]*>.*?</footer>'

$newFooter = @"
        <footer class="w-full bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 py-8 relative">
            <div class="container mx-auto px-4">
                <div class="flex flex-col md:flex-row items-center justify-between gap-6 max-w-6xl mx-auto">
                    <div class="text-gray-600 dark:text-gray-400 text-sm font-medium flex-1">
                        © 2026 NextGen Insurance Forum e.V.
                    </div>
                    
                    <div class="flex-shrink-0">
                        <button onclick="openDonationModal()" class="text-gray-700 dark:text-gray-300 hover:text-[#0E4B94] dark:hover:text-[#2CD9C3] font-bold py-2 px-4 transition-colors">
                            Nur Vereinsarbeit unterstützen
                        </button>
                    </div>

                    <div class="flex flex-col md:flex-row items-center gap-6 flex-1 justify-end">
                        <div class="flex items-center gap-6">
                            <a href="impressum.html" class="text-gray-600 dark:text-gray-400 hover:text-[#0E4B94] dark:hover:text-[#2CD9C3] text-sm transition-colors">Impressum</a>
                            <a href="datenschutzerklarung.html" class="text-gray-600 dark:text-gray-400 hover:text-[#0E4B94] dark:hover:text-[#2CD9C3] text-sm transition-colors">Datenschutz</a>
                        </div>
                        <div class="flex items-center gap-4">
                            <a href="mailto:info@nextgenforum.de" class="text-gray-600 dark:text-gray-400 hover:text-[#0E4B94] dark:hover:text-[#2CD9C3] transition-colors flex items-center" aria-label="Email">
                                <span class="material-symbols-outlined" style="font-size: 1.5rem;">mail</span>
                            </a>
                            <a href="https://www.linkedin.com/company/nextgen-forum" target="_blank" rel="noopener noreferrer" class="text-gray-600 dark:text-gray-400 hover:text-[#0E4B94] dark:hover:text-[#2CD9C3] transition-colors flex items-center" aria-label="LinkedIn">
                                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"></path>
                                </svg>
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Donation Popup Modal -->
            <div id="donation-modal" class="fixed inset-0 z-[100] hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
                <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 md:p-8 relative text-left">
                    <button onclick="closeDonationModal()" class="absolute top-4 right-4 text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-white transition-colors">
                        <span class="material-symbols-outlined" style="font-size: 2rem;">close</span>
                    </button>
                    
                    <h2 class="text-3xl font-extrabold text-[#0E4B94] dark:text-[#2CD9C3] mb-6">Jetzt spenden</h2>
                    
                    <div class="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 mb-6">
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">Unsere Bankverbindung</h3>
                        <p class="text-gray-700 dark:text-gray-300 font-mono text-lg mb-1 font-bold">IBAN: DE12 3456 7890 1234 5678 90</p>
                        <p class="text-gray-600 dark:text-gray-400 mb-1">BIC: ABCDEF12XXX</p>
                        <p class="text-gray-600 dark:text-gray-400">Empfänger: NextGen Insurance Forum e.V.</p>
                    </div>
                    
                    <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mb-8">
                        Wir sind wegen Förderung der Erziehung, Volks- und Berufsbildung nach dem Freistellungsbescheid des Finanzamts XY, Steuernummer XY, vom XY als gemeinnützig anerkannt und nach § 5 Abs. 1 Nr. 9 KStG von der Körperschaftssteuer befreit.<br><br>Zusätzlich für Spenden bis 300 € gilt der Kontoauszug als offizieller Spendennachweis beim Finanzamt. Auf Wunsch stellen wir dir natürlich gerne eine separate Bescheinigung aus.
                    </p>

                    <div class="border-t border-gray-200 dark:border-gray-800 pt-6">
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Separate Bescheinigung anfordern</h3>
                        <form id="donation-receipt-form" class="space-y-4">
                            <div>
                                <label for="receipt-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deine E-Mail-Adresse</label>
                                <input type="email" id="receipt-email" required class="w-full px-4 h-12 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-[#2CD9C3] dark:text-white transition-all">
                            </div>
                            <button type="submit" class="w-full md:w-auto h-12 px-8 bg-[#0E4B94] text-white font-bold rounded-lg hover:bg-[#0a356b] transition-colors shadow-md">Abschicken</button>
                        </form>
                        <div id="receipt-success" class="hidden mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 rounded-lg flex items-center gap-3">
                            <span class="material-symbols-outlined">check_circle</span>
                            <span>Wir schicken dir eine Spendenbescheinigung zeitnah zu.</span>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                function openDonationModal() {
                    const modal = document.getElementById('donation-modal');
                    modal.classList.remove('hidden');
                    document.body.style.overflow = 'hidden';
                }
                function closeDonationModal() {
                    const modal = document.getElementById('donation-modal');
                    modal.classList.add('hidden');
                    document.body.style.overflow = '';
                }
                
                document.getElementById('donation-modal').addEventListener('click', function(e) {
                    if(e.target === this) {
                        closeDonationModal();
                    }
                });

                document.getElementById('donation-receipt-form')?.addEventListener('submit', function(e) {
                    e.preventDefault();
                    this.classList.add('hidden');
                    document.getElementById('receipt-success').classList.remove('hidden');
                });
            </script>
        </footer>
"@

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    
    if ($content -match $oldFooterRegex) {
        $content = $content -replace $oldFooterRegex, $newFooter
        [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.Encoding]::UTF8)
        Write-Host "Updated $($file.Name)"
    } else {
        Write-Host "Footer not found in $($file.Name)"
    }
}
