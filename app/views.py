from flask import render_template, request
from app import app
import numpy as np
import re
import pymysql as mdb
db = mdb.connect('localhost', 'charlotte', 'insight', 'LocalClassifieds', charset = 'utf8')
from MakePrediction import MakePrediction
from Scraper import ExtractCarData

@app.route('/')

@app.route('/input')
def bikes_input():
    return render_template("input1.html")

@app.route('/output')
def cars_output():
    
    url = request.args.get("URL")
    nr = request.args.get("NR")
    err = False
    message = ""
    
    if not url:
        message +=  "Please enter a link to your listing."
        err = True
   
    if not nr:
        message += " Please enter the number of days within which you would like to sell."
        err = True

    elif int(nr) < 1 or int(nr) > 20: # or isinstance(nr, int) == False :
        message += " Please enter an integer number between 1 and 20."
        err = True

    if url and err == False:
        item_data = ExtractCarData(url)
    
        if not item_data:
            message  += " Could not extract data from the link provided. Please check the link."
            err = True
        else:
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
            if not "honda civic" in car_model.lower() and not "toyota camry" in car_model.lower() and not "nissan altima" in car_model.lower():
                message += " Currently, only Honda Civic, Toyota Camry and Nissan Altima are supported."
                err = True
            else:
                (prob, messages) = MakePrediction(nr,title,location,price,nr_pics,description,nr_links,contact,note,coord,car_model, cylinders, drive, fuel, odometer, color, car_size, car_status, transmission, car_type)
                phone = "Yes" if contact == 1 else "No"
                geo = "Yes" if coord == 1 else "No"
                return render_template('output1.html', nr = nr, percent = prob, messages = messages, car_model=car_model, price=price, odometer=odometer, title = title.rstrip("-"), nr_pics = nr_pics, description=description,
                    color = color, phone=phone, geo = geo, car_status = car_status, transmission=transmission,car_type = car_type, )
            
      
            
    if err == True:
        return render_template('output1_message.html', message = message)

