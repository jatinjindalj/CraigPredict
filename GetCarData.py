#Extract urls of NYC car listings on Craiglist, then extract data for each url
import numpy as np
import pandas as pd
import urllib
import requests
import re
import time
from bs4 import BeautifulSoup as Soup
import pymysql as mdb
from Scraper import ExtractCarData
import sys
sys.setrecursionlimit(3000) 

con = mdb.connect('localhost', 'charlotte', 'insight', 'LocalClassifieds')
#create tables
#with con:
#    cur = con.cursor()

#cur.execute("CREATE TABLE HondaAccord(Id INT PRIMARY KEY AUTO_INCREMENT, AdId CHAR(10), Title TEXT, Location VARCHAR(255), Date CHAR(19) , Price FLOAT, NrPics SMALLINT, Description TEXT, DayCount SMALLINT, NrLinks SMALLINT, Contact TINYINT, Note TINYINT, COORD TINYINT, UpdateDate CHAR(19), AdTouched TINYINT,  SoldDays SMALLINT, CarModel  VARCHAR(255), CarCondition VARCHAR(255), Cylinders VARCHAR(255), Drive VARCHAR(255), Fuel VARCHAR(255), Odometer VARCHAR(255), Color VARCHAR(255), CarSize VARCHAR(255), CarStatus VARCHAR(255), Transmission VARCHAR(255), CarType VARCHAR(255));
#cur.execute("CREATE TABLE HondaCivic(Id INT PRIMARY KEY AUTO_INCREMENT, AdId CHAR(10), Title TEXT, Location VARCHAR(255), Date CHAR(19) , Price FLOAT, NrPics SMALLINT, Description TEXT, DayCount SMALLINT, NrLinks SMALLINT, Contact TINYINT, Note TINYINT, COORD TINYINT, UpdateDate CHAR(19), AdTouched TINYINT,  SoldDays SMALLINT, CarModel  VARCHAR(255), CarCondition VARCHAR(255), Cylinders VARCHAR(255), Drive VARCHAR(255), Fuel VARCHAR(255), Odometer VARCHAR(255), Color VARCHAR(255), CarSize VARCHAR(255), CarStatus VARCHAR(255), Transmission VARCHAR(255), CarType VARCHAR(255));
#cur.execute("CREATE TABLE ToyotaCamry(Id INT PRIMARY KEY AUTO_INCREMENT, AdId CHAR(10), Title TEXT, Location VARCHAR(255), Date CHAR(19) , Price FLOAT, NrPics SMALLINT, Description TEXT, DayCount SMALLINT, NrLinks SMALLINT, Contact TINYINT, Note TINYINT, COORD TINYINT, UpdateDate CHAR(19), AdTouched TINYINT,  SoldDays SMALLINT, CarModel  VARCHAR(255), CarCondition VARCHAR(255), Cylinders VARCHAR(255), Drive VARCHAR(255), Fuel VARCHAR(255), Odometer VARCHAR(255), Color VARCHAR(255), CarSize VARCHAR(255), CarStatus VARCHAR(255), Transmission VARCHAR(255), CarType VARCHAR(255));
#cur.execute("CREATE TABLE NissanAltima(Id INT PRIMARY KEY AUTO_INCREMENT, AdId CHAR(10), Title TEXT, Location VARCHAR(255), Date CHAR(19) , Price FLOAT, NrPics SMALLINT, Description TEXT, DayCount SMALLINT, NrLinks SMALLINT, Contact TINYINT, Note TINYINT, COORD TINYINT, UpdateDate CHAR(19), AdTouched TINYINT,  SoldDays SMALLINT, CarModel  VARCHAR(255), CarCondition VARCHAR(255), Cylinders VARCHAR(255), Drive VARCHAR(255), Fuel VARCHAR(255), Odometer VARCHAR(255), Color VARCHAR(255), CarSize VARCHAR(255), CarStatus VARCHAR(255), Transmission VARCHAR(255), CarType VARCHAR(255));


