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
Trulia网站比zillow好爬,没有图片验证机制
"""

from __future__ import print_function
from lib.misc import sleep, tryit
from lib.logger import Log
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

class Trulia(object):
    def __init__(self, log = Log(), driver = None):
        self.log = log
        self.driver = driver
    
    def add_driver(self, driver):
        self.driver = driver
        
    def trulia_property_detail(self, html, street, zipcode):
        """property info extractor
        extract detail info from HTML
        """
        soup = BS4(html)
        
        ## === address, city, state,
        address_field = list()
        try:
            h1 = soup.find("h1", itemprop = "address")
            for span in h1.find_all("span"):
                if span.string:
                    address_field.append(span.string.strip())
        except:
            pass
        
        ## === features and public record
        features = list()
        try: ## === features
            ul = soup.find("ul", class_ = "listInline pdpFeatureList")
            for li in ul.find_all("li"):
                if len(li.attrs) == 0:
                    features.append(li.text.strip())
        except:
            pass
        
        try: ## === public record
            ul = soup.find("ul", class_ = "listInline mbn pdpFeatureList")
            for li in ul.find_all("li"):
                if len(li.attrs) == 0:
                    features.append(li.text.strip())
        except:
            pass
        
        ## === school
        schools_info = list()
        try:
            div = soup.find("div", class_ = "mediaBody  pls ptm pln")
            for p in div.find_all("p"):
                schools_info.append(p.text.strip())
        except:
            pass
            
        ## === validate result, if result valid, then return, if not, raise error
        if (len(address_field) > 0) and (len(features) > 0) and (len(schools_info) > 0):
            address_field = ",".join(address_field)
            features = "&&".join(features)
            schools_info = "\n".join(schools_info)
            return address_field, features, schools_info
        else:
            raise("Failed to extract info from %s, %s" % (street, zipcode))

    def property_detail_by_street_and_zipcode(self, street, zipcode):
        """ENTER text in a input box,
        """
        self.driver.get("http://www.trulia.com/") # 打开搜索主页面
        elem = self.driver.find_element_by_id("searchbox_form_location") # 定位到 id = "searchbox_form_location" 的搜索框
        elem.clear()
        elem.send_keys("%s %s" % (street, zipcode)) # 在文本框内输入内容
        elem.send_keys(Keys.RETURN) # 把内容send出去(相当于点击了"search")
        html = self.driver.page_source # 获得html
        return self.trulia_property_detail(html, street, zipcode) # 对html进行解析
    
    def stable_crawler(self, street, zipcode, try_howmany = 5): # 尝试五次
        return tryit(try_howmany, self.property_detail_by_street_and_zipcode, street, zipcode)
    
    @staticmethod
    def digital_filter(text):
        res = list()
        for char in text:
            if char.isdigit():
                res.append(char)
        return "".join(res)
    
    def feature_parser(self, text):
        features = {key: "unknown" for key in ["price", "sqft", "bedroom", "bathroom", "status"]}
        
        for field in text.split("&&"):
            field = field.lower()
            ## 价格
            if "price" in field:
                features["price"] = self.digital_filter(field)
                continue
            ## 面积
            elif ("sqft" in field) and ("lot size" not in field):
                features["sqft"] = self.digital_filter(field)
            elif "lot size" in field:
                if features["sqft"] == "unknown":
                    features["sqft"] = self.digital_filter(field)
                    continue
            ## 卧室
            elif "bedroom" in field:
                features["bedroom"] = self.digital_filter(field)
                continue
            ## 洗手间
            elif "bathroom" in field:
                features["bathroom"] = self.digital_filter(field)
                continue
            ## 市场状态
            elif "status" in field:
                features["status"] = field.split(":")[-1].strip()
                continue
        return features
    
    def address_parser(self, text):
        address_fields = text.split(",")
        if len(address_fields) >= 4:
            address, city, state, zipcode = (address_fields[0],
                                             address_fields[1],
                                             address_fields[2],
                                             address_fields[3])
            return address, city, state, zipcode