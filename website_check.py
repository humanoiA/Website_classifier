#!/usr/bin/env python
# coding: utf-8

from earthy.wordlist import punctuations
from earthy.wordlist import stopwords as stop_criteria
from earthy.preprocessing import remove_stopwords
import re
import nltk.corpus
import logging
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
'''import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor'''
import urllib
import  bs4
logging.getLogger('scrapy').propagate = False

update='crawl_status=1'
websites=[]
api2_update=''
count=1
website_url=''
def removetags_fc(data_str):
    appendingmode_bool = True
    output_str = ''
    for char_str in data_str:
        if char_str == '>':
            appendingmode_bool = False
        elif char_str == '<':
            appendingmode_bool = True
            continue
        if appendingmode_bool:
            output_str += char_str
    return output_str

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

      #  logging.exception(':(')
       # r=requests.post('http://13.71.83.193/api/website-data/'+str(i['id'])+'?'+"crawl_status=2")
        
       # j+=1
def contact_extractor(id):
    global websites
    global website_url
    global update
    global api2_update
    global count
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
    print('-'*80)
                
    
    
    

    print('Update for {} website is {}'.format(website_url,update))
    count=count+1
    print('http://13.71.83.193/api/website-data/'+id+'?'+update)
'''
    if r.status_code==200:
        print('API3 POST IS SUCCESSFUL')
    else:
        print('API3 COULD NOT POST')
        '''
    #print('-'*80)
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
    
#
#if api2_request.status_code==200:
 #   print('API2 submitted successfullly')
##   print('API2 is not submitted')

def website_classifier():
    keywords_edu=['training','coaching']
    stop = stopwords.words('english') + list(string.punctuation) + list(stop_criteria['en'])+ list(punctuations)
    r = requests.get('http://13.71.83.193/api/website-data?count=10') #for now keeping the count as 20
    data=json.loads(r.text)

    global websites
    global website_url
    global update
    global api2_update
    global count
    for j in range(len(data)):
        i=data[j]
    
        update='crawl_status=1'

        try:
            cat1=cat2=cat3=0
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
            soup = BeautifulSoup(page_html, 'html.parser')
            text_string = soup.findAll(text=True)
            uClient.close()
            for link in soup.find_all('a'):
                if link.has_attr('href'):
                    if 'careers' in link.attrs['href'].lower():
                    #print('Jobs')
                        cat2+=1
                    if 'events' in link.attrs['href'].lower():
                    #print('Events')
                        cat1+=1
            word_tokens = word_tokenize(removetags_fc(text_string))
            lmtzr = WordNetLemmatizer()
            group_list=str()
            filtered_sentence = [a for a in word_tokens if a not in stop] 
            for a in range(len(filtered_sentence)):
                filtered_sentence[a]=lmtzr.lemmatize(filtered_sentence[a].lower())
            for a in filtered_sentence:
                if a in keywords_edu:
                    cat3+=1
            if cat1==0 and cat2==0 and cat3==0:
                nouns = [word for (word, pos) in nltk.pos_tag(word_tokens) if (pos[:2] == 'NN')] 
                common_word=FreqDist(nouns).most_common(15)
                for a in common_word:
                    if re.match(r'[a-z]+$',str(a[0]).lower()):
                        if i['group'] == '':
                            group_list=a[0]
                            print(group_list+'--->'+str(i['website'].lower()))
                            break
                        else:
                            group_list=i['group']
                            print(group_list+'--->'+str(i['website'].lower()))
                            break
            elif cat1==cat2 and cat1!=0 and cat2!=0:
                print('Jobs and Events--->'+str(i['website'].lower()))
                group_list='Jobs_and_Events'
                update+='&events_found=1&jobs_found=1'
            elif cat1==cat3 and cat1!=0 and cat3!=0:
                print('Education_and_Events--->'+str(i['website'].lower()))
                group_list='Education and Events'
                update+='&education_found=1&events_found=1'
            elif cat3==cat2 and cat3!=0 and cat2!=0:
                print('Jobs_and_Education--->'+str(i['website'].lower()))
                group_list='Jobs and Eduaction'
                update+='&education_found=1&jobs_found=1'
            elif cat1>cat2 and cat1>cat3:
                print('Events--->'+str(i['website'].lower()))
                group_list='Events'
                update+='&events_found=1'
            elif cat2>cat1 and cat2>cat3:
                print('Jobs--->'+str(i['website'].lower()))
                group_list='Jobs'
                update+='&jobs_found=1'
            elif cat3>cat1 and cat3>cat2:
                print('Education--->'+str(i['website'].lower()))
                group_list='Education'
                update+='&education_found=1'
            api2_update+='group'+str((count))+'='+group_list+'&'+'url'+str((count))+'='+str(website_url)+'&'
            contact_extractor(str(i['id']))
        except Exception as e:
            logging.exception(':(')   
            print('Update for {} website is crawl_status=2'.format(i['website']))
            print('-'*80)
            continue
website_classifier()
api2_update=api2_update[:-1]
print('http://13.71.83.193/api/new-api?'+api2_update)