with con:
    cur = con.cursor()
    cur.execute("UPDATE HondaAccord SET  AdTouched = 0")
    #cur.execute("UPDATE HondaCivic SET  AdTouched = 0")
    #cur.execute("UPDATE ToyotaCamry SET  AdTouched = 0")
    #cur.execute("UPDATE NissanAltima SET  AdTouched = 0")
    cur.close()
    con.commit()

items = []
url = "http://newyork.craigslist.org/search/cto?query=honda+accord"
#url = "http://newyork.craigslist.org/search/cto?query=honda+civic"
#url = "http://newyork.craigslist.org/search/cto?query=toyota+camry"
#url = "http://newyork.craigslist.org/search/cto?query=nissan+altima"
r = requests.get(url)

main_text = Soup(r.text, 'html.parser')

rows = main_text.find_all('p', 'row')
for row in rows:
    for a in row.find_all('a', href=True, limit=1):
        link= a['href']
        items.append(link)

i = 1
moreAds = True
while (i < 25 and moreAds == True):
    print i
    r = requests.get("http://newyork.craigslist.org/search/cto?s="+str(i)+"00&query=honda accord")
    #r = requests.get("http://newyork.craigslist.org/search/cto?s="+str(i)+"00&query=honda civic")
    #r = requests.get("http://newyork.craigslist.org/search/cto?s="+str(i)+"00&query=toyota camry")
    #r = requests.get("http://newyork.craigslist.org/search/cto?s="+str(i)+"00&query=nissan altima")
    if r:
        main_text = Soup(r.text, 'html.parser')
        rows = main_text.find_all('p', 'row')
        for row in rows:
            for a in row.find_all('a', href=True, limit=1):
                link= a['href']
                items.append(link)

    else:
        moreAds = False
    i += 1
