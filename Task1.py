import json
import requests
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.probability import FreqDist
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.request import urlopen as uReq
from urllib.request import Request
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
import string
import traceback
import re
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

keywords_event=['event','book','ticket']
keywords_jobs=['job','hiring','recruitment','career','skill','apply','salary','business','walk-in','vacancy','salary','experience','company','industry']
keywords_edu=['exam','class','entrance','kid','student','writing','read','quiz','course','education','management','video','science','math']
list_len=len(keywords_event)
for i in range(list_len):
    for syn in wordnet.synsets(keywords_event[i]):
        for name in syn.lemma_names():
            keywords_event.append(name)
list_len=len(keywords_jobs)
for i in range(list_len):
    for syn in wordnet.synsets(keywords_jobs[i]):
        for name in syn.lemma_names():
            keywords_jobs.append(name)
list_len=len(keywords_edu)
for i in range(list_len):
    for syn in wordnet.synsets(keywords_edu[i]):
        for name in syn.lemma_names():
            keywords_edu.append(name)
stop = stopwords.words('english') + list(string.punctuation)
r = requests.get('http://13.71.83.193/api/website-data?count=40')
data=json.loads(r.text)
for i in data:
    try:
        cat1=cat2=cat3=0
        #my_url='https://www.edsys.in/40-free-educational-websites-you-shouldnt-miss/'
        hdr = {'User-Agent': 'Mozilla/5.0'}
        if str(i['website']).startswith('http'):
            req = Request(str(i['website'].lower()),headers=hdr)
        else:
            req = Request('http://'+str(i['website'].lower()),headers=hdr)    
        uClient=uReq(req)
        page_html=uClient.read()
        uClient.close()
        word_tokens = word_tokenize(text_from_html(page_html))
        lmtzr = WordNetLemmatizer()
        filtered_sentence = [j for j in word_tokens if j not in stop] 
        for j in range(len(filtered_sentence)):
            filtered_sentence[j]=lmtzr.lemmatize(filtered_sentence[j].lower())
        for j in filtered_sentence:
            if j in keywords_edu:
                cat3+=1
        for j in filtered_sentence:
            if j in keywords_jobs:
                cat2+=1
        for j in filtered_sentence:
            if j in keywords_event:
                cat1+=1
        if cat1>=cat2 and cat1>=cat3:
            print('Events--->'+str(i['website'].lower()))
        elif cat2>=cat1 and cat2>=cat3:
            print('Jobs--->'+str(i['website'].lower()))
        else:
            print('Education--->'+str(i['website'].lower()))
        #fdist1 = FreqDist(filtered_sentence)
        #print(str(fdist1.most_common(3))+'---'+str(i))
    except Exception as e:
        print(str(i['website'])+'--> crawl_status=1')
        #traceback.print_exc()