import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class LinkChecker:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")

        self.driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

    def check_link(self, url):
        try:
            self.driver.get(url)
            time.sleep(1)

            try:
                betaal_button = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.TAG_NAME, "sfc-button"))
                )
                if betaal_button.is_displayed():
                    return "werkend"
                else:
                    return "verlopen"
            except Exception as e:
                print(f"Error: {e}")
                return "verlopen"

        except Exception as e:
            print(f"Error while loading the page: {e}")
            return "verlopen"
        finally:
            self.driver.quit()

