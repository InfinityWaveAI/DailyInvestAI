"""
Module for setting up Selenium WebDriver for scraping Twitter (X).

Functions:
- setup_web_driver(): Configures and initializes a Selenium WebDriver instance.

"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def setup_web_driver():
    """
    Sets up and initializes a Selenium WebDriver instance for Chrome.

    Returns:
    - webdriver.Chrome: A Selenium WebDriver instance with Chrome configuration.
    """
    # Configure Chrome options (add custom options here if needed)
    chrome_options = Options()

    # Use WebDriverManager to handle driver installation
    service = Service(executable_path=CM().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to Twitter login page
    driver.get('https://x.com/search?q=%28%23Cake%29+until%3A2019-11-21+since%3A2006-12-17&src=typed_query&f=live')

    # Example login flow (replace placeholders with real credentials if automating login)
    try:
        # Enter username
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input'))
        )
        element.send_keys('@ganeshlocalapp')  # username
        time.sleep(2)

        # Click 'Next' button
        driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]/div/span/span').click()

        # Enter password
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'))
        )
        element.send_keys('Get$et@1cr')  # password
        time.sleep(2)

        # Click 'Login' button
        driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button/div/span/span').click()
        time.sleep(5)

    except Exception as e:
        print("Error during login setup:", e)

    return driver