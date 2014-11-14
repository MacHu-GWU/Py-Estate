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
A wrapper to get data from www.zillow.com
"""

from __future__ import print_function
try:
    from .crawler import Crawler
    from .logger import Log
except:
    from crawler import Crawler
    from logger import Log
    
from bs4 import BeautifulSoup as BS4
import re


def gen_url_by_zipcode(zipcode, n = 100):
    return ["https://www.redfin.com/zipcode-homes-for-sale/%s?start=%s" % (zipcode, i*50) for i in range(n)]


def home_for_sale_by_zipcode(zipcode):
    spider = Crawler()
    for url in gen_url_by_zipcode(zipcode):
        html = spider.html(url)
        if html:
            soup = BS4(html)
            div = soup.find("div", id = "listings")
            divs = div.find_all("tr", id = re.compile(r"listing.*"))
            if len(divs) > 0:
                for tr in divs:
                    tds = tr.find_all("td")
                    address = tds[1].div.a.text.strip()
                    broker = tds[1].div.find("span", class_="broker-name").text.strip()
                    citystate = tds[1].div.text.replace(address, "").replace(broker, "").strip()
                    price = tds[3].text.strip()
                    beds = tds[4].text.strip()
                    baths = tds[5].text.strip()
                    sqft = tds[6].text.strip()
                    persqft = tds[7].text.strip()
                    yield address, citystate, zipcode, price, beds, baths, sqft, persqft, broker
            else:
                break
            
for i in home_for_sale_by_zipcode("20817"):
    print(i)
