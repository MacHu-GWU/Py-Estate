##encoding=utf8

from __future__ import print_function
from pyestate.lib.logger import Log
from pyestate.trulia import Trulia
from selenium import webdriver
import pandas as pd, numpy as np
import sqlite3

conn = sqlite3.connect("estate.db")
c = conn.cursor()

def create_db():
    try:
        cmd = """CREATE TABLE treatment_houseinfo (
        id TEXT,
        rough_address TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zipcode TEXT,
        bedroom REAL,
        bathroom REAL,
        sqft REAL,
        price REAL,
        PRIMARY KEY (id, rough_address));"""
        c.execute(cmd)
    except:
        pass
    try:
        cmd = """CREATE TABLE control_houseinfo (
        id TEXT,
        rough_address TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zipcode TEXT,
        bedroom REAL,
        bathroom REAL,
        sqft REAL,
        price REAL,
        PRIMARY KEY (id, rough_address));"""
        c.execute(cmd)
    except:
        pass
    conn.commit()
    
create_db()

def main():
    log = Log()
    driver = webdriver.Firefox()
    driver.set_page_load_timeout(30) # 设置timeout时间为30秒
    trulia = Trulia(log)
    trulia.add_driver(driver)
    
    treatment, control = (pd.read_csv("dr_2014_treatment_geoinfo.txt", sep="\t", header = 0, index_col = False, dtype = {"zipcode": np.str}),
                          pd.read_csv("dr_2014_control_geoinfo.txt", sep="\t", header = 0, index_col = False, dtype = {"zipcode": np.str}))

    treatment_existing = set( [id[0] for id in c.execute("SELECT id FROM treatment_houseinfo").fetchall()] )
    control_existing = set( [id[0] for id in c.execute("SELECT id FROM control_houseinfo").fetchall()] )
    
    for id, rough_address, zipcode in treatment.values:
        if id not in treatment_existing:
            try:
                print("anlysising %s, %s" % (rough_address, zipcode))
                address_field, features, schools_info = trulia.stable_crawler(rough_address, zipcode)
                features = trulia.feature_parser(features)
                address, city, state, zipcode = trulia.address_parser(address_field)
                c.execute("""INSERT INTO treatment_houseinfo VALUES (?,?,?,?,?,?,?,?,?,?)""", 
                          (id, rough_address, address, city, state, zipcode,
                           features["bedroom"], features["bathroom"], features["sqft"], features["price"],))
                print("\tSUCCESS!")
                conn.commit()
            except Exception as e:
                log.write(str(e), "%s %s" % (rough_address, zipcode) )
                
    for id, rough_address, zipcode in control.values:
        if id not in control_existing:
            try:
                print("anlysising %s, %s" % (rough_address, zipcode))
                address_field, features, schools_info = trulia.stable_crawler(rough_address, zipcode)
                
                features = trulia.feature_parser(features)
                address, city, state, zipcode = trulia.address_parser(address_field)
                c.execute("""INSERT INTO control_houseinfo VALUES (?,?,?,?,?,?,?,?,?,?)""", 
                          (id, rough_address, address, city, state, zipcode,
                           features["bedroom"], features["bathroom"], features["sqft"], features["price"],))
                print("\tSUCCESS!")
                conn.commit()
            except Exception as e:
                log.write(str(e), "%s %s" % (rough_address, zipcode) )
                
main()