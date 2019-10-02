#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:





# In[1]:


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
import  bs4
logging.getLogger('scrapy').propagate = False


# In[2]:


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


# In[3]:


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
r = requests.get('http://13.71.83.193/api/website-data?count=20') #for now keeping the count as 20
data=json.loads(r.text)


# In[47]:



websites=[]
api2_update=''
count=1
for j in range(len(data)):
    i=data[j]
    
    update='crawl_status=1'

    try:
        cat1=cat2=cat3=0
        #my_url='https://www.edsys.in/40-free-educational-websites-you-shouldnt-miss/'
                    
        
            
#         html_text = str(req.text) 
#         email_list = re.findall('\w+@\w+\.{1}\w+', html_text) 

#         dic = {'email': mail_list, 'link': str(req.url)} 
#         print(dic)
#         #df = pd.DataFrame(dic) #byme
#         email.append(dic)
        #df.to_csv(self.path, mode='a', header=False) 
        #df.to_csv(self.path, mode='a', header=False) 
        hdr = {'User-Agent': 'Mozilla/5.0'}
        if str(i['website']).startswith('http'):
            req = Request(str(i['website'].lower()),headers=hdr)
            websites.append(i['website'])
            website_url=i['website']
        else:
            req = Request('http://'+str(i['website'].lower()),headers=hdr)    
            websites.append('http://'+i['website'])
            website_url='http://'+i['website']
        uClient=uReq(req)
        page_html=uClient.read()
        uClient.close()
        word_tokens = word_tokenize(text_from_html(page_html))
        lmtzr = WordNetLemmatizer()
        group_list=str()
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
        if cat1==0 and cat2==0 and cat3==0:
            group_list=FreqDist(filtered_sentence).most_common(1)
        if cat1>=cat2 and cat1>=cat3:
            #print('Events--->'+str(i['website'].lower()))
            group_list='Events'
            update+='&events_found=1'
        elif cat2>=cat1 and cat2>=cat3:
            #print('Jobs--->'+str(i['website'].lower()))
            group_list='Jobs'
            update+='&jobs_found=1'
        else:
            #print('Education--->'+str(i['website'].lower()))
            group_list='Education'
            update+='&education_found=1'
        
        api2_update+='group'+str((count))+'='+group_list+'&'+'url'+str((count))+'='+str(website_url)+'&'

    # for email and phone numbers
        # finding email and contact on main page
        page = requests.get(website_url)
        main_contact=page.content

        main_contact_soup = BeautifulSoup(main_contact, 'html.parser')  #Parse html code
        text_of_main_contact = main_contact_soup.findAll(text=True)

        visible_texts = filter(tag_visible, text_of_main_contact)
        main_contact_html_text=u" ".join(t.strip() for t in visible_texts)

        main_contact_mail_list = re.findall('\w+@\w+\.{1}\w+', main_contact_html_text)
        #main_phone_list=re.findall("1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?",main_contact_html_text)
        main_phone_list=re.findall("|".join(["\+\d\d?-? ?\d{3}-\d{3}-\d{4}","\\+\\d\\d?-? ?\\d{10}","\\+\\d\\d?-? ?\\d{5} \\d{5}","\\+\\d\\d?-? ?\\d{3}\\-? ?\\d{7}","\\+\\d\\d?-? ?\\d{4}\\-? ?\\d{6}"]) ,main_contact_html_text)
        
        if len(main_contact_mail_list) is not 0:
            update+='&email_search=1'
            print("Email found at main Page: ",main_contact_mail_list)
            mail_string=''

            for mk in range(len(main_contact_mail_list)):
                if mk==len(main_contact_mail_list)-1:
                    mail_string+=str(main_contact_mail_list[mk])
                else:
                    mail_string+=str(main_contact_mail_list[mk])+','
            api2_update+='email'+str(count)+'='+mail_string+'&'
        if len(main_phone_list) is not 0:
            update+='&contact_found=1'

            phone_string=''
            print("Phone number found at main page: ",main_phone_list)
            for mp in range(len(main_phone_list)):
                if mp==len(main_phone_list)-1:
                    phone_string+=str(main_phone_list[mp])
                else:
                    #mail_string+=str(main_contact_mail_list[mk])+','
                    phone_string+=str(main_phone_list[mp])+','
            api2_update+='phone'+str(count)+'='+phone_string+'&'
        
        
        
        #finding mail and contact in website's contact page
        soup=bs4.BeautifulSoup(page.text,'html.parser')


        for link in soup.find_all('a',href=True):
            
            if str(link['href']).startswith('http') and 'contact' in str(link['href']).lower():

                try:
                    contact_page = requests.get(link['href'])  #to extract page from website
                except requests.exceptions.ConnectionError:
                    continue
                sc=contact_page.status_code
                if sc == 403:
                    continue
                f=contact_page.content

                contact_soup = BeautifulSoup(f, 'html.parser')  #Parse html code
                texts = contact_soup.findAll(text=True)

                visible_texts = filter(tag_visible, texts)
                html_text=u" ".join(t.strip() for t in visible_texts)

                mail_list = re.findall('\w+@\w+\.{1}\w+', html_text)
                phone_list=re.findall("|".join(["\+\d\d?-? ?\d{3}-\d{3}-\d{4}","\\+\\d\\d?-? ?\\d{10}","\\+\\d\\d?-? ?\\d{5} \\d{5}","\\+\\d\\d?-? ?\\d{3}\\-? ?\\d{7}","\\+\\d\\d?-? ?\\d{4}\\-? ?\\d{6}"]) ,html_text)
                
                
                #Updating strings for api and api3
                if len(mail_list) is not 0:
                    if 'email_search' not in update:
                        update+='&email_search=1'
                    mail_string=''
                    
                    for k in range(len(mail_list)):
                        if k==len(mail_list)-1:
                            mail_string+=str(mail_list[k])
                        else:
                            mail_string+=str(mail_list[k])+','
                    if 'email'+str(count) not in api2_update:
                        
                        api2_update+='email'+str(count)+'='+mail_string+'&'
                
                
                    
                if len(phone_list) is not 0:
                    if 'contact_found' not in update:
                        update+='&contact_found=1'
                    
                    phone_string=''
                    for p in range(len(phone_list)):
                        if p==len(phone_list)-1:
                            phone_string+=str(phone_list[p])
                        else:
                            phone_string+=str(phone_list[p])+','
                    if 'phone'+str(count) not in api2_update:
                        api2_update+='phone'+str(count)+'='+phone_string+'&'
                    
                
                
                print("Contact us page link: ",link['href'])
                if len(mail_list) is not 0:
                    print("Email found at Contact us page: ",mail_list)
                if len(phone_list) is not 0:
                    print("Phone number found at Contact us page: ",phone_list)
                break
                
    
    
    
    except Exception as e:
        print('Invalid website',i['website'])
        r=requests.post('http://13.71.83.193/api/website-data/'+str(i['id'])+'?'+"crawl_status=2")
        print('Update for {} website is crawl_status=2'.format(i['website']))
        print('-'*80)
        j+=1
        continue
    
    print('Update for {} website is {}'.format(website_url,update))
    
    r=requests.post('http://13.71.83.193/api/website-data/'+str(i['id'])+'?'+update)
    if r.status_code==200:
        print('API3 POST IS SUCCESSFUL')
    else:
        print('API3 COULD NOT POST')
    count=count+1
    print('-'*80)
#         traceback.print_exc()
#         fdist1 = FreqDist(filtered_sentence)
#         print('top_three keyword',str(fdist1.most_common(3))+'---'+str(i))
        

    #commenting for now
    
    
    
    
#     except Exception as e:     
#         #print(+'--> crawl_status=1')
#         r=requests.post('http://13.71.83.193/api/website-data/'+str(i['id'])+'?crawl_status=1')
#         if str(r.status_code)=='OK':
#             print('POST SUCCESSFUL')
#         else:
#             print('COULD NOT POST')
#         #traceback.print_exc()  


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[48]:


api2_update=api2_update[:-2]
#api2_update


# In[50]:



#calling api 2
api2_request=requests.post('http://13.71.83.193/api/new-api?'+api2_update)
if api2_request.status_code==200:
    print('API2 submitted successfullly')
else:
    print('API2 is not submitted')



# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




