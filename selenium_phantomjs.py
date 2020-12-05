#!/usr/bin/env python
# -*-coding:utf-8 -*-

import time                
import re                
import sys      
import codecs          
from selenium import webdriver            
from selenium.webdriver.common.keys import Keys
import urllib2
from bs4 import BeautifulSoup
import pandas
import urlparse
from selenium.webdriver.common.action_chains import ActionChains

import seaborn as sb
import chardet
import socket

# reload(sys)
# sys.setdefaultencoding('utf-8')
# socket.setdefaulttimeout(120)  #超过2分钟后自动跳出 （try catch 函数）

def download(url,user_agent='wswp',num_retries=2):
    print 'Dowloading:',url
    headers={'User_agent':user_agent}
    request=urllib2.Request(url,headers=headers)
    html=urllib2.urlopen(request).read()
    return html

def download_01(url,user_agent='wswp',num_retries=2):
    print 'Dowloading:',url
    headers={'User_agent':user_agent}
    try:
        request=urllib2.Request(url,headers=headers)
        html=urllib2.urlopen(request).read()
    except socket.error:
        errno, errstr = sys.exc_info()[:2]
        request=urllib2.Request(url,headers=headers)

def get_detail(div_one,brand_len):
    #将brand_info(brand)和price写入dataFrame中
    pro_div_head = div_one.find('div',attrs={'class':"pro-intro"}).find('h3').get_text().strip()
    detail['brand_info'].append(pro_div_head)
    detail['brand'].append(pro_div_head[0:brand_len])
    detail['model'].append(pro_div_head[brand_len:].split(u'（')[0].strip())
    try:
        pro_div_param = div_one.find('div',attrs={'class':"pro-intro"}).find('ul',attrs={'class':"param clearfix"}).find_all('li')
    except Exception as e:
        print e
    finally:
        try:
            pri_div=div_one.find('div',attrs={'class':"price-box"}).find('span',attrs={'class':"price price-normal"}).find('b',attrs={'class':"price-type"}).get_text().strip()
        except Exception as e:
            try:
                pri_div=div_one.find('div',attrs={'class':"price-box"}).find('span',attrs={'class':"price price-na"}).find('b',attrs={'class':"price-type"}).get_text().strip()
            except Exception as e:
                try:
                    pri_div=div_one.find('div',attrs={'class':"price-box"}).find('span',attrs={'class':"price price-sp-num"}).find('b',attrs={'class':"price-type"}).get_text().strip()
                except Exception as e:
                    try:
                        pri_div=div_one.find('div',attrs={'class':"price-box"}).find('span',attrs={'class':"price price-np-num"}).find('b',attrs={'class':"price-type"}).get_text().strip()
                    except Exception as e:
                        pri_div=u"null"
        detail.setdefault('price',[]).append(pri_div)
        #所有参数写入dataFrame中
        try:
            for t in range(0,len(pro_div_param)):
                span=pro_div_param[t].find('span').get_text().strip()
                if detail.has_key(span) == True:
                    detail[span].append(pro_div_param[t]['title'].strip())
                else:
                    detail.setdefault(span,[]).append(pro_div_param[t]['title'].strip())
        except Exception as e:
            print e
        return detail

def get_one_page(brand_url,brand_len):
    global detail
    detail = {}
    detail.setdefault('brand',[])
    detail.setdefault('price',[])
    detail.setdefault('brand_info',[])
    detail.setdefault('model',[])
    html = download(brand_url)
    soup = BeautifulSoup(html,'lxml')
    #获取第一条记录
    div_one = soup.find('div',attrs={'class':"list-item item-one clearfix"})
    get_detail(div_one,brand_len)
    #获取一下记录
    div_ones = soup.find_all('div',attrs={'class':'list-item clearfix'})
    for i in range(0,len(div_ones)):
        get_detail(div_ones[i],brand_len)
    global df
    df = df.append(pandas.DataFrame(detail.values(),index=detail.keys()).T)
    return df
    

def crawl(url,i,brand_len):
    driver.get(url)
    each_xpath = "//div[@id='J_ParamBrand']/a[%d]" % (int(i)+1)
    print each_xpath 
    driver.find_element_by_xpath(each_xpath).click()
    #driver.find_element_by_xpath("//div[@id='J_ParamBrand']/a[1]").click()
    print "click button_brand successfully......."
    brand_url = driver.current_url #sanxing
    #driver.get_screenshot_as_file('c:\\study\image01.jpg')
    driver.get(brand_url)
    #list_url = driver.find_element_by_xpath("//div[@id='J_ModeSwitch']/a[1]").get_attribute('href')
    driver.find_element_by_xpath("//div[@id='J_ModeSwitch']/a[1]").click()
    print "click button_list successfully......"
    brand_url = driver.current_url #sanxing list
    get_one_page(brand_url,brand_len) #h获取第一页的detail
    print "get the first page detail successfully......"
    #获取下一页(after 10 page dont need)
    flag = 1
    while flag <= 15:
        try:
            driver.find_element_by_xpath("//div[@class='page-box']/div[@class='pagebar']/a[@class='next']").click()
        except Exception as e:
            try:
                driver.find_element_by_xpath("//div[@class='page-box']/div[@class='pagebar']/a[@class='historyStart']").click()
            except Exception as e:
                print 'this is end'
                break
            else:
                brand_url = driver.current_url
                print brand_url
                get_one_page(brand_url,brand_len)
                print 'get the detail successfully......'
                flag = flag + 1
        else:
            brand_url = driver.current_url
            print brand_url
            get_one_page(brand_url,brand_len)
            print 'get the detail successfully......'
            flag = flag + 1   
    return df

#主函数  
if __name__ == '__main__':  
    driver = webdriver.PhantomJS(executable_path = 'C:\\Python27\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')     
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_list_1.html'
    html = download(url)
    mysoup = BeautifulSoup(html,'lxml')
    div = mysoup.find('div',attrs={'id':"J_BrandAll", 'class':"brand-list",'data-multi':"0"})
    a = div.find_all('a')
    df = pandas.DataFrame()
    for i in range(0,50):
        brand_len = len(a[i].get_text().strip())
        print a[i].get_text().strip()
        crawl(url,i,brand_len)  #23 
    df.to_excel(r'C:\\study\\hxy_device_update.xlsx',encoding='utf-8',index=False)


    # df['model'] = df['model'].map(str.upper)
    # df['model'] = df['model'].map(replace(' ',''))