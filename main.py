import requests
import config
import codecs
import json

# API Parameters
api_key = config.api_key
agency = 'AC'
stop_code = '14623'


url = f'http://api.511.org/transit/StopMonitoring?api_key={api_key}&agency={agency}&stopCode={stop_code}&format=JSON'

response = requests.get(url)
status = response.status_code
if status == 200:
    print("Succesful Request")
else:
    print(f'Request Fail: {status}')

headers = response.headers['content-type']

# JSON formatted resopnse, method from: https://groups.google.com/g/511sfbaydeveloperresources/c/K40TiNf8ydA
response_json = json.loads(codecs.decode(response.content, encoding='utf-8-sig'))

print(response_json)


