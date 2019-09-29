import requests
#for crawl_status
id=1
r=requests.post('http://13.71.83.193/api/website-data/'+id+'?crawl_status=1')
if str(r.status_code)=='OK':
    print('POST SUCCESSFUL')
else:
    print('COULD NOT POST')
#for email/contact found
phone=132435465
mail='john.doe@email.com'
r=requests.post('http://13.71.83.193/api/new-api?phone1='+phone+'&email1='+mail)
if str(r.status_code)=='OK':
    print('POST SUCCESSFUL')
else:
    print('COULD NOT POST')
