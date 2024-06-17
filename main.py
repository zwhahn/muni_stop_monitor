import requests
import config

# API Parameters
api_key = config.api_key
agency = 'AC'
stop_code = '14623'


url = f'http://api.511.org/transit/StopMonitoring?api_key={api_key}&agency={agency}&stopCode={stop_code}'

response = requests.get(url)
status = response.status_code
if status == 200:
    print("Succesful Request")
else:
    print(f'Request Fail: {status}')

print(response)

