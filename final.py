import pandas as pd
import mysql.connector
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.probability import FreqDist
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import string
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')
stop = stopwords.words('english') + list(string.punctuation)
file = open('Interest groups - 5th Sept.txt','r')
words=file.read().split('\n')
mydb= mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="6ff949d8e428",
    database="dbms_assignment")
mycursor = mydb.cursor()
#print(words[5])
stop_words = set(stopwords.words('english'))
df = pd.read_csv('top-1m.csv',header=None)
df=df.head(1500)
site_link=df.iloc[:,1]
for i in site_link:
    try:
        max=0
        html = urllib.request.urlopen('https://'+str(i)).read()
        #tokenizer.tokenize(text_from_html(html))
        word_tokens = word_tokenize(text_from_html(html))
        #filtered_sentence = [w for w in word_tokens if not w in stop_words] 
        filtered_sentence = [i for i in word_tokens if i not in stop] 
        sum=0
        category=''
        #for w in word_tokens: 
         #   if w not in stop_words: 
          #      filtered_sentence.append(w) 
        #print(site_text)
        for j in words:
            count = filtered_sentence.count(j)
            if(count>=1):
                if max<count:
                    max=count
                    category=j
                sum+=count
        if max==0 or sum==0:
            fdist1 = FreqDist(filtered_sentence)
            print(str(fdist1.most_common(3))+'---'+str(i))
            mycursor.execute("INSERT INTO website_classifier (site_address, confidence_category_or_top_keyword) VALUES('"+str(i)+"','"+str(fdist1.most_common(3)).replace("\'",'').replace("()",'')+"')")
            mydb.commit()
        else:
            a=str(max/sum)+'---'+category
            print(a+'---'+str(i))
            mycursor.execute("INSERT INTO website_classifier (site_address, confidence_category_or_top_keyword) VALUES('"+str(i)+"','"+a+"')")
            mydb.commit()
    except Exception as e:
        print(e)
  #      print('')#   print('END---\n')