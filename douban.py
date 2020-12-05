#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # 等待元素加载的
from selenium.webdriver.support import expected_conditions as EC  #判断条件是否满足
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import sys
import requests
import json
import re
import pandas
from pyecharts import Bar,Pie,Line
from lxml import etree
import pickle
import sqlite3

reload(sys) 
sys.setdefaultencoding('utf8')   

class Login_by_pwd(object):
    """docstring for Login"""
    def __init__(self, usr_name, usr_pwd):
        self.usr_name = usr_name
        self.usr_pwd = usr_pwd
        self.url = 'https://www.douban.com/'
        self.driver = webdriver.Firefox()

    def get_cookie(self):
        
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        cookie_f = self.driver.get_cookies()

        name = self.driver.find_element_by_xpath('//div[@class="item item-account"]/input[@id="form_email"]')
        time.sleep(1)
        usr = usr_name
        name.send_keys(usr)

        password = self.driver.find_element_by_xpath('//div[@class="item item-passwd"]/input[@id="form_password"]')
        time.sleep(1)
        pwd = usr_pwd
        password.send_keys(pwd)

        submit = self.driver.find_element_by_xpath('//div[@class="item item-submit"]/input[@class="bn-submit"]')
        time.sleep(3)
        submit.click()
        
        time.sleep(3) 
        page = self.driver.page_source
        print page
        
        cookie_s = self.driver.get_cookies()
        print cookie_s

        return cookie_f,cookie_s

    def save_cookie(self,cookie,tb_txt):
        with open(tb_txt,'w') as f:
            f.write(json.dumps(cookie))

class CrawList(object):
    """
        该类简单获取top20电视剧信息列表
        gettvlist() 是通过RequestsCookieJar()来获取cookies 并且通过requests.get() 来解析网页
        通过 gettvlist() 获取tv名称和得分 是通过两个列表压缩而成的
        最后将结果写入到sqlite3 库名是tv.db 表名是tvlist
    """
    
    def gettvlist(self, tb_txt):
        # utilize requests module
        title = []
        rate = []
        time.sleep(3)
        url = 'https://movie.douban.com/j/search_subjects?type=tv&tag=热门&sort=recommend&page_limit=20&page_start=0'
        jar = requests.cookies.RequestsCookieJar()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6726.400 QQBrowser/10.2.2265.400'
        }
        f = open(tb_txt, 'r')
        for line in f.read().split(';'):
            name, value = line.strip().split('=',1)
            jar.set(name, value)
        r = requests.get(url, cookies=jar, headers=headers)
        # print r.text # r的返回结果为text
        for i in range(0,len(r.json()['subjects'])): # r的返回结果为json文件
            title.append(r.json()['subjects'][i]['title'])
            rate.append(r.json()['subjects'][i]['rate'])
        # print title
        # print rate
        ziplist = zip(title, rate)
        df = pandas.DataFrame(ziplist, columns=['title','rate'])
        # df.to_json('tv_list.json')
        con = sqlite3.connect('C:\\Program Files\\Sublime Text 3\\Project\\HXY\\dora_pc\\tv.db')
        pandas.DataFrame.to_sql(df, name='tvlist', con=con, if_exists='replace')

class CrawlUserview(object):
    """
    该类是获取top20电视剧的得分，简介的keyword，以及用户短评的keyword
    hotbrief() 是通过driver.add_cookie()来获取cookies 并且通过driver.get() 来解析网页
    在通过 hotbrief() 获取该tv的简介 是通过字典append入列表中的
    """
    def __init__(self, tb_txt):

        self.tb_txt = tb_txt
        self.info = {}
        self.info.setdefault('title',[])
        self.info.setdefault('brief',[])
        self.info.setdefault('score',[])
        self.info.setdefault('view',{})

        url = "https://www.douban.com/"
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6726.400 QQBrowser/10.2.2265.400'
        headers = {'User_agent':user_agent}
        self.driver = webdriver.Firefox()
        with open(self.tb_txt,'r') as f:
            cookies_dict = json.loads(f.read())
        self.driver.get(url)
        for i in cookies_dict:
            self.driver.add_cookie(i)
        self.driver.refresh()

    def hotbrief(self):

        url = "https://movie.douban.com/tv/#!type=tv&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start=0"
        self.driver.get(url)
        # print driver.page_source
        time.sleep(2)
        score = self.driver.find_elements_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div/div[4]/div/a/p')
        # print score
        for i in range(0, len(score)):
            print score[i].text
            self.info['score'].append(score[i].text)

        handle = self.driver.current_window_handle
        # print handle
        # print self.driver.current_url
        time.sleep(3)
        for i in range(0,len(score)):
            u = "/html/body/div[3]/div[1]/div/div[1]/div/div[4]/div/a[%s]/p" % (i+1)
            self.driver.find_element_by_xpath(u).click()
            time.sleep(3)
            headers = self.driver.window_handles
            # print headers
            self.driver.switch_to_window(headers[1])
            time.sleep(3)
            # print driver.current_url
            title = self.driver.find_element_by_xpath("/html/body/div[3]/div[1]/div[2]/div[1]/div[4]/h2/i").text
            print title
            self.info['title'].append(title)
            brief = self.driver.find_element_by_xpath("/html/body/div[3]/div[1]/div[2]/div[1]/div[4]/div/span").text
            print brief
            self.info['brief'].append(brief)
            for t in range(1,6):
                try:
                    xpath = "/html/body/div[3]/div[1]/div[2]/div[1]/div[10]/div[2]/div[2]/div[1]/div[%d]/div/p/span[3]/a" % t
                    ext = self.driver.find_element_by_xpath(xpath)
                    ext.click()
                except Exception as e:
                    print 'all'
            views = self.driver.find_elements_by_xpath("/html/body/div[3]/div[1]/div[2]/div[1]/div[10]/div[2]/div[2]/div[1]/div/div/p/span")
            v = []
            for j in range(0,len(views)):
                print views[j].text
                v.append(views[j].text)
            self.info['view'][i] = v
            self.driver.close()
            self.driver.switch_to_window(headers[0])
            time.sleep(2)
            # print driver.current_window_handle

        with open('douban_tv02.json','w') as file:
            file.write(json.dumps(self.info, indent=2, ensure_ascii=False))
       
