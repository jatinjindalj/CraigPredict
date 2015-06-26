#Make prediction of probability of sale for a given listing, make some suggestions to improve the listing for a faster sale
#Prediction is made using random forest model
import numpy as np
import pandas as pd
import nltk as nltk
import pymysql as mdb
import sklearn
import scipy as sci
import nlp
import pickle


def MakePrediction(nr,title,location, price,nr_pics,description,nr_links,contact,note,coord,car_model, cylinders, drive, fuel, odometer, color, car_size, car_status, transmission, car_type):
    #check model
    if "honda civic" in car_model.lower():
        learner = pickle.load( open( "RFLearnerHondaCivicNoText"+str(nr)+".p", "rb" ) )
        color_dict =  pickle.load( open("Color_HondaCivic_Dict.p","rb")  )
        cartype_dict =  pickle.load( open("CarType_HondaCivic_Dict.p","rb")  )
        
    elif "toyota camry" in car_model.lower() :
        learner = pickle.load( open( "RFLearnerToyotaCamryNoText"+str(nr)+".p", "rb" ) )
        color_dict =  pickle.load( open("Color_ToyotaCamry_Dict.p","rb")  )
        cartype_dict =  pickle.load( open("CarType_ToyotaCamry_Dict.p","rb")  )
    elif "nissan altima" in car_model.lower() :
        learner = pickle.load( open( "RFLearnerNissanAltimaNoText"+str(nr)+".p", "rb" ) )
        color_dict =  pickle.load( open("Color_NissanAltima_Dict.p","rb")  )
        cartype_dict =  pickle.load( open("CarType_NissanAltima_Dict.p","rb")  )
    
    len_title = len(title.split()) 
    len_description = len(description.split())
   
    if color_dict[color]:
        color = color_dict[color] 
    else:
        color = -100
    if cartype_dict[car_type]:
        car_type = cartype_dict[car_type] 
    else:
        car_type = -100

    car_status = 1 if car_status == 'clean' else 0
    cylinders = 0 if cylinders == "" else 1
    drive= 0 if drive == "" else 1
    transmission = 1 if transmission == "automatic" else 0
    fuel = 1 if fuel == 'gas' else 0
  
    year = car_model.split(" ")
    year = year[0]
    if odometer == "":
        odometer = -10000
    
    X1 = pd.Series([contact,nr_pics,price,len_title ,len_description, coord,
                    cylinders,drive,fuel,odometer,color,car_status, transmission, year, car_type, nr_links] ,
                    index = ['Contact','NrPics','Price','LenTitle','LenDescription','COORD',
                             'Cylinders','Drive','Fuel','Odometer','Color','CarStatus','Transmission','Year','CarType','NrLinks'])
   
    prob = learner.predict_proba(X1.values)
    prob = prob.ravel()
    prob = int(prob[1] * 100)

    X1S = X1.copy()
    max_prob = prob
    best_pic = nr_pics
    best_title = len_title
    best_desc = len_description    
    best_pic_index = 1
    best_title_index = 1
    best_desc_index = 1
    no_odo = 0
    changes = [0,1,3]
    for ch_pic in changes: #50% less, 100% more
        X1S['NrPics'] = int((ch_pic*0.5  + 0.5) *nr_pics)
        for len_tit in changes:
            X1S['LenTitle'] = nt((len_tit *0.5 +0.5) * len_title)
            for len_des in changes:
                X1S['LenDescription'] = int((len_des *0.5 +0.5) * len_description)
             
                prob1 = learner.predict_proba(X1S.values)
                prob1 = prob1.ravel()
                prob1 = int(prob1[1] * 100)
                prob2 = 0
                if X1['Odometer'] != -10000:
                    X1S['Odometer'] = -10000
                    prob2 = learner.predict_proba(X1S.values)    
                    prob2 = prob2.ravel()
                    prob2 = int(prob2[1] * 100)
                
                if prob1 > max_prob:
                    best_pic = X1S['NrPics']
                    best_pic_index = ch_pic
                    best_title = X1S['LenTitle']
                    best_title_index = len_tit
                    best_desc = X1S['LenDescription']
                    best_desc_index = len_des
                    max_prob = prob1
                    no_odo = 0
                    if prob2 > prob1:
                        max_prob = prob2
                        no_odo = 1
               
    messages = []
   
    if best_pic_index == 0:
        messages.append("Include half as many pictures. \n")
    elif best_pic_index == 3:
        messages.append("Include twice as many pictures. \n")
    if best_title_index == 0:
        messages.append("Reduce the number of words in the title by 50 percent. \n")
    elif best_title_index ==3:
        messages.append("Include twice as many words in the title. \n")
    if best_desc_index == 0:
        messages.append("Reduce the number of words in the description by  50 percent. \n")
    elif best_desc_index == 3:
        messages.append("Include twice as many words in  the description. \n")
       
    if no_odo == 1:
        messages.append( "Do not include odometer information in your listing. \n")
    if len(messages) > 0:
        messages.insert(0,"If you make the following changes, your car will sell within {} days with a probability of {} percent: \n".format(nr, max_prob))
   
   
    X1S = X1.copy()
    pr = 0.9  * price
    X1S['LenTitle'] = best_title
    X1S['LenDescription'] =  best_desc
    if no_odo == 1:
        X1S['Odometer'] = -10000
    X1S['NrPics'] = best_pic
    X1S['Price'] = pr                 
    max_prob_price = learner.predict_proba(X1S.values)                 
    max_prob_price=  max_prob_price.ravel()
    max_prob_price = int( max_prob_price[1] * 100)        
               
    if max_prob_price > max_prob:
        messages.append("If you additionally reduce the price by 10 percent to ${}, you will sell within {} days with a probability of {} percent.".format(pr, nr, max_prob_price))            
    
    
    return (prob,  messages)
    
