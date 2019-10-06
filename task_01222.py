
import api_update # python script for calling APIs
import numpy as np
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
import urllib
import  bs4
logging.getLogger('scrapy').propagate = False

update='crawl_status=1' #stores parameters to be passed onto api/changes to crawl status=2 if webpage is not accessible
websites=[]#stores the list of websites
api2_update=''#stores the parameters for every site like which group list it belongs to and contact 
count=1#used to iterate through website id
website_url=''#stores website url
def removetags_fc(data_str):
    '''This function is used to remove all html tags from the String

        return:
            a string without html tags
    '''
    #function to remove html tags 
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
    '''This function is a helper function to removes all the html tags from the element
            it finds all visible text excluding scripts, comments, css etc.

            
            return:
                True or False

    '''
    #function to remove html tags
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    ''' This function is used to extract text from html page ,it uses function tag_visible() as a helper funciton 

            parameter:
                html content of page
            return:
                String of all visible text
    '''
    #function to extract text from html page
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)


def contact_extractor(id):

    '''This Function Extracts Emails and Phone numbers from Website's homepage as well as their contact page'''

    global websites
    global website_url
    global update
    global api2_update
    global count

    
    mail_string=''  #Initialising string for emails at website's home page
    phone_string='' #Initialising string for phone number at website's home page
    mail_string1='' #Initialising string for emails at website's Contact page
    phone_string1='' #Initialising string for phone number at website's home page
    page = requests.get(website_url)
    main_contact=page.content


    main_contact_soup = BeautifulSoup(main_contact, 'html.parser')  #Parse html code
    text_of_main_contact = main_contact_soup.findAll(text=True)

    visible_texts = filter(tag_visible, text_of_main_contact)
    main_contact_html_text=u" ".join(t.strip() for t in visible_texts)


    #Email_list for homepage
    all_main_contact_mail_list = re.findall('\w+@\w+\.{1}\w+', main_contact_html_text) 

    #Phone number list for homepage
    all_main_phone_list=re.findall("|".join(["\+\d\d?-? ?\d{3}-\d{3}-\d{4}","\\+\\d\\d?-? ?\\d{10}","\\+\\d\\d?-? ?\\d{5} \\d{5}","\\+\\d\\d?-? ?\\d{3}\\-? ?\\d{7}","\\+\\d\\d?-? ?\\d{4}\\-? ?\\d{6}"]) ,main_contact_html_text)

    main_contact_mail_list=np.unique(all_main_contact_mail_list)
    main_phone_list=np.unique(all_main_phone_list)


    if len(main_contact_mail_list) is not 0:
        update+='&email_search=1'
        print("Email found at main Page: ",main_contact_mail_list)
        

        for mk in range(len(main_contact_mail_list)):
            if mk==len(main_contact_mail_list)-1:
                mail_string+=str(main_contact_mail_list[mk])
            else:
                mail_string+=str(main_contact_mail_list[mk])+','
    if len(main_phone_list) is not 0:
        update+='&contact_found=1'

        print("Phone number found at main page: ",main_phone_list)
        for mp in range(len(main_phone_list)):
            if mp==len(main_phone_list)-1:
                phone_string+=str(main_phone_list[mp])
            else:
                phone_string+=str(main_phone_list[mp])+','



