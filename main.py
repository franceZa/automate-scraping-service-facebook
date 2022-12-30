# main.py

from flask import Flask, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary  # Adds chromedriver binary to path
import cafestorythailand 
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
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)

browser = webdriver.Chrome(chrome_options=chrome_options)
#browser.get("http://0.0.0.0:8081/")

@app.route("/",methods=[ "POST","GET"])
def home():
    # browser.get("https://www.shopmoment.com") # for test
    # file_name = 'test.png'
    # browser.save_screenshot(file_name)
    # return send_file(file_name)

    is_init_load = False
    app_cafe = cafestorythailand.scrap_cafestorythailand(is_init_load,browser)
    app_cafe.execute()
    #browser.close()
    return ('hello world!',204)
    

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))