class CrawlReview(object):
    """
    该类是获取top20评论
    该方法是通过 driver 来获取cookies
    getinfo() 是通过driver获取top20评论中的基本信息
    getreview() 是通过driver根据top20评论中的id来获取top20的评论，该评论是ajax异步加载
    """
    def __init__(self, tb_txt):

        self.tb_txt = tb_txt
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
        self.headers = {'User_agent':self.user_agent}
        self.driver = webdriver.Firefox()
        with open(self.tb_txt,'r') as f:
            cookies_list = json.loads(f.read())
        url = "https://www.douban.com/"
        self.driver.get(url)
        for i in cookies_list:
            self.driver.add_cookie(i)
        self.driver.refresh()
        self.info = {}
        self.info.setdefault('name',[])
        self.info.setdefault('img',[])
        self.info.setdefault('author',[])
        self.info.setdefault('title',[])
        self.info.setdefault('nm_id',[])
        self.info.setdefault('text',[])

    def getinfo(self):
        
        # print driver.page_source
        self.driver.get('https://movie.douban.com/')
        self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/ul/li[7]/a').click()
        names = self.driver.find_elements_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div/div/a/img')
        authors = self.driver.find_elements_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div/div/header/a[2]')
        titles = self.driver.find_elements_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div/div/div/h2/a')
        nm_ids = self.driver.find_elements_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div')
        for i in range(0,len(nm_ids)):
            time.sleep(2)
            self.info['name'].append(names[i].get_attribute('title'))
            img_url = requests.get(names[i].get_attribute('src'))
            img = pickle.dumps(img_url.content) # uft-8 to byte
            with open('C:\\study\\'+str(i)+'.jpg','wb') as fb:
                fb.write(img)
            self.info['img'].append(img)
            self.info['author'].append(authors[i].text)
            self.info['title'].append(titles[i].text)
            self.info['nm_id'].append(nm_ids[i].get_attribute('data-cid'))
        # with open('douban01.json','w') as file:
        #     file.write(json.dumps(self.info, indent=2, ensure_ascii=False))

    def getreview(self):

        for i in range(0,len(self.info['nm_id'])):
            time.sleep(2)
            all_url = 'https://movie.douban.com/j/review/%s/full' % self.info['nm_id'][i]
            print all_url
            # self.driver.get(all_url)
            # print self.driver.page_source
            # print self.driver.find_elements_by_xpath('//div[@id="json"]').text
            page = requests.get(all_url)
            page_d = json.loads(page.text)['body'] #json to dict
            html = etree.HTML(page_d)
            revs = html.xpath('//div/div/div/p/text()')
            print revs
            aa = ''
            for j in range(0,len(revs)):
                aa = aa + revs[j]
            self.info['text'].append(aa.strip().replace('\n',''))
            print "finishing the %d" % i
        with open('douban03.json','w') as file:
            file.write(json.dumps(self.info, indent=2, ensure_ascii=False))
        # zipped = zip(self.name, self.author, self.title, self.review)
        # df = pandas.DataFrame(zipped, columns=['name','img','author','title','review'])
        # df = pandas.DataFrame(self.info, columns=['name','author','title','text'])
        # df.to_excel('C:\\study\\douban10.xlsx', encoding='utf-8', index=False)

