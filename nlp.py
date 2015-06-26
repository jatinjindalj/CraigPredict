from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


def tokenize(text):
    tokenizer = RegexpTokenizer('\w+|')
    tokens = tokenizer.tokenize(text)
   
    stems = []
    for item in tokens:
        stems.append(PorterStemmer().stem(item))
    tagged = pos_tag(stems)
    return [word for word, pos in tagged if (pos == 'JJ' or pos == 'RB')]

def tokenize2(text):
    tokens = word_tokenize(text) #keep 2gramx
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    tagged = pos_tag(tokens) #tokens
    return [word for word, pos in tagged if (pos == 'JJ' or pos == 'RB')]
# or  pos == 'NN'  or pos == 'NNS')]
    
