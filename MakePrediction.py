#Make prediction of probability of sale for a given listing, make some suggestions to improve the listing for a faster sale
#Prediction is made using random forest model
import numpy as np
import pandas as pd
import nltk as nltk
import sklearn
import scipy as sci
import nlp
import pickle


def MakePrediction(nr,title,location, price,nr_pics,description,nr_links,contact,note,coord,car_model, cylinders, drive, fuel, odometer, color, car_size, car_status, transmission, car_type):
    #check model
    if "honda civic" in car_model.lower():
        learner = pickle.load( open( "RFLearnerHondaCivicNoTextNYC"+str(nr)+".p", "rb" ) )
        color_dict =  pickle.load( open("Color_HondaCivic_Dict.p","rb")  )
        cartype_dict =  pickle.load( open("CarType_HondaCivic_Dict.p","rb")  )
        location_dict =  pickle.load( open("LocationDict_HondaCivic.p","rb")  )
        
    elif "toyota camry" in car_model.lower() :
        learner = pickle.load( open( "RFLearnerToyotaCamryNoTextNYC"+str(nr)+".p", "rb" ) )
        color_dict =  pickle.load( open("Color_ToyotaCamry_Dict.p","rb")  )
        cartype_dict =  pickle.load( open("CarType_ToyotaCamry_Dict.p","rb")  )
        location_dict =  pickle.load( open("LocationDict_ToyotaCamry.p","rb")  )
    elif "nissan altima" in car_model.lower() :
        learner = pickle.load( open( "RFLearnerNissanAltimaNoTextNYC"+str(nr)+".p", "rb" ) )
        color_dict =  pickle.load( open("Color_NissanAltima_Dict.p","rb")  )
        cartype_dict =  pickle.load( open("CarType_NissanAltima_Dict.p","rb")  )
        location_dict =  pickle.load( open("LocationDict_NissanAltima.p","rb")  )
    
    len_title = len(title.split()) 
    len_description = len(description.split())
   
    if color in color_dict.keys():
        color = color_dict[color] 
    else:
        color = -100
    if car_type in cartype_dict.keys():
        car_type = cartype_dict[car_type] 
    else:
        car_type = -100

    if location in location_dict.keys():
        location = location_dict[location]
    else:
        location = -100

    car_status = 1 if car_status == 'clean' else 0
    cylinders = 0 if cylinders == "" else 1
    drive= 0 if drive == "" else 1
    transmission = 1 if transmission == "automatic" else 0
    fuel = 1 if fuel == 'gas' else 0
  
    year = car_model.split(" ")
    year = year[0]
    if odometer < 1000 and year < 2015: 
        odometer *= 1000
    if odometer == "":
        odometer = -10000
    ratio_sentences_words = nlp.sentence_count(description.decode('utf-8'))/(len_description+1.)
    ratio_sentences_words /= (len_description+1.)
    lex_diversity = nlp.lexical_diversity(description.decode('utf-8'))

    X1 = pd.Series([contact,nr_pics,price,len_title ,len_description, coord,
                    cylinders,drive,fuel,odometer,color,car_status, transmission, year, car_type, nr_links,ratio_sentences_words,lex_diversity, location] ,
                    index = ['Contact','NrPics','Price','LenTitle','LenDescription','COORD',
                             'Cylinders','Drive','Fuel','Odometer','Color','CarStatus','Transmission','Year','CarType','NrLinks','RatioSentencesWords','LexDiversity','LocationCats'])
   
    prob = learner.predict_proba(X1.values)
    prob = prob.ravel()
    prob = int(prob[1] * 100)

    X1S = X1.copy()
    max_prob = prob
    best_pic = nr_pics
    best_price = price
    best_desc = len_description 
    best_ratio = ratio_sentences_words
    best_lex = lex_diversity
    best_pic_index = 1
    best_price_index = 1
    best_desc_index = 1
    best_ratio_index = 1
    best_lex_index = 1
    changes = [0,1,3]
    for ch_pic in changes: #50% less, 100% more
        if X1S['NrPics'] != 0:
            X1S['NrPics'] = int((ch_pic*0.5  + 0.5) *nr_pics)
        else:
            X1S['NrPics'] = 0
            best_pic_index = 1
        for pr in range(3): #100,95,90%,
            X1S['Price'] =  (100- pr*5) *0.01 * price
            for len_des in changes:
                X1S['LenDescription'] = int((len_des *0.5 +0.5) * len_description)
                for rs in range(3):
                    X1S['RatioSentencesWords'] = (rs*0.5 + 0.5) * X1['RatioSentencesWords']
                for ld in range(3):
                    X1S['LexDiversity'] = int(ld*0.5 + 0.5) * X1['LexDiversity']
                    prob1 = learner.predict_proba(X1S.values)
                    prob1 = prob1.ravel()
                    prob1 = int(prob1[1] * 100)
                            
                if prob1 > max_prob:
                    best_pic = X1S['NrPics']
                    best_pic_index = ch_pic
                    best_price = X1S['Price']
                    best_price_index = pr
                    best_desc = X1S['LenDescription']
                    best_desc_index = len_des
                    best_ratio = X1S['RatioSentencesWords']
                    best_ratio_index = rs
                    best_lex = X1S['LexDiversity']
                    best_lex_index = ld
                    max_prob = prob1
                          
               
    messages = []
    print ratio_sentences_words,0.5*X1['RatioSentencesWords'],best_ratio
    if best_pic_index == 0:
        messages.append("- Include half as many pictures. \n")
    elif best_pic_index == 3:
        messages.append("- Include twice as many pictures. \n")
    if best_price_index == 1:
        messages.append("- Reduce the price by 5 percent to {} dollars. \n".format(price*0.95))
    elif best_price_index == 2:
        messages.append("-  Reduce the price by 10 percent to {} dollars. \n".format(price*0.9))
    if best_desc_index == 0:
        messages.append("- Reduce the number of words in the description by  50 percent. \n")
    elif best_desc_index == 3:
        messages.append("- Include twice as many words in  the description. \n")
    if best_ratio_index == 0:
        messages.append("- Use longer sentences in the description. \n")
    elif best_ratio_index == 2: 
        messages.append("- Use shorter sentences in the description. \n")
    if best_lex_index == 0: 
        messages.append("- Formulate a less lexically diverse description.\n")
    elif best_lex_index == 2: 
        messages.append("- Formulate a more lexically diverse description. \n")
    if len(messages) > 0:
        messages.insert(0,"Your car will sell within {} days with a probability of {} percent if you \n".format(nr, max_prob))
    
    
    return (prob,  messages)
    