class CrawSpecialView(object):
    """
        获取西红柿首富的影评总量为10w
        取2.5w需用训练，2.5w用于测试，
        其余的5w通过模型，预测出来

        通过cookie登陆我的账号，直接跳转到西红柿首富的网页
        方法 webdriver 添加cookie 以及解析网页
    """
    def __init__(self, tb_txt):
        self.tb_txt = tb_txt
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
        self.headers = {'User_agent':self.user_agent}
        self.driver = webdriver.Firefox()
        with open(self.tb_txt, 'r') as f:
            cookie = json.loads(f.read())
        url = 'https://www.douban.com/'
        self.driver.get(url)
        for i in cookie:
            self.driver.add_cookie(i)
        self.driver.refresh()
        self.author = {}

    def get_commend(self, url, ctype):

        self.driver.get(url)
        writer = self.driver.find_elements_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/div/div[2]/h3/span[2]/a')
        scores = self.driver.find_elements_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/div/div[2]/h3/span[2]/span[2]')
        comments = self.driver.find_elements_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/div/div[2]/p/span')
        for i in range(0, len(scores)):
            info = {}
            info['type'] = ctype
            info['score'] = int(scores[i].get_attribute('class')[7:8])
            info['comment'] = comments[i].text
            self.author[writer[i].text] = info
            # self.author[i] = info
        print self.driver.current_url
        print 'finishing'

    def get_next_page(self, first_url, ctype, result):

        self.get_commend(first_url, ctype)
        try:
            self.driver.find_element_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/div[22]/a').click()
        except Exception as e:
            print 'don\'t find the next page' 
        else:
            time.sleep(3)
            url = self.driver.current_url
            print url
        flag = 0 
        while flag <= 50:
            self.get_commend(url, ctype)
            try:
                self.driver.find_element_by_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/div[21]/a[3]').click()
            except Exception as e:
                print 'don\'t find the next page'
            else:
                time.sleep(3)
                url = self.driver.current_url
                print url
            flag += 1
        with open(result, 'w') as f:
            f.write(json.dumps(self.author, indent=2, ensure_ascii=False))

    def get_all_commend(self):
        url_h = 'https://movie.douban.com/subject/27605698/comments?start=0&limit=20&sort=new_score&status=P&percent_type=h'
        self.get_next_page(url_h, 'high', 'xhscf_high.json')
        url_l = 'https://movie.douban.com/subject/27605698/comments?start=0&limit=20&sort=new_score&status=P&percent_type=l'
        self.get_next_page(url_l, 'low', 'xhscf_low.json')
        print "all is finishing"


class DrawPic(object):
    """
    该类是用于可视化
    """

    def __init__(self, name, value):
        from pyecharts import configure
        self.name = name
        self.value = value
        configure(global_theme='dark')

    def bar(self):
        bar = Bar("visual picture", "hot top series")
        bar.add("series", name, value)
        # bar.print_echarts_options() # 该行只为了打印配置项，方便调试时使用
        bar.render(r"C:\study\my_first_chart.html")    # 生成本地 HTML 文件

    def bar_zoom(self):
        bar = Bar("Bar - datazoom - inside 示例")
        bar.add(
            "",
            name,
            value,
            is_datazoom_show=True,
            datazoom_type="both",
            datazoom_range=[10, 25],
        )
        bar.render(r"C:\study\my_first_chart2.html")

    def pie_zoom(self):
        pie = Pie("饼图-圆环图示例", title_pos='center')
        pie.add(
            "",
            name,
            value,
            radius=[40, 75],
            label_text_color=None,
            is_label_show=True,
            legend_orient="vertical",
            legend_pos="left",
        )
        pie.render(r"C:\study\my_first_chart3.html")

    def line(self):
        line = Line(title="折线图示例", width=1000, height=600)
        # line.add("商家A", attr, v1, mark_point=["average"])
        line.add("series", name, value, is_smooth=True, mark_line=["max", "average"], xaxis_rotate=30, label_text_size=5)
        line.print_echarts_options()
        line.render(r"C:\\study\\my_first_chart3.html")

     

if __name__ == '__main__':
    # usr_name = 'cannot tell you!'
    # usr_pwd = 'cannot tell you!'
    # login = Login_by_pwd(usr_name,usr_pwd)
    # cookie1,cookie2 = login.get_cookie()
    # login.save_cookie(cookie1,"cookie1.txt")
    # login.save_cookie(cookie2,"cookie2.txt")

    # ls = CrawList()
    # ls.gettvlist('dbcookie.txt')
    # ls = CrawlUserview('cookie2.txt')
    # ls.hotbrief()

    a = CrawSpecialView('cookie2.txt')
    a.get_all_commend()


    # cr = CrawlReview("cookie2.txt")
    # cr.getinfo()
    # cr.getreview()

    # dr = DrawPic(name,value)
    # dr.pie_zoom()
    # dr.line()

    