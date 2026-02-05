
import time
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MeroShare:
    def __init__(self) -> None:
        self.driver: Optional[WebDriver] = None
        self.wait: Optional[WebDriverWait] = None
        self.setup_driver()

    def setup_driver(self) -> None:
        logger.info("Setting up Chrome driver...")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("Chrome driver initialized successfully.")

    def login(self, dp_id: str, username: str, password: str) -> None:
        """
        Perform login operation with provided credentials.

        Args:
            dp_id (str): Depository Participant ID.
            username (str): User login name.
            password (str): User login password.
        
        Raises:
            Exception: If login fails or elements are not found.
        """
        if not self.driver or not self.wait:
            logger.error("Driver not initialized. Cannot proceed with login.")
            return

        try:
            logger.info("Navigating to MeroShare login page...")
            self.driver.get("https://meroshare.cdsc.com.np/#/login")
            
            logger.info("Selecting DP ID...")
            dp_dropdown = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".select2-selection--single, .ng-select-container, #selectBranch")))
            dp_dropdown.click()
            
            search_input = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field, input[type='search']")))
            search_input.clear()
            search_input.send_keys(dp_id)
            time.sleep(1)
            search_input.send_keys(Keys.ENTER)
            
            logger.info("Entering username...")
            username_field = self.wait.until(EC.visibility_of_element_located((By.ID, "username")))
            username_field.clear()
            username_field.send_keys(username)
            
            logger.info("Entering password...")
            password_field = self.wait.until(EC.visibility_of_element_located((By.ID, "password")))
            password_field.clear()
            password_field.send_keys(password)
            
            logger.info("Submitting login credentials...")
            login_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-login, button[type='submit'], .sign-in-here")))
            login_btn.click()
            
            logger.info("Login action completed. Waiting for verification...")
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"An error occurred during login: {e}")
            raise e

    def get_current_issues(self) -> None:
        """
        Navigates to the 'My ASBA' section and extracts currently available issues.

        This method identifies active IPOs, FPOs, and Right Shares by parsing
        the company list on the ASBA dashboard and logging the details.
        """
        if not self.driver or not self.wait:
            logger.error("Driver not initialized.")
            return

        try:
            logger.info("Navigating to My ASBA...")
            try:
                sidebar_toggle = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'sidebar-minimizer--header')]")))
                sidebar_toggle.click()
            except Exception:
                logger.debug("Sidebar minimizer not found or not clickable, proceeding...")

            my_asba_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#/asba' and span[text()='My ASBA']]")))
            my_asba_link.click()
            
            logger.info("Scanning for available shares...")
            try:
                companies = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.company-list")))
            except Exception:
                 logger.info("No company list found (timeout).")
                 return

            if not companies:
                logger.info("No current issues found.")
                return

            logger.info(f"Found {len(companies)} active issues:")
            
            for idx, comp in enumerate(companies, 1):
                try:
                    company_name_elem = comp.find_element(By.CSS_SELECTOR, "span[tooltip='Company Name']")
                    company_name = company_name_elem.text.strip()
                    
                    sub_group_elem = comp.find_element(By.CSS_SELECTOR, "span[tooltip='Sub Group']")
                    sub_group = sub_group_elem.text.strip()
                    
                    share_type_elem = comp.find_element(By.CSS_SELECTOR, "span.share-of-type")
                    share_type = share_type_elem.text.strip()
                    
                    logger.info(f"{idx}. {company_name} | {sub_group} | {share_type}")
                except Exception as e:
                    logger.warning(f"Error parsing company info for item {idx}: {e}")

        except Exception as e:
            logger.error(f"Failed to fetch current issues: {e}")

    def close(self) -> None:
        logger.info("Closing driver...")
        if self.driver:
            self.driver.quit()
        logger.info("Driver closed.")

def main() -> None:
    dp_id = os.getenv("MEROSHARE_DP_ID")
    username = os.getenv("MEROSHARE_USERNAME")
    password = os.getenv("MEROSHARE_PASSWORD")

    if not all([dp_id, username, password]):
        logger.error("Missing environment variables. Please check your .env file.")
        return

    mero_share = MeroShare()
    try:
        mero_share.login(dp_id, username, password) # type: ignore
        mero_share.get_current_issues()
    except Exception:
        logger.exception("Automation failed.")
    finally:
        mero_share.close()

if __name__ == "__main__":
    main()