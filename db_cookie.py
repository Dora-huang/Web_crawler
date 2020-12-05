#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # 等待元素加载的
from selenium.webdriver.support import expected_conditions as EC  #判断条件是否满足
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sys
reload(sys) 
sys.setdefaultencoding('utf8')   

# regexp_extract(home,'\"lng\"\:\"(.*?)\"',1) lng,regexp_extract(home,'\"lat\"\:\"(.*?)\"',1) lat

def get_cookie(usr_name,usr_pwd):
    url = 'http://news.baidu.com/?tn=news'
    driver = webdriver.Firefox()
    wait = WebDriverWait(driver, 6)
    
    driver.delete_all_cookies()
    driver.get(url)
    cookie_f = driver.get_cookies()

    login = wait.until(EC.presence_of_element_located((By.XPATH ,'//div[@id="header-wrapper"]/div[@id="usrbar"]/ul/li[3]/a[@id="passLog"]')))
    time.sleep(3)
    login.click()

    time.sleep(1)
    name = driver.find_element_by_xpath('//form[@class="pass-form pass-form-normal"]/p[5]/input[2]')
    time.sleep(1)
    usr = usr_name
    name.send_keys(usr)

    password = driver.find_element_by_xpath('//form[@class="pass-form pass-form-normal"]/p[6]/input[2]')
    time.sleep(1)
    pwd = usr_pwd
    password.send_keys(pwd)

    submit = driver.find_element_by_xpath('//form[@class="pass-form pass-form-normal"]/p[9]/input')
    time.sleep(3)
    submit.click()
    
    time.sleep(3) 
    page = driver.page_source
    # print page
    
    cookie_s = driver.get_cookies()
    # print cookie_s

    return cookie_f,cookie_s

def save_cookie(cookie,tb_txt):
    with open(tb_txt,'w') as f:
        f.write(json.dumps(cookie))
    

def read_cookie(tb_txt):
    with open(tb_txt,'r') as f:
        cookies_dict = json.loads(f.read())
    return cookies_dict

def login_with_cookie(cookies_dict=None):

    driver = webdriver.Firefox()
    driver.get("http://news.baidu.com/?tn=news")

    print driver.get_cookies()
    for i in cookies_dict:
        driver.add_cookie(i)

    driver.refresh()
    print driver.get_cookies()

if __name__ == '__main__':
    usr_name = '136xxxxx'
    usr_pwd = 'zzzzzz'
    # get_cookie(usr_name,usr_pwd)
    cookie1,cookie2 = get_cookie(usr_name,usr_pwd)
    save_cookie(cookie1,"cookie1.txt")
    save_cookie(cookie2,"cookie2.txt")
    cookies_dict = read_cookie("cookie2.txt")
    login_with_cookie(cookies_dict=cookies_dict)
    # login_with_cookie()