#finding Emails and Phone numbers in website's contact page
    soup=bs4.BeautifulSoup(page.text,'html.parser')

    #looping over all link present at homepage
    for link in soup.find_all('a',href=True):


    
        #Chosing only ContactUs link of website
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

            #Using Regex for extracting Emails and Phone numbers at contactUs page
            all_mail_list = re.findall('\w+@\w+\.{1}\w+', html_text)
            all_phone_list=re.findall("|".join(["\+\d\d?-? ?\d{3}-\d{3}-\d{4}","\\+\\d\\d?-? ?\\d{10}","\\+\\d\\d?-? ?\\d{5} \\d{5}","\\+\\d\\d?-? ?\\d{3}\\-? ?\\d{7}","\\+\\d\\d?-? ?\\d{4}\\-? ?\\d{6}"]) ,html_text)
        
            #taking out only unique emails and phone numbers
            mail_list=np.unique(all_mail_list)
            phone_list=np.unique(all_phone_list)



            if len(mail_list) is not 0:
                if 'email_search' not in update:
                    update+='&email_search=1'
            
                for k in range(len(mail_list)):
                    if k==len(mail_list)-1:
                        mail_string1+=str(mail_list[k])
                    else:
                        mail_string1+=str(mail_list[k])+','
                                        
                
                    
            if len(phone_list) is not 0:
                if 'contact_found' not in update:
                    update+='&contact_found=1'
                    
                for p in range(len(phone_list)):
                    if p==len(phone_list)-1:
                        phone_string1+=str(phone_list[p])
                    else:
                        phone_string1+=str(phone_list[p])+','
                    
                
                
            print("Contact us page link: ",link['href'])
            if len(mail_list) is not 0:
                print("Email found at Contact us page: ",mail_list)
            if len(phone_list) is not 0:
                print("Phone number found at Contact us page: ",phone_list)
            break

    

    #API2 string update.....adding Emails
    if len(mail_string)==0 and len(mail_string1) is not 0:
    	api2_update+='email'+str(count)+'='+mail_string1+'&'
    elif len(mail_string1)==0 and len(mail_string) is not 0:
    	api2_update+='email'+str(count)+'='+mail_string+'&'
    elif len(mail_string1) is not 0 and len(mail_string) is not 0:
    	mail_update=mail_string+','+mail_string1
    	api2_update+='email'+str(count)+'='+mail_update+'&'


    #API2 string update....adding Phone numbers 
    if len(phone_string)==0 and len(phone_string1) is not 0:
    	api2_update+='phone'+str(count)+'='+phone_string1+'&'
    elif len(phone_string1)==0 and len(phone_string) is not 0:
    	api2_update+='phone'+str(count)+'='+phone_string+'&'
    elif len(phone_string1) is not 0 and len(phone_string) is not 0:
    	phone_update=phone_string+phone_string1
    	api2_update+='phone'+str(count)+'='+phone_update+'&'


    print('Update for {} website is {}'.format(website_url,update))
    count=count+1
    print('http://13.71.83.193/api/website-data/'+id+'?'+update)
    #Requesting API3 for update
    api_update.API3(update,id) #API3 call
    print('-'*80)


def website_classifier():
    '''This function classifies the website on the basis of its content'''




    keywords_edu=['training','coaching']#keyword to classify whether it is an education website or not
    stop = stopwords.words('english') + list(string.punctuation) + list(stop_criteria['en'])+ list(punctuations)#to remove stopwords from text extracted from webpage like . , ; i,am, the etc.  
    r = requests.get('http://13.71.83.193/api/website-data?count=40') #for now keeping the count as 40
    data=json.loads(r.text)#to load data from api 

    global websites
    global website_url
    global update
    global api2_update
    global count
    for j in range(len(data)):
        i=data[j]
    
        update='crawl_status=1'

        try:
            cat1=cat2=cat3=0#cat1-category1 belongs to events | cat2- category2 belongs to jobs | cat3-category3 belongs to education
            hdr = {'User-Agent': 'Mozilla/5.0'}
            #checking if web address starts with http or not, if not adding http at the beginning of address
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
                    if 'careers' in link.attrs['href'].lower():#checking if website has a career link
                        cat2+=1
                    if 'events' in link.attrs['href'].lower():#checking if website has an event link
                        cat1+=1
            word_tokens = word_tokenize(removetags_fc(text_string))#tokenizing words from website
            lmtzr = WordNetLemmatizer()
            group_list=str()
            filtered_sentence = [a for a in word_tokens if a not in stop] #removing stop words
            for a in range(len(filtered_sentence)):
                filtered_sentence[a]=lmtzr.lemmatize(filtered_sentence[a].lower())#lemmetizing words; ex-running can be writtten as run || converting words into their original form
            for a in filtered_sentence:
                if a in keywords_edu:
                    cat3+=1#checking if there is any match with education keywords
            if cat1==0 and cat2==0 and cat3==0:
                nouns = [word for (word, pos) in nltk.pos_tag(word_tokens) if (pos[:2] == 'NN')]#extracting only noun from we address 
                common_word=FreqDist(nouns).most_common(15)#finding frequency distribution of most common words
                for a in common_word:
                    if re.match(r'[a-z]+$',str(a[0]).lower()):#if common word has only words then assign it to group_list(the group assigned to the webpage like education,jobs etc), do not assign if any word like hello134 is found
                        if i['group'] == '':#assign to group list only if the websie is not grouped earlier as there are some false outputs
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
            api2_update+='group'+str((count))+'='+group_list+'&'+'url'+str((count))+'='+str(website_url)+'&'#api2 update 
            contact_extractor(str(i['id']))
            
        except Exception as e:
            #logging.exception(':(')   
            print('Update for {} website is crawl_status=2'.format(i['website']))
            #Request for API3 update
            api_update.API3('crawl_status=2',str(i['id'])) #API3 call
            print('-'*80)
            continue


website_classifier()

#Requesting API2 update
api2_update=api2_update[:-1]
print('Update sending to API2 is ---->  '+api2_update)

api_update.API2(api2_update) #API2 call


# print('docstring of funcitons ')
# print(website_classifier.__doc__)
# print(contact_extractor.__doc__)


