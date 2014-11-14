##################################
#encoding=utf8                   #
#version =py27, py33             #
#author  =sanhe                  #
#date    =2014-10-29             #
#                                #
#    (\ (\                       #
#    ( -.-)o    I am a Rabbit!   #
#    o_(")(")                    #
#                                #
##################################

"""
zillow作为美国房地产咨询的第一大门户网站，有很多人都觊觎它的数据。所以zillow的防爬虫技术也特别的强大。
每次用机器登录zillow的网页，都会需要输入图片上的验证码。所以我们不得不使用selenium技术直接操作浏览器，
从而绕开它的拦阻。
"""

from __future__ import print_function
from .misc import sleep, tryit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as BS4
import sys
import re

try:
    reload(sys); # change the system default encoding = utf-8
    eval('sys.setdefaultencoding("utf-8")') # python3中不需要这样做
except:
    pass

"""
====== 房产价格，面积，学区等具体信息 ======
"""

def zillow_property_detail(html):
    """property info extractor
    extract detail info from HTML
    
    [CN]在www.zillow.com网站上的每一个房地产都有一个唯一的zillow id，通过这个ID可以定位到唯一的url。
    例如： http://www.zillow.com/homedetails/2033-Forbes-Ave-Pittsburgh-PA-15219/11273420_zpid/
    
    只要我们能获得地产页面的html，我们就可以从中解析出许多具体信息
    """
    soup = BS4(html)
    
    ## === For Sale or For Rent or Sold
    try:
        div = soup.find("div", class_ = "estimates")
        forwhat = div.find_all("div")[0]
        forwhat = forwhat.text.strip()
    except:
        raise Exception("Failed to get Forwhat")
        return None
    ## === How much money
    try:
        howmuch = div.find_all("div")[1]
        howmuch = howmuch.text.strip()
    except:
        raise Exception("Failed to get Howmuch")
    ## === square ft area    
    try:
        header = soup.find("header", class_ = "zsg-content-header addr")
        h3 = header.find("h3")
        sqft_info = h3.find_all("span")[-1].text
        try:
            sqft_info = sqft_info.replace(",", "")
            if sqft_info.split(" ")[-1] == "sqft": # 倒数第一个 是sqft
                sqft = int(sqft_info.split(" ")[-2]) # 倒数第二个 是数值
        except:
            sqft = -1
    except:
        raise Exception("Failed to get sqft")
    ## === city
    try:
        span = soup.find("span", itemprop = "addressLocality")
        city = span.text.strip()
    except:
        raise Exception("Failed to get city")
    ## === state
    try:
        span = soup.find("span", itemprop = "addressRegion")
        state = span.text.strip()
    except:
        raise Exception("Failed to get state")
    ## === local schools
    try:
        schools = list()
        ul = soup.find("ul", class_ = "nearby-schools-list")
        for li in ul.find_all("li", class_ = "nearby-school assigned-school  clearfix"):
            rate = li.find("div", class_ = "nearby-schools-rating").span.text
            school_name = li.find("div", class_ = "nearby-schools-name").a.text
            grade = li.find("div", class_ = "nearby-schools-grades").text
            distance = li.find("div", class_ = "nearby-schools-distance").text
            assigned = "assigned"
            schools.append( (rate, school_name, grade, distance, assigned) )
            
        for li in ul.find_all("li", class_ = "nearby-school  clearfix"):
            rate = li.find("div", class_ = "nearby-schools-rating").span.text
            school_name = li.find("div", class_ = "nearby-schools-name").a.text
            grade = li.find("div", class_ = "nearby-schools-grades").text
            distance = li.find("div", class_ = "nearby-schools-distance").text
            assigned = "not assigned"
            schools.append( (rate, school_name, grade, distance, assigned) )
    except:
        raise Exception("Failed to get schools")
    return city, state, sqft, forwhat, howmuch, schools

def property_detail_by_street_and_zipcode(driver, street, zipcode):
    """ENTER text in a input box,
    """
    driver.get("http://www.zillow.com/") # 再次打开主页面
    elem = driver.find_element_by_name("citystatezip") # 定位到 name = "citystatezip" 的搜索框
    elem.send_keys("%s %s" % (street, zipcode)) # 在文本框内输入内容
    elem.send_keys(Keys.RETURN) # 把内容send出去(相当于点击了"search")
    html = driver.page_source # 获得html
    
    soup = BS4(html) 
    a = soup.find("a", class_ = "routable mask hdp-link") # 解析出zillow id所在的页面
    url = "http://www.zillow.com" + a["href"]
    
    driver.get(url)
    html = driver.page_source # 得到zillow id所在页面的html
    
#     with open("%s_%s.html" % (street, zipcode), "w") as f:
#         f.write(html)
    
    return zillow_property_detail(html) # 对html进行解析

"""
====== zipcode, city, state 等地方综合统计信息 ======
"""

def local_detail(html):
    soup = BS4(html)
    blocks = soup.find_all("div", class_ = "zsg-lg-1-3 zsg-md-1-1 zsg-sm-1-1 value-info-block")
    
    # find midian price
    try:
        market_overview = blocks[0]
        ul = market_overview.find("ul", class_ = "value-info-list")
        li = ul.find_all("li")[2]
        price = li.span.text.strip().replace("$", "").replace(",", "")
    except:
        raise Exception("Failed to get midian price")
    # find midian price/sqft
    try:
        list_and_sales = blocks[2]
        ul = list_and_sales.find("ul", class_ = "value-info-list")
        li = ul.find_all("li")[1]
        price_per_sqft = li.span.text.strip().replace("$", "").replace(",", "")
    except:
        raise Exception("Failed to get price/sqft")
    # find midian sqfts
    try:
        price, price_per_sqft = int(price), int(price_per_sqft)
        mid_sqft = float(price)/price_per_sqft
        return price, price_per_sqft, mid_sqft
    except:
        print("\tprice = %s, per_sqft = %s" % (price, price_per_sqft))
        raise Exception("Failed to calculate price/sqft")

def local_market(driver, zipcode):
    driver.get("http://www.zillow.com/home-values/") # 再次打开主页面
    elem = driver.find_element_by_name("TextField_0") # 定位到 name = "citystatezip" 的搜索框
    elem.send_keys("%s" % zipcode) # 在文本框内输入内容
    elem.send_keys(Keys.RETURN) # 把内容send出去(相当于点击了"search")
    html = driver.page_source # 获得html

#     with open("stats_%s.html" % zipcode, "w") as f:
#         f.write(html)
    
    return local_detail(html)