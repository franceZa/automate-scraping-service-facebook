from flask import Flask, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary  # Adds chromedriver binary to path
import scrapper_facebook # scraping file
import time
import requests
import os
app = Flask(__name__)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1024,768")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage') 
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
prefs = {"profile.default_content_setting_values.notifications" : 2} # block notifications
chrome_options.add_experimental_option("prefs",prefs)
browser = webdriver.Chrome(chrome_options=chrome_options)


@app.route("/",methods=[ "POST","GET"])
def home():

    is_init_load = False
    app_cafe = scrapper_facebook.scraper(is_init_load,browser)
    app_cafe.execute()
    #browser.close()
    return ('hello world!',204)
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))