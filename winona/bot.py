from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import json
from datetime import datetime
from dotenv import load_dotenv

class WebScraper:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Create data directory if it doesn't exist
        self.data_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Set up Chrome options
        chrome_options = Options()
        # Uncomment the line below if you want to run Chrome in headless mode
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        
        # Set download directory
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.data_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        
        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        """
        Login to Magis5 website with reCAPTCHA token
        """
        try:
            # Get credentials from environment variables
            username = os.getenv('MAGIS5_USERNAME')
            password = os.getenv('MAGIS5_PASSWORD')
            recaptcha_token = os.getenv('MAGIS5_RECAPTCHA_TOKEN')
            
            if not all([username, password, recaptcha_token]):
                raise ValueError("Credentials or reCAPTCHA token not found in environment variables")
            
            # Navigate to login page
            self.driver.get("https://app.magis5.com.br/v2/admin/autenticacao/login.php")
            
            # Wait for login form to be present and enter credentials using XPath
            username_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="login"]'))
            )
            password_field = self.driver.find_element(By.XPATH, '//*[@id="password"]')
            
            # Enter credentials
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Inject reCAPTCHA token using JavaScript
            self.driver.execute_script(f"""
                document.getElementById('g-recaptcha-response').innerHTML = '{recaptcha_token}';
                document.getElementById('g-recaptcha-response').style.display = 'block';
            """)
            
            # Wait a moment for the token to be processed
            time.sleep(2)
            
            # Find and click login button using XPath
            login_button = self.driver.find_element(By.XPATH, '//*[@id="kt_login_signin_submit"]')
            login_button.click()
            
            # Wait for login to complete and check for successful login
            time.sleep(5)
            
            # Check if login was successful by looking for the user toggle element
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="kt_quick_user_toggle"]'))
                )
                print("Login successful - User toggle element found")
                return True
            except:
                print("Login failed - Could not find user toggle element")
                return False
                
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def navigate_to_report(self):
        """
        Navigate to the financial report page and generate report
        """
        try:
            # Wait after login
            time.sleep(5)
            
            # Click on Finance menu
            finance_menu = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="menu-financeiro"]/span[1]'))
            )
            finance_menu.click()
            
            # Click on Product Report submenu
            product_report = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="submenu-financeiro-relatorioporproduto"]/span[2]'))
            )
            product_report.click()
            
            # Wait for page to load
            time.sleep(5)
            
            # Set the date
            date_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="data1"]'))
            )
            date_field.clear()
            date_field.send_keys("01/04/2025")
            
            # Click submit button
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="submit"]'))
            )
            submit_button.click()
            
            # Wait for report to generate
            time.sleep(3)
            
            # Click export button
            export_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="divAccordionButtons"]/div/div[2]/div[2]/a'))
            )
            export_button.click()
            
            # Click Excel export option
            excel_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="exportTableXLS"]/li/span/span'))
            )
            excel_option.click()
            
            # Wait for download to complete
            time.sleep(5)
            
            # Get the most recent file in the download directory
            files = os.listdir(self.data_dir)
            if files:
                # Get the most recent file
                latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(self.data_dir, x)))
                
                # Generate timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Create new filename
                new_filename = f"orders_{timestamp}.xls"
                
                # Rename the file
                old_path = os.path.join(self.data_dir, latest_file)
                new_path = os.path.join(self.data_dir, new_filename)
                os.rename(old_path, new_path)
                
                print(f"File saved as: {new_filename}")
                return True
            else:
                print("No file was downloaded")
                return False
            
        except Exception as e:
            print(f"Report generation failed: {str(e)}")
            return False

    def close(self):
        """
        Close the browser
        """
        self.driver.quit()

def main():
    # Initialize the scraper
    scraper = WebScraper()
    
    try:
        # Login
        if scraper.login():
            print("Login successful")
            
            # Navigate to report and generate it
            if scraper.navigate_to_report():
                print("Report generated and downloaded successfully")
        else:
            print("Failed to login")
    
    finally:
        # Always close the browser
        scraper.close()

if __name__ == "__main__":
    main()
