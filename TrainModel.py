#Train random forest model
import numpy as np
import pandas as pd
import nltk as nltk
import pymysql as mdb
import sklearn
from sklearn.ensemble import RandomForestClassifier
import pickle
import nlp
from scipy import interp
import matplotlib.pyplot as plt

def trainModel():
    con = mdb.connect('localhost', 'charlotte', 'insight', 'LocalClassifieds')
    #df = pd.read_sql("SELECT * FROM ToyotaCamry", con)
    #df = pd.read_sql("SELECT * FROM NissanAltima", con)
    #df = pd.read_sql("SELECT * FROM HondaAccord", con)
    df = pd.read_sql("SELECT * FROM HondaCivic", con)
    
    #data = df[ (df['SoldDays'] > 0)  & (df['CarModel'].str.contains(r"[tT][oO][yY][oO][tT][aA] [cC][aA][mM][rR][yY]"))   ]  #completed items
    #data = df[ (df['SoldDays'] > 0)   & (df['CarModel'].str.contains(r"[nN][iI][sS][sS][aA][nN] [aA][lL][tT][iI][mM][aA]"))   ]
    #data = df[ (df['SoldDays'] > 0)  & (df['CarModel'].str.contains(r"[Hh][oO][nN][dD][aA] [aA][cC][cC][oO][rR][dD]"))   ]
    data = df[ (df['SoldDays'] > 0) &  (df['CarModel'].str.contains(r"[Hh][oO][nN][dD][aA] [cC][iI][vV][iI][cC]"))   ]
    data['Odometer'] =  data['Odometer'].convert_objects(convert_numeric=True)   
    data.loc[data['Odometer'].isnull(), 'Odometer'] = -10000
    data.reset_index(inplace = True)
    print "Number of training items: {}".format(len(data))
    #extract variables year, length of title/description, map categorical variables onto numbers
    year = data['CarModel'].str.split(" ")
    data['Year'] =  [int(y[0]) for y in year]
    data['LenTitle'] = data['Title'].str.split().apply(lambda x: len(x)) -1
    data['LenDescription']  =  data['Description'].str.split().apply(lambda x: len(x))-1
    data.loc[(data['Fuel'] == 'gas'), 'Fuel'] = 1
    data.loc[data['Fuel'] != 1, 'Fuel']= 0
    data.loc[(data['Transmission'] == 'automatic'), 'Transmission'] = 1
    data.loc[data['Transmission'] != 1, 'Transmission']= 0
    data.loc[(data['Cylinders'] == ""), 'Cylinders'] = 0
    data.loc[data['Cylinders'] != 0, 'Cylinders']= 1   
    data.loc[(data['Drive'] == ""), 'Drive'] = 0
    data.loc[data['Drive'] != 0, 'Drive']= 1   
    data.loc[(data['CarStatus'] == "clean"), 'CarStatus'] = 1
    data.loc[data['CarStatus'] != 1, 'CarStatus']= 0 
    for col in data[['Color','CarType']].columns:
        categories = data[col].unique()
        cat_dict = {}
        i=1
        for cat in categories:
            cat_dict.update({cat: i})
            i += 1
        data[col] = data[col].map(cat_dict)    
        #par = pickle.dump(cat_dict, open( col+"_ToyotaCamry_Dict.p", "wb" ) )
        #par = pickle.dump(cat_dict, open( col+"_NissanAltima_Dict.p", "wb" ) )
        #par = pickle.dump(cat_dict, open( col+"_HondaAccord_Dict.p", "wb" ) )
        par = pickle.dump(cat_dict, open( col+"_HondaCivic_Dict.p", "wb" ) )

    X1 = data[['Contact','NrPics','Price','LenTitle','LenDescription','COORD',
      'Cylinders','Drive','Fuel','Odometer','Color','CarStatus','Transmission','Year','CarType','NrLinks']].values
    DataDict = {}
    DataDict.update({0: 'Contact',  1: 'NrPics',  2 :'Price', 3: 'LenTitle', 4 : 'LenDescription',
                     5: 'COORD',  6: 'Cylinders', 7 :'Drive', 8: 'Fuel', 9: 'Odometer',
                     10: 'Color', 11: 'CarStatus', 12: 'Transmission', 13: 'Year', 14: 'CarType',15: 'NrLinks'})

    X = X1
    max_scores = np.zeros(31)
    best_feat = np.zeros(31)
    best_depth = np.zeros(31)
    features = []
    

    
    #Find best random forest parameters for each n (max_features and max_depth)
    for n in range(1,21,1):
        data['Sold'] = 0
        data.loc[data['SoldDays'] <= n, 'Sold'] = 1
        YC = data['Sold']   #Classification model output variable
        print data['Sold'].value_counts()
        for max_feat in range(2,16,2):  #number of features considered in each split of the tree
            for depth in range(10,200,10): #max depth of the tree
                n_folds = 10
                cv = sklearn.cross_validation.StratifiedKFold(YC,n_folds,shuffle = True)
                scores = np.zeros(n_folds)
                for f,(train, test) in enumerate(cv):
                    learner = RandomForestClassifier(n_estimators=500, max_depth=depth,  max_features= max_feat)
                    learner.fit(X[train,:],YC[train])
                    probs = learner.predict_proba(X[test,:])    
                    if probs.shape[1] > 1:
                        fpr, tpr, thresholds = sklearn.metrics.roc_curve(YC[test], probs[:,1])
                        scores[f] = sklearn.metrics.auc(fpr,tpr)
                    else:
                        scores[f] = 0
                    if np.mean(scores) > max_scores[n]:
                        max_scores[n] = np.mean(scores)
                        best_feat[n] = max_feat
                        best_depth[n] = depth
                        features.append(learner.feature_importances_)#coef_)
                         
        print "For n = {}, best auc is {}  for max feat = {}, max depth = {}".format(n, max_scores[n],  best_feat[n], best_depth[n])
        coeff = np.abs(features[n])
        coeff = coeff.ravel()
        sorted_coeff = np.sort(coeff)
        sorted_indices = np.argsort(coeff)
     
        for i in range(1,25):
            index = sorted_indices[len(coeff)-i]
            print DataDict[index], sorted_coeff[len(coeff)-i]

    #Train models for each n using best params found above
    for n in range(1,21,1):
        print n, best_depth[n], best_feat[n]
        data['Sold'] = 0
        data.loc[data['SoldDays'] <= n, 'Sold'] = 1
        YC = data['Sold']
        learner = RandomForestClassifier(n_estimators=500, max_depth=best_depth[n],  max_features= int(best_feat[n]))
        learner.fit(X,YC)
        par = pickle.dump(learner, open( "RFLearnerHondaCivicNoText"+str(n)+".p", "wb" ) )
        #par = pickle.dump(learner, open( "RFLearnerHondaAccordNoText"+str(n)+".p", "wb" ) )
        #par = pickle.dump(learner, open( "RFLearnerToyotaCamryNoText"+str(n)+".p", "wb" ) )
        #par = pickle.dump(learner, open( "RFLearnerNissanAltimaNoText"+str(n)+".p", "wb" ) )

    #Make plot of mean ROCs for n=5 (prob of sale within 5 days)
    for n in range(3,18,3):
        data['Sold'] = 0
        data.loc[data['SoldDays'] <= n, 'Sold'] = 1
        YC = data['Sold']
        n_folds = 5
        mean_tpr = 0.0
        mean_fpr = np.linspace(0, 1, 100)
        all_tpr = []
        cv = sklearn.cross_validation.StratifiedKFold(YC,n_folds,shuffle = True)
        for f,(train, test) in enumerate(cv):
            learner = RandomForestClassifier(n_estimators=500, max_depth=best_depth[n],  max_features= int(best_feat[n]) )
            learner.fit(X[train,:],YC[train])
            probs = learner.predict_proba(X[test,:])
            if probs.shape[1] > 1:
                fpr, tpr, thresholds = sklearn.metrics.roc_curve(YC[test], probs[:,1])
                auc = sklearn.metrics.auc(fpr,tpr)
                mean_tpr += interp(mean_fpr, fpr, tpr)
                mean_tpr[0] = 0.0

        mean_tpr /= len(cv)
        mean_tpr[-1] = 1.0
        mean_auc = sklearn.metrics.auc(mean_fpr, mean_tpr)
        plt.plot(mean_fpr, mean_tpr, '-', label='Mean ROC n =%d (area = %0.2f) ' % (n,mean_auc), lw=2)
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC Honda Civic: Prob. of sale within 5 days')
    #plt.title('ROC Toyota Camry: Prob. of sale within 5 days')
    #plt.title('ROC Honda Accord: Prob. of sale within 5 days')
    #plt.title('ROC Nissan Altima: Prob. of sale within 5 days')
    plt.legend(loc="lower right")
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6))
    #plt.savefig('ROC_RF_NoText_HondaCivic.pdf')
    #plt.savefig('ROC_RF_NoText_HondaAccord.pdf')
    #plt.savefig('ROC_RF_NoText_NissanAltima.pdf')
    #plt.savefig('ROC_RF_NoText_ToyotaCamry.pdf')

trainModel()

 
