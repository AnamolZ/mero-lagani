"""
MeroShare Scraping Service

Provides automation utilities for interacting with the MeroShare portal
via Selenium WebDriver. Handles browser initialization, authentication,
and extraction of currently available share issues (IPO, FPO, etc.).
"""

import time
import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

load_dotenv()

class MeroShare:
    """
    Service class responsible for browser automation against the
    MeroShare web portal.
    """

    def __init__(self) -> None:
        """
        Initializes the Selenium WebDriver and wait handler.
        """
        self.driver: Optional[WebDriver] = None
        self.wait: Optional[WebDriverWait] = None
        self.setup_driver()

    def setup_driver(self) -> None:
        """
        Configures and launches a headless Chrome browser instance.

        Uses webdriver-manager to automatically download and manage
        the appropriate ChromeDriver binary.
        """
        logger.info("Setting up Chrome driver...")

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  
        options.add_argument("--no-sandbox")  
        options.add_argument("--disable-dev-shm-usage")  
        options.add_argument("--start-maximized")

        service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

        logger.info("Chrome driver initialized successfully.")

    def login(self, dp_id: str, username: str, password: str) -> None:
        """
        Logs into the MeroShare portal.

        Args:
            dp_id: Depository Participant ID
            username: Account username
            password: Account password

        Raises:
            Exception: If login flow fails
        """
        if not self.driver or not self.wait:
            logger.error("Driver not initialized. Cannot login.")
            return

        try:
            logger.info("Opening login page...")
            self.driver.get("https://meroshare.cdsc.com.np/#/login")

            # Select DP ID from dropdown
            logger.info("Selecting DP ID...")
            dp_dropdown = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".select2-selection--single, .ng-select-container, #selectBranch")
                )
            )
            dp_dropdown.click()

            # Search DP ID
            search_input = self.wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input.select2-search__field, input[type='search']")
                )
            )
            search_input.clear()
            search_input.send_keys(dp_id)

            time.sleep(1)  
            search_input.send_keys(Keys.ENTER)

            # Enter username
            logger.info("Entering username...")
            username_field = self.wait.until(
                EC.visibility_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(username)

            # Enter password
            logger.info("Entering password...")
            password_field = self.wait.until(
                EC.visibility_of_element_located((By.ID, "password"))
            )
            password_field.clear()
            password_field.send_keys(password)

            # Submit login
            logger.info("Submitting login form...")
            login_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.btn-login, button[type='submit'], .sign-in-here")
                )
            )
            login_btn.click()

            logger.info("Login submitted. Waiting for dashboard...")
            time.sleep(1)

        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise

    def get_current_issues(self) -> List[Dict[str, Any]]:
        """
        Navigates to 'My ASBA' and extracts active share issues.

        Returns:
            List of dictionaries containing:
            - company_name
            - sub_group
            - share_type
        """
        if not self.driver or not self.wait:
            logger.error("Driver not initialized.")
            return []

        found_issues: List[Dict[str, Any]] = []

        try:
            logger.info("Navigating to My ASBA...")

            # Attempt sidebar expansion if minimized
            try:
                sidebar_toggle = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class,'sidebar-minimizer--header')]")
                    )
                )
                sidebar_toggle.click()
            except Exception:
                logger.debug("Sidebar toggle not available.")

            # Open My ASBA section
            my_asba_link = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@href='#/asba' and span[text()='My ASBA']]")
                )
            )
            my_asba_link.click()

            logger.info("Scanning for share issues...")

            try:
                companies = self.wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.company-list")
                    )
                )
            except Exception:
                logger.info("No issues detected (timeout).")
                return []

            if not companies:
                logger.info("No active issues found.")
                return []

            logger.info(f"Found {len(companies)} active issues.")

            # Extract details from each company card
            for idx, comp in enumerate(companies, start=1):
                try:
                    company_name = comp.find_element(
                        By.CSS_SELECTOR, "span[tooltip='Company Name']"
                    ).text.strip()

                    sub_group = comp.find_element(
                        By.CSS_SELECTOR, "span[tooltip='Sub Group']"
                    ).text.strip()

                    share_type = comp.find_element(
                        By.CSS_SELECTOR, "span.share-of-type"
                    ).text.strip()

                    logger.info(f"{idx}. {company_name} | {sub_group} | {share_type}")

                    found_issues.append(
                        {
                            "company_name": company_name,
                            "sub_group": sub_group,
                            "share_type": share_type,
                        }
                    )

                except Exception as e:
                    logger.warning(f"Failed parsing issue #{idx}: {e}")

        except Exception as e:
            logger.error(f"Issue retrieval failed: {e}")

        return found_issues

    def close(self) -> None:
        """
        Safely terminates the WebDriver session.
        """
        logger.info("Closing browser...")
        if self.driver:
            self.driver.quit()
        logger.info("Browser closed.")


def main() -> None:
    """
    Entry point for standalone execution.

    Loads credentials from environment variables and runs the
    scraping workflow.
    """
    dp_id = os.getenv("MEROSHARE_DP_ID")
    username = os.getenv("MEROSHARE_USERNAME")
    password = os.getenv("MEROSHARE_PASSWORD")

    if not all([dp_id, username, password]):
        logger.error("Missing credentials in environment.")
        return

    mero_share = MeroShare()

    try:
        mero_share.login(dp_id, username, password)
        mero_share.get_current_issues()
    except Exception:
        logger.exception("Automation failed.")
    finally:
        mero_share.close()


if __name__ == "__main__":
    main()