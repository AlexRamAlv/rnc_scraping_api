from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'app':'running',
        'make a post': 'for scraping info'
    })
@app.route('/scrape', methods=['POST'])
def scrape_rnc():
    data = request.json
    rnc_number = data.get('rnc_number')
    
    if not rnc_number:
        return jsonify({'error': 'RNC number is required'}), 400
    
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)
    try:
        

        # Open the web page
        url = "https://dgii.gov.do/app/WebApps/ConsultasWeb/consultas/rnc.aspx"
        driver.get(url)

        # Wait for the input element to be present
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_cphMain_txtRNCCedula"))
        )

        # Enter the RNC number into the input box
        input_box.send_keys(rnc_number)

        # Click the search button
        search_button = driver.find_element(By.ID, "ctl00_cphMain_btnBuscarPorRNC")
        search_button.click()

        # Wait for the results to load (adjust the waiting time if necessary)
        time.sleep(5)

        # Extract the desired information from the parsed HTML
        RNC_element = driver.find_element(By.CSS_SELECTOR, "tbody > tr:nth-child(1) > td:nth-child(2)")
        enterprise_name_element = driver.find_element(By.CSS_SELECTOR, "tbody > tr:nth-child(2) > td:nth-child(2)")
        economic_activity_element = driver.find_element(By.CSS_SELECTOR, "tbody > tr:nth-child(7) > td:nth-child(2)")

        if enterprise_name_element and economic_activity_element and RNC_element:
            enterprise_name = enterprise_name_element.text
            economic_activity = economic_activity_element.text
            RNC = RNC_element.text

        else:
            enterprise_name = "Not Found"

        # Close the WebDriver
        driver.quit()

        return jsonify({"enterprise_name": enterprise_name, "economic activity": economic_activity, "Tax ID": RNC})

    except Exception as e:
        driver.quit()
        return jsonify({"error": "Check RNC; it does not exist or it is not well written"}), 500

if __name__ == '__main__':
    app.run()
