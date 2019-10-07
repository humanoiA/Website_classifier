import requests

def new_api(api2_update):


	api2_request=requests.post('http://13.71.83.193/api/new-api?'+api2_update)
	

	if api2_request.status_code==200:
		print('New API POST SUCCESSFUL')
	else:
		print('Status code is ',api2_request.status_code)
		print('New API COULD NOT POST')


def website_data_api(api3_update,id):
	r=requests.post('http://13.71.83.193/api/website-data/'+id+'?'+api3_update)
	

	if r.status_code==200:
		print('Website data POST IS SUCCESSFUL')
	else:
		print('Status code is ',r.status_code)
		print('website data COULD NOT POST')