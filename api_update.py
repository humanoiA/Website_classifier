import requests

def API2(api2_update):


	api2_request=requests.post('http://13.71.83.193/api/new-api?'+api2_update)
	

	if api2_request.status_code==200:
		print('API2 POST SUCCESSFUL')
	else:
		print('API2 COULD NOT POST')


def API3(api3_update,id):
	r=requests.post('http://13.71.83.193/api/website-data/'+id+'?'+api3_update)
	

	if r.status_code==200:
		print('API3 POST IS SUCCESSFUL')
	else:
		print('API3 COULD NOT POST')