import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

SESSION_DIR = os.path.join(os.getcwd(), "browser_session")
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)


async def fetch_notes():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=True,
            args=["--no-sandbox"]
        )
        
        page = await context.new_page()
        
        print("🚀 Navigation vers la page...")
        await page.goto("https://planete.inp-toulouse.fr", wait_until="networkidle")

        # Clic sur le bouton de connexion CAS
        await page.click("#portalCASLoginLink")
        await page.wait_for_load_state("networkidle")
        
        # Remplir les champs de login
        username = os.getenv("INP_USERNAME")
        password = os.getenv("INP_PASSWORD")
        
        await page.fill("#username", username)
        await page.fill("#password", password)
        await page.click("button[name='submit'][value='Login']")
        await page.wait_for_load_state("networkidle")
        
        # Clic sur "Dossier scolaire" (ouvre un nouvel onglet)
        async with context.expect_page() as new_page_info:
            await page.click('a.top10-link[href="https://mdw-pegase.inp-toulouse.fr/"]')
        pegase_page = await new_page_info.value
        await pegase_page.wait_for_load_state("networkidle")
        
        # Clic sur "Parcours"
        await pegase_page.click('span:has-text("Parcours")')
        await pegase_page.wait_for_selector('vaadin-button:has-text("Notes et résultats")')
        
        # Clic sur "Notes et résultats"
        await pegase_page.click('vaadin-button:has-text("Notes et résultats")')
        await pegase_page.wait_for_selector('vaadin-grid')
        
        # Extraction des données avec scroll
        data = await pegase_page.evaluate('''async () => {
            const grid = document.querySelector('vaadin-grid');
            const results = new Map();
            
            const extractVisible = () => {
                const cells = document.querySelectorAll('vaadin-grid-cell-content');
                for (let i = 0; i < cells.length; i += 2) {
                    const nameCell = cells[i];
                    const resultCell = cells[i + 1];
                    if (nameCell && resultCell) {
                        const name = nameCell.innerText.trim();
                        const result = resultCell.innerText.trim();
                        if (name && !results.has(name)) {
                            results.set(name, result);
                        }
                    }
                }
            };
            
            const scroller = grid.shadowRoot.querySelector('#table');
            if (scroller) {
                const scrollHeight = scroller.scrollHeight;
                let currentScroll = 0;
                const step = 300;
                
                while (currentScroll < scrollHeight) {
                    scroller.scrollTop = currentScroll;
                    await new Promise(r => setTimeout(r, 100));
                    extractVisible();
                    currentScroll += step;
                }
                scroller.scrollTop = scrollHeight;
                await new Promise(r => setTimeout(r, 200));
                extractVisible();
            } else {
                extractVisible();
            }
            
            return Array.from(results.entries()).map(([name, result]) => ({name, result}));
        }''')
        
        await context.close()
        
        return data
