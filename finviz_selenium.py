from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de Selenium
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')

# Initialiser le driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def login_and_go_to_screener():
    """ Se connecte à Finviz et va directement au screener sans vérifier la connexion. """
    try:
        print("🔄 Connexion à Finviz...")
        driver.get('https://elite.finviz.com/login.ashx')

        # Remplir le formulaire de connexion
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(os.getenv('FINVIZ_EMAIL'))
        driver.find_element(By.NAME, 'password').send_keys(os.getenv('FINVIZ_PASSWORD'))
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        # Pause pour laisser le temps de charger après connexion
        time.sleep(3)

        # Aller directement au screener
        driver.get('https://elite.finviz.com/screener.ashx')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.screener_table')))
        print("✅ Accès au screener réussi !")

    except Exception as e:
        print(f"❌ Erreur lors de la connexion : {str(e)}")

def extract_screener_data():
    """ Récupère les options 'Order By' et 'Signal' du screener. """
    data = {"orderby_options": {}, "signal_options": {}}

    try:
        # XPaths mis à jour
        ORDERBY_XPATH = "/html/body/div[3]/table/tbody/tr[1]/td/table/tbody/tr/td[4]/select"
        SIGNAL_XPATH = "/html/body/div[3]/table/tbody/tr[1]/td/table/tbody/tr/td[7]/select"

        # 1. Extraire les options Order By
        orderby = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, ORDERBY_XPATH)))
        ActionChains(driver).move_to_element(orderby).click().perform()  # Assurer un vrai clic
        time.sleep(1)

        options = driver.find_elements(By.XPATH, "//div[contains(@class, 'dropdown-menu')]//a")
        for option in options:
            text = option.text.strip()
            href = option.get_attribute('href')
            if text and href:
                data["orderby_options"][text] = href

        print("✅ Options 'Order By' récupérées.")

        # 2. Extraire les options Signal
        signal_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, SIGNAL_XPATH)))
        options = signal_dropdown.find_elements(By.TAG_NAME, 'option')
        for option in options:
            text = option.text.strip()
            value = option.get_attribute('value')
            if text and value:
                data["signal_options"][text] = value

        print("✅ Options 'Signal' récupérées.")
        return data

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {str(e)}")
        return None

if __name__ == "__main__":
    login_and_go_to_screener()
    screener_data = extract_screener_data()

    if screener_data:
        with open('finviz_screener_data.json', 'w', encoding='utf-8') as f:
            json.dump(screener_data, f, indent=2, ensure_ascii=False)
        print("📁 Données sauvegardées dans 'finviz_screener_data.json'")

    # Attendre avant de fermer
    input("Appuyez sur Entrée pour fermer...")
    driver.quit()

