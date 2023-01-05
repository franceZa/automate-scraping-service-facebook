
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

class scraper(object):
    def __init__(self, is_init_load, browser):

        self.is_init_load = is_init_load
        self.browser = browser
        with open("conf/application.yml", 'r') as stream:
            self.conf = yaml.safe_load(stream)
        self.line_token = self.conf['user']['line_token']
        self.url = 'https://notify-api.line.me/api/notify'
        self.headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+self.line_token}

    def execute(self):
        wd = self.browser # selenium.webdriver
        wd.get("https://facebook.com") # route to facebook login
        wait = WebDriverWait(wd, 30)
        #login to facebook 
        # Read YAML file 
        user_id = self.conf['user']['username']
        my_password = self.conf['user']['password']
        # find location of input text field 
        user_name_obj = wd.find_element(By.XPATH,"//input[@type='text']")
        user_name_obj.send_keys(user_id)
        password_obj = wd.find_element(By.XPATH,"//input[@type='password']")
        password_obj.send_keys(my_password)
        # find location of login button
        log_in_bottom = wd.find_element(By.XPATH,"//button[@name='login']")
        log_in_bottom.click()

        # url changes to facebook prayutofficial
        wait.until(EC.url_changes('https://www.facebook.com/prayutofficial'))
        wd.get('https://www.facebook.com/prayutofficial')

        # store text data
        message_key = []
        raw_text={}

        #หน่วงเวลาให้ facebook โหลดทัน
        PAUSE_TIME = 5

        # Get scroll height
        last_height =1
        def getdata():
            try:
                see_more_list = wd.find_elements(By.XPATH, "//*[(text()='See more' or text()='ดูเพิ่มเติม')]") #หา elements ปุ่ม ดูเพิ่มเติม
                for s in see_more_list:
                    wd.execute_script("arguments[0].click();", s) #กดปุ่ม ดูเพิ่มเติม
                    time.sleep(2)
                # get all article or post \ หา elements ของโพสต์
                article_list = wd.find_elements(By.XPATH, "//div[@role='article' and @aria-posinset != '']")
                # get article text \ หา elements ของข้อความ
                all_text_list = wd.find_elements(By.XPATH,f"//*[@data-ad-comet-preview='message']")

                # for index,a in enumerate(all_text_list):
                #     print(f'index: {index}, t: {str(a.text)[:50]}')
                #logic-> facebook render ใหม่ทุกครั้งที่เลื่อนลงซึ่งเวลา scroll ลงเราจะได้ text ทั้งของเดิม+อันที่ render มาใหม่
                #ดังนั้นสร้าง message_key มาเก็บ article ที่ซ้ำของเดิมถ้าไม่ซ้ำให้ append message_key 

                for index,a in enumerate(article_list):
                    id_ = str(a.get_attribute('aria-describedby')).split(' ')  
                    print(f'index: {index} id_ {id_}') 
                    text_block = id_[1]
                    # if already have an article then pass 
                    if (text_block in message_key) == False:
                        print(f'index: {index} id_ {text_block} append') 
                        message_key.append(text_block)
                        # store article i to raw_text 
                        raw_text[text_block] = str(all_text_list[index].text).strip()
                        print(f'index: {index} id_ {text_block} text {str(all_text_list[index].text)[:10]}') 
                    elif len(raw_text[text_block]) == 0:
                        raw_text[text_block] = str(all_text_list[index].text).strip()
                        print(f'index: {index} id_ {text_block} text {str(all_text_list[index].text)[:10]}')
                #print(f'raw_text {raw_text}')
                new_height = wd.execute_script("return document.body.scrollHeight")
                return new_height
            except NoSuchElementException:
                # error failed: Element not found. (0x490)
                return 'err'

        def scroll():
            # scroll down to load data
                new_height = getdata()
                wd.execute_script("window.scrollTo({ left: 0, top: document.body.clientHeight, behavior: 'smooth' })")
                new_height = wd.execute_script("return document.body.scrollHeight")
                # set wait for load web page
                time.sleep(PAUSE_TIME)

                return new_height
         

        while True:
            # Scroll down to bottom
            if self.is_init_load:
                new_height=scroll()
                # Calculate new scroll height and compare with last scroll height
                if new_height == last_height or new_height=='err':
                    break
                last_height = new_height
            else:
                new_height = scroll() #เก็บโพสต์ 1,2,3 เเล้วเลื่อนลงเพื่อโหลดข้อมูล
                new_height = scroll() #เก็บโพสต์ 4,5,6 เเล้วเลื่อนลงเพื่อโหลดข้อมูล เเล้วหยุด
                break

        ID = []
        text_value = []
        for k,v in raw_text.items():
            ID.append(k)
            text_value.append(v)
        
        df = pd.DataFrame({'id':ID,'text':text_value})
        current_dateTime = datetime.now().strftime('%y-%m-%d')
        #token for access cloud storage
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'conf/facebook-scraping-373515-fe5dfaaf7d48.json'
        df.to_parquet(f"prayutofficial_data_{current_dateTime}.parquet")
        #facebook-scraping-payut-test
     
        df.to_parquet(f"gs://facebook-scraping-payut-test/prayutofficial_data_{current_dateTime}.parquet")
        print(df)
        print('fin')
        #time.sleep(1000)
        msg = f'prayutofficial_data_{current_dateTime} ok'
        r = requests.post(self.url, headers=self.headers, data = {'message':msg})
  



