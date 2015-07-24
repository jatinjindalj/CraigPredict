import numpy as np
import pandas as pd
import nltk as nltk
import pymysql as mdb
import sklearn
import scipy as sci
from sklearn.ensemble import RandomForestClassifier
import nlp
import pickle
from scipy import interp
import matplotlib.pyplot as plt



def trainModel():
    con = mdb.connect('localhost', 'charlotte', 'insight', 'LocalClassifieds')
    df = pd.read_sql("SELECT * FROM ToyotaCamry", con)
    #df = pd.read_sql("SELECT * FROM NissanAltima", con)
    data = df[ (df['SoldDays'] > 0)    & (df['CarModel'].str.contains(r"[tT][oO][yY][oO][tT][aA] [cC][aA][mM][rR][yY]"))   ]
    #data = df[ (df['SoldDays'] > 0)   & (df['CarModel'].str.contains(r"[nN][iI][sS][sS][aA][nN] [aA][lL][tT][iI][mM][aA]")) ]
    data.reset_index(inplace = True)
    print "Number of training items: {}".format(len(data))
    year = data['CarModel'].str.split(" ")
    data['Year'] =  [int(y[0]) for y in year]
    data['Odometer'] =  data['Odometer'].convert_objects(convert_numeric=True)
    data.loc[(data['Odometer'] < 1000) & (data['Year'] < 2015),'Odometer'] *= 1000  #often, 178000 given as 178etc.
    data.loc[data['Odometer'].isnull(), 'Odometer'] = -10000
    #variables: length of title, length of description, lexical diversity, nr sentences/nr words
    data['LenTitle'] = data['Title'].str.split().apply(lambda x: len(x)) -1
    data['LenDescription']  =  data['Description'].str.split().apply(lambda x: len(x))
    data['RatioSentencesWords'] = [nlp.sentence_count(text.decode('utf-8')) for text in data['Description'].values]
    data['RatioSentencesWords'] = data['RatioSentencesWords']/ (data['LenDescription']+1.)
    
    data['LexDiversity'] =  [nlp.lexical_diversity(text.decode('utf-8')) for text in data['Description'].values]
   
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
        par = pickle.dump(cat_dict, open( col+"_NissanAltima_Dict.p", "wb" ) )
    
    data.loc[data['Location'].isnull(), 'Location'] = ""
    data['Location'] = data['Location'].str.lower()
    locs = data['Location'].unique()
    loc_cts = data['Location'].value_counts()
    loc_dict = {}
    i=1
    for loc in locs:
        if loc_cts[loc] >= 5:
            loc_dict.update({loc: i})
        else: 
            loc_dict.update({loc: 0})
        i += 1
    data['LocationCats'] = data['Location'].map(loc_dict)
    #par = pickle.dump(loc_dict,open("LocationDict_ToyotaCamry.p","wb"))
    par = pickle.dump(loc_dict,open("LocationDict_NissanAltima.p","wb"))

    X1 = data[['Contact','NrPics','Price','LenTitle','LenDescription','COORD','Cylinders','Drive','Fuel',
    'Odometer','Color','CarStatus','Transmission','Year','CarType','NrLinks','LexDiversity',
    'RatioSentencesWords','LocationCats']].values
    DataDict = {}
    DataDict.update({0: 'Contact',  1: 'NrPics',  2 :'Price', 3: 'LenTitle', 4 : 'LenDescription',
                     5: 'COORD',  6: 'Cylinders', 7 :'Drive', 8: 'Fuel', 9: 'Odometer',10: 'Color',
                    11: 'CarStatus', 12: 'Transmission', 13: 'Year', 14: 'CarType',15:'NrLinks',
                    16: 'LexDiversity',17:'RatioSentencesWords', 18: 'LocationCats'})

    X = X1
    max_scores = np.zeros(31)
    best_feat = np.zeros(31)
    best_depth = np.zeros(31)
    features = []
    #params = open('BestParamsToyotaCamry_NY_NoText.txt', 'w+')
    params = open('BestParamsNissanAltima_NY_NoText.txt', 'w+')
    for n in range(1,21,1):
        data['Sold'] = 0
        data.loc[data['SoldDays'] <= n, 'Sold'] = 1
        YC = data['Sold']   #Classification model output variable
        print data['Sold'].value_counts()
        for max_feat in range(2,16,2):
            for depth in range(30,110,20):
                n_folds = 10
                cv = sklearn.cross_validation.StratifiedKFold(YC,n_folds,shuffle = True)
                scores = np.zeros(n_folds)
                for f,(train, test) in enumerate(cv):
                    learner = RandomForestClassifier(n_estimators=300, max_depth=depth,  max_features= max_feat)               
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
                    features.append( learner.feature_importances_)
                         
        print "For n = {}, best AUC is {}  for max feat = {}, max depth = {}".format(n, max_scores[n],  best_feat[n], best_depth[n])
        params.write("For n = {}, best AUC is {}  for max feat = {}, max depth = {}\n".format(n, max_scores[n],  best_feat[n], best_depth[n]))
        coeff = features[n]
        sorted_coeff = np.sort(coeff)
        sorted_indices = np.argsort(coeff)
        for i in range(1,19):
            
            index = sorted_indices[len(coeff)-i]
            print DataDict[index], sorted_coeff[len(coeff)-i]
    params.close()

   
    for n in range(1,21,1):
        print n, best_depth[n], best_feat[n]
        data['Sold'] = 0
        data.loc[data['SoldDays'] <= n, 'Sold'] = 1
        YC = data['Sold']
        learner = RandomForestClassifier(n_estimators=500, max_depth=best_depth[n],  max_features= int(best_feat[n]))                    
        learner.fit(X,YC)
        #par = pickle.dump(learner, open( "RFLearnerToyotaCamryNoTextNYC"+str(n)+".p", "wb" ) )
        #par = pickle.dump(learner, open( "RFLearnerNissanAltimaNoTextNYC"+str(n)+".p", "wb" ) )
 
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
            learner = RandomForestClassifier(n_estimators=1000, max_depth=best_depth[n],  max_features= int(best_feat[n]) )                   
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
        plt.plot(mean_fpr, mean_tpr, '-', label='Mean CV ROC d =%d (AUC = %0.2f) ' % (n,mean_auc), lw=2)
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC Toyota Camry: Prob. of sale within d days')
    #plt.title('ROC Nissan Altima: Prob. of sale within d days')
    plt.legend(loc="lower right")
    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6))
    #plt.savefig('ROC_RF_NoText_NissanAltima_NYC.pdf')
    plt.savefig('ROC_RF_NoText_ToyotaCamry_NYC.pdf')

trainModel()

 