print "Number of items " ,len(items)
ct = 0
url2 = "http://newyork.craigslist.org"
for item in items:
    all_url = url2 + item
    item_data = ExtractCarData(all_url)
    if item_data:
        id = item_data[0]              # unique listing id
        title = item_data[1]           # title of listing
        location = item_data[2]        # location of listing (optional)
        date = item_data[3]            # date listed
        price = item_data[4]           # price (optional)
        nr_pics = item_data[5]         # nr of pictures
        description = item_data[6]     # description (optional)
        day_count = item_data[7]       # number of days posting has been on Craiglist
        nr_links = item_data[8]        # number of links in description (0 most of the time)
        contact = item_data[9]         # 1 if contact by phone possible, 0 otherwise
        note = item_data[10]           # 1 if note on "unsolicited offers...", 0 otherwise
        coord = item_data[11]          # 1 if specific location (resulting in map) given, 0 otherwise
        update_date = item_data[12]    # date of update of listing (if updated)
        car_model = item_data[13]      # car model (Honda Civic, etc)
        car_condition = item_data[14]  #condition of car
        cylinders = item_data[15]
        drive = item_data[16]
        fuel = item_data[17]        
        odometer = item_data[18]        
        color = item_data[19]        
        car_size = item_data[20]
        car_status = item_data[21]
        transmission = item_data[22]
        car_type = item_data[23]

        with con:
            cur = con.cursor()
            cur.execute("SELECT AdId from HondaAccord")
            #cur.execute("SELECT AdId from HondaCivic")
            #cur.execute("SELECT AdId from ToyotaCamry")
            #cur.execute("SELECT AdId from NissanAltima")
            AdIds = cur.fetchall()
            AdIds = list(AdIds)
            AdIds = [ad[0] for ad in AdIds]
    
        if id not in AdIds:
            sql = """INSERT INTO HondaAccord(AdId, Title, Location, Date, Price, NrPics, Description, DayCount, NrLinks, Contact, Note, Coord, UpdateDate, AdTouched, SoldDays, CarModel, CarCondition, Cylinders, Drive, Fuel, Odometer, Color, CarSize, CarStatus, Transmission, CarType )  VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s)"""
            #sql = """INSERT INTO HondaCivic(AdId, Title, Location, Date, Price, NrPics, Description, DayCount, NrLinks, Contact, Note, Coord, UpdateDate, AdTouched, SoldDays, CarModel, CarCondition, Cylinders, Drive, Fuel, Odometer, Color, CarSize, CarStatus, Transmission, CarType )  VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s)"""
            #sql = """INSERT INTO ToyotaCamry(AdId, Title, Location, Date, Price, NrPics, Description, DayCount, NrLinks, Contact, Note, Coord, UpdateDate, AdTouched, SoldDays,CarModel, CarCondition, Cylinders, Drive, Fuel, Odometer, Color, CarSize, CarStatus, Transmission, CarType )  VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s)"""
            #sql = """INSERT INTO NissanAltima(AdId, Title, Location, Date, Price, NrPics, Description, DayCount, NrLinks, Contact, Note, Coord, UpdateDate, AdTouched, SoldDays,CarModel, CarCondition, Cylinders, Drive, Fuel, Odometer, Color, CarSize, CarStatus, Transmission, CarType )  VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s)"""
            
            cur = con.cursor()
            cur.execute(sql, (id, title, location, date, price, nr_pics, description, day_count, nr_links, contact, note, coord, update_date, 1,  0,  car_model, car_condition, cylinders, drive, fuel, odometer, color, car_size, car_status, transmission, car_type ))
            else:
                sql = """UPDATE HondaAccord SET Title = %s, Location = %s, Price = %s, NrPics = %s, Description = %s, DayCount = DayCount+1, NrLinks = %s, Contact = %s, Note = %s, Coord = %s, UpdateDate = %s, AdTouched =  1,CarModel = %s, CarCondition = %s, Cylinders = %s, Drive = %s, Fuel = %s, Odometer = %s, Color = %s, CarSize = %s, CarStatus = %s, Transmission = %s, CarType = %s  WHERE AdId = %s"""
                #sql = """UPDATE HondaCivic SET Title = %s, Location = %s, Price = %s, NrPics = %s, Description = %s, DayCount = DayCount+1, NrLinks = %s, Contact = %s, Note = %s, Coord = %s, UpdateDate = %s, AdTouched =  1,CarModel = %s, CarCondition = %s, Cylinders = %s, Drive = %s, Fuel = %s, Odometer = %s, Color = %s, CarSize = %s, CarStatus = %s, Transmission = %s, CarType = %s  WHERE AdId = %s"""
                #sql = """UPDATE ToyotaCamry SET Title = %s, Location = %s, Price = %s, NrPics = %s, Description = %s, DayCount = DayCount +1, NrLinks = %s, Contact = %s, Note = %s, Coord= %s, UpdateDate = %s, AdTouched =  1,CarModel = %s, CarCondition = %s, Cylinders = %s, Drive = %s, Fuel = %s, Odometer = %s, Color = %s, CarSize = %s, CarStatus = %s, Transmission = %s, CarType = %s  WHERE AdId = %s"""
                #sql = """UPDATE NissanAltima SET Title = %s, Location = %s, Price = %s, NrPics = %s, Description = %s, DayCount = DayCount+1, NrLinks = %s, Contact = %s, Note = %s, Coord = %s, UpdateDate = %s, AdTouched =  1,CarModel = %s, CarCondition = %s, Cylinders = %s, Drive = %s, Fuel = %s, Odometer = %s, Color = %s, CarSize = %s, CarStatus = %s, Transmission = %s, CarType = %s  WHERE AdId = %s"""
                       cur = con.cursor()
            cur.execute(sql, (title, location, price, nr_pics, description, nr_links, contact, note, coord, update_date,  car_model, car_condition, cylinders, drive, fuel, odometer, color, car_size, car_status, transmission, car_type, id))
        con.commit()
        cur.close()

      
with con:
    cur = con.cursor()
    #query = """UPDATE HondaAccord SET SoldDays = DayCount +1 WHERE (AdTouched = 0 and SoldDays = 0)"""
    #query = """UPDATE HondaCivic SET SoldDays = DayCount +1 WHERE (AdTouched = 0 and SoldDays = 0)"""
    #query = """UPDATE ToyotaCamry SET SoldDays = DayCount +1 WHERE (AdTouched = 0 and SoldDays = 0)"""
    #query = """UPDATE NissanAltima SET SoldDays = DayCount +1 WHERE (AdTouched = 0 and SoldDays = 0)"""
    cur.execute(query)
    cur.close()
con.commit()

   