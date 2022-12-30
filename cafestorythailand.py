
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import sys
import pandas as pd
import numpy as np
import yaml
import os
import argparse
from datetime import datetime
from google.cloud import storage
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests

class scrap_cafestorythailand(object):
    def __init__(self, is_init_load, browser):

        self.is_init_load = is_init_load
        self.browser = browser
        with open("conf/application.yml", 'r') as stream:
            self.conf = yaml.safe_load(stream)
        self.line_token = self.conf['user']['line_token']
        self.url = 'https://notify-api.line.me/api/notify'
        self.headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+self.line_token}
        #print('x')
    def execute(self):
        #print('x')
        wd = self.browser

        wd.get("https://facebook.com")
        wait = WebDriverWait(wd, 30)

        #login to facebook 
        # Read YAML file
        
        user_id = self.conf['user']['username']
        my_password = self.conf['user']['password']
        user_name_obj = wd.find_element(By.XPATH,"//input[@type='text']")
        user_name_obj.send_keys(user_id)
        password_obj = wd.find_element(By.XPATH,"//input[@type='password']")
        password_obj.send_keys(my_password)
        log_in_bottom = wd.find_element(By.XPATH,"//button[@name='login']")
        log_in_bottom.click()

        wait.until(EC.url_changes('https://www.facebook.com/cafestorythailand/'))
        wd.get('https://www.facebook.com/cafestorythailand/')


        # store text data

        message_key = []
        raw_text={}


        PAUSE_TIME = 5

        # Get scroll height
        last_height =1

        def scroll_and_getdata():
            # scroll down to load data
            try:
                wd.execute_script("window.scrollTo({ left: 0, top: document.body.clientHeight, behavior: 'smooth' })")
                new_height = wd.execute_script("return document.body.scrollHeight")
                #print(f'new_height {new_height}')
                # set wait for load web page

                #sleep = int(np.log(new_height))
                time.sleep(PAUSE_TIME)
                #print(f'sleep {sleep}')

                # cick all See more buton
                see_more_list = wd.find_elements(By.XPATH, "//*[(text()='See more' or text()='ดูเพิ่มเติม')]")
                for s in see_more_list:
                    wd.execute_script("arguments[0].click();", s)
                    time.sleep(1)
                # get all article or post
                article_list = wd.find_elements(By.XPATH, "//div[@role='article' and @aria-posinset != '']")
                # get article text
                all_text_list = wd.find_elements(By.XPATH,f"//*[@data-ad-comet-preview='message']")

                #logic-> facebook render ใหม่ทุกครั้งที่เลื่อนลงซึ่งเวลา scroll ลงเราจะได้ text ทั้งของเดิม+อันที่ render มาใหม่
                #ดังนั้นสร้าง message_key มาเก็บ article ที่ซ้ำของเดิมถ้าไม่ซ้ำให้ append message_key 

                for index,a in enumerate(article_list):
                    id_ = str(a.get_attribute('aria-describedby')).split(' ')   
                    #up_load_block = id_[0]
                    text_block = id_[1]
                    # if already have an article then pass 
                    if (text_block in message_key) ==False :
                        message_key.append(text_block)
                        # store article i to raw_text 
                        raw_text[text_block] = all_text_list[index].text
                #print(f'article_list {len(article_list)}')
                #print(f'raw_text_list {len(all_text_list)}')
                return new_height
            except NoSuchElementException:
                # error failed: Element not found. (0x490)
                return 'err'

        while True:
            # Scroll down to bottom
            if self.is_init_load:
                new_height=scroll_and_getdata()
                # Calculate new scroll height and compare with last scroll height
                if new_height == last_height or new_height=='err':
                    break
                last_height = new_height
            else:
                scroll_and_getdata()
                break

        ID = []
        text_value = []
        for k,v in raw_text.items():
            ID.append(k)
            text_value.append(v)

        df = pd.DataFrame({'id':ID,'text':text_value})
        #print(df)
        current_dateTime = datetime.now().strftime('%y-%m-%d')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'conf/secret-bucksaw-369808-389cbbff5ede.json'
        df.to_parquet(f"gs://review_data_set/raw_data/cafestorythailand/cafestorythailand_data_{current_dateTime}.parquet")
        
        

        msg = f'cafestorythailand_data_{current_dateTime} ok'
        r = requests.post(self.url, headers=self.headers, data = {'message':msg})
        #print (r.text)


    #docker build -t cafe:1 .
    #Flask==1.1.1
    # gunicorn==20.0.4
    # selenium==3.141.0
    # chromedriver-binary==79.0.3945.36    


