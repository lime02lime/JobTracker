from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#openai:
from openai import OpenAI

def take_screenshot(url, screenshot_path):
    # Set up the WebDriver (ensure you have the path to your Edge WebDriver)
    edge_options = EdgeOptions()
    edge_options.add_argument("--headless")  # Run headlessly
    edge_options.add_argument("--disable-gpu")
    #edge_options.add_argument("--window-size=1920x1080")

    service = EdgeService('C:\Program Files\edgedriver_win64\msedgedriver.exe')  # Replace with your path to edgedriver
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        # Open the webpage
        driver.get(url)

        # Optionally, wait for certain elements to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Get the dimensions of the page
        total_width = driver.execute_script("return document.body.scrollWidth")
        total_height = driver.execute_script("return document.body.scrollHeight")

        # Set the window size to the dimensions of the page
        driver.set_window_size(total_width, total_height)

        # Take the screenshot
        driver.save_screenshot(screenshot_path)

        print(f"Screenshot saved to {screenshot_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()
