#!/usr/bin/env python
# coding: utf-8

# In[69]:


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
import logging
import os
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import urllib
logging.getLogger('scrapy').propagate = False


# In[70]:


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


# In[71]:


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
r = requests.get('http://13.71.83.193/api/website-data?')
data=json.loads(r.text)


# In[72]:


websites=[]
for j in range(len(data)):
    i=data[j]

    try:
        cat1=cat2=cat3=0
        #my_url='https://www.edsys.in/40-free-educational-websites-you-shouldnt-miss/'
        hdr = {'User-Agent': 'Mozilla/5.0'}
        if str(i['website']).startswith('http'):
            req = Request(str(i['website'].lower()),headers=hdr)
            websites.append(i['website'])
        else:
            req = Request('http://'+str(i['website'].lower()),headers=hdr)    
            websites.append('http://'+i['website'])
            
        
            
#         html_text = str(req.text) 
#         email_list = re.findall('\w+@\w+\.{1}\w+', html_text) 

#         dic = {'email': mail_list, 'link': str(req.url)} 
#         print(dic)
#         #df = pd.DataFrame(dic) #byme
#         email.append(dic)
        #df.to_csv(self.path, mode='a', header=False) 
        #df.to_csv(self.path, mode='a', header=False) 
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
        #print(+'--> crawl_status=1')
        r=requests.post('http://13.71.83.193/api/website-data/'+str(i['id'])+'?crawl_status=1')
        if str(r.status_code)=='OK':
            print('POST SUCCESSFUL')
        else:
            print('COULD NOT POST')
        #traceback.print_exc()  


# In[1]:


# for i in websites:
#     print(i)


# In[74]:


contact_links=[]
emails_dic={}
phone_dic={}


# In[75]:


class MailSpider(scrapy.Spider):
    
    name = 'email'
    
    def parse(self, response):
        
        links = LxmlLinkExtractor(allow=()).extract_links(response)
        links = [str(link.url) for link in links]
        links.append(str(response.url))
        
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_link) 
            
    def parse_link(self, response):
        
#         for word in self.reject:
#             if word in str(response.url):
#                 return
        
        if 'contact' in str(response.url).lower():
        
            html_text = str(response.text)
            
            mail_list = re.findall('\w+@\w+\.{1}\w+', html_text)
            #phone_list=re.findall(r"+\d{2}\s?0?\d{10}",html_text)
            #phone_list=re.findall("/^[\.-)( ]*([0-9]{3})[\.-)( ]*([0-9]{3})[\.-)( ]*([0-9]{4})$/",html_text)
            phone_list=re.findall("1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?",html_text)
            #print(foundnum)
            print(str(response.url))
            contact_links.append(str(response.url)) 
            print(mail_list) 
            emails_dic[str(response.url)]= mail_list #storing in dictionary format
            phone_dic[str(response.url)]=phone_list #storing in dictionary format
            print(phone_list)
            print('-'*50)
        else:
            return


# In[76]:


reject_words = ['facebook', 'instagram', 'youtube', 'twitter', 'wiki']


# In[77]:


process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0'})
process.crawl(MailSpider, start_urls=websites , reject=reject_words)
process.start()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




