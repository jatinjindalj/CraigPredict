from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import nltk
import numpy as np


def tokenize(text):
    #tokens = word_tokenize(text) #keep 2gramx
    tokenizer = RegexpTokenizer('\w+|')#\d+')#'\w+|\$[\d\.]+|\S+')
    tokens = tokenizer.tokenize(text)   
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    stems = []
    for item in tokens:
        stems.append(PorterStemmer().stem(item))
    tagged = pos_tag(stems) #tokens
    return [word for word, pos in tagged if (pos == 'JJ' or pos == 'RB')]
   #pos == 'NNP' oror pos == 'CD'pos == 'NNP' or  pos == 'NN' or pos == 'NNS' or 
        
def sentence_count(text):
    if text != "":
        punct_tokenizer  = nltk.data.load('tokenizers/punkt/english.pickle')
        sentences =  punct_tokenizer.tokenize(text)
        return len(sentences)
    else:
        return 0
    
def lexical_diversity(text):
    #tokenizer = RegexpTokenizer('\w+|')#\d+')#'\w+|\$[\d\.]+|\S+')
    #tokens = tokenizer.tokenize(text)   
    tokens = word_tokenize(text)   
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    stems = []
    for item in tokens:
        stems.append(PorterStemmer().stem(item))
    unique_stems = np.unique(stems)

    return len(tokens)/(len(unique_stems)+1.)