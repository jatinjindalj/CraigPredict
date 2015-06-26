#For a given url, scrapes data off Craigslist car postings

import urllib
import requests
import re
import time
from bs4 import BeautifulSoup as Soup

        
def ExtractCarData(url):

    r2 =  requests.get(url)
    text = Soup(r2.text)
    id = re.search(r'(var buttonPostingID = \")(\d*)(\")',str(text))

    titletext = text.find_all('span', class_ = "postingtitletext")

    price = re.search(r'(\"price\"\>)(\$)(\d*)', str(titletext))
    title = re.search(r'(\"postingtitletext\"\>)([^\<]+)(\<)', str(titletext))
    datetext = text.find('time')
    date = re.search(r'(\<time datetime=\")(\d\d\d\d-\d\d-\d\d\w\d\d:\d\d:\d\d)', str(datetext))
    if id and price and title and date:  #add item only if id, price, date and a title are found
        price = float(price.group(3))
        title = title.group(2)
        date = date.group(2)
        id = id.group(2)

        lat = re.search(r'(data-latitude=\")(\d\d\.\d\d\d\d\d\d)(\")', str(text))
        if lat:
            coord = 1
        else:
            coord = 0
        solicited = re.search(r'do NOT contact me with unsolicited services or offers', str(text))
        if solicited:
            note = 1
        else:
            note = 0

        up = re.search('(updated: \<time datetime=\")(\d\d\d\d-\d\d-\d\d\w\d\d:\d\d:\d\d)(-0400\"\>)', str(text))
        if up:
            update_date = up.group(2)
        else:
            update_date = ""

        loc = re.search(r'(\<small\> \()(\w.*)(\)\<\/small\>)', str(titletext))
        images = re.findall(r'data-imgid', str(text))
        description_text = text.find('section')
        descr = re.search(r'(postingbody\"\>\n)(.*?)(\<\/section\>)', str(description_text), re.DOTALL)
        if descr:
            nr_links = len(re.findall(r'http://', descr.group(2)))
            show_contact = re.search(r'\"showcontact\"', descr.group(2))
            if show_contact:
                contact = 1
            else:
                contact = 0
            description = re.sub(r'\<.*\>', "", descr.group(2))
            description = re.sub(r'\n', "", description)
        else:
            description = ""
            contact = 0

        if loc:
            location = loc.group(2)
        else:
            location = ""
        if images:
            if len(images) == 1:
                nr_pics = 1
            else:
                nr_pics = len(images)/2
        else:
            nr_pics = 0

        #use only in first read, modifiy appropriately
        #day = re.search(r'(\d\d\d\d-\d\d-)(\d\d)(T)', date).group(2)
        #month = re.search(r'(\d\d\d\d-)(\d\d)(-)', date).group(2)
        #if month == "06":
        #    day_count = 21 - int(day)
        #else:
        #    day_count = 31 - int(day) + 21
        day_count=0    
    #--------------
       
        car_model = text.findAll('p', class_ = "attrgroup")[0].text
        params = text.findAll('p', class_ = "attrgroup")#.find_all('b')
        car_condition = re.search(r'(condition:\<b\>)(.*)(\<\/b\>)',str(params))
        if car_condition:
            car_condition = car_condition.group(2)
        else:
            car_condition= ""
        cylinders = re.search(r'(cylinders:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if cylinders:
            cylinders = cylinders.group(2)
        else:
            cylinders = ""
        drive = re.search(r'(drive:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if drive:
            drive = drive.group(2)
        else:
            drive= ""
        fuel = re.search(r'(fuel:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if fuel:
            fuel = fuel.group(2)
        else:
            fuel = ""
        odometer = re.search(r'(odometer:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if odometer:
            odometer = odometer.group(2)
        else:
            odometer = ""
        color = re.search(r'(paint color:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if color:
            color = color.group(2)
        else:
            color = ""
        car_size = re.search(r'(size:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if car_size:
            car_size = car_size.group(2)
        else:
            car_size = ""
        car_status = re.search(r'(title status:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if car_status :
            car_status  = car_status .group(2)
        else:
            car_status  = ""
        transmission = re.search(r'(transmission:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if transmission:
            transmission = transmission.group(2)
        else:
            transmission = ""
        car_type = re.search(r'(type:\s\<b\>)(.*?)(\<\/b\>)',str(params))
        if  car_type:
             car_type =  car_type.group(2)
        else:
             car_type = ""
     
        return (id, title, location, date, price, nr_pics, description, day_count, nr_links, contact, note, coord, update_date,
                     car_model, car_condition, cylinders, drive, fuel, odometer, color, car_size, car_status, transmission, car_type)
    else:
        return None