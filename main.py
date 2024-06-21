import requests
import config
import codecs
import json
from datetime import datetime
import pytz

# API Parameters
api_key = config.api_key
agency = 'SF'
stop_code = '14624'


url = f'http://api.511.org/transit/StopMonitoring?api_key={api_key}&agency={agency}&stopCode={stop_code}&format=JSON'

response = requests.get(url)
status = response.status_code
if status == 200:
    print("Succesful Request")
else:
    print(f'Request Fail: {status}')

headers = response.headers

# JSON formatted resopnse, method from: https://groups.google.com/g/511sfbaydeveloperresources/c/K40TiNf8ydA
response_json = json.loads(codecs.decode(response.content, encoding='utf-8-sig'))
# print(response_json)

for item in response_json:
    # print("item: ", item)
    
    for subitem in response_json[item]:
        # print("subitem: ", subitem)

        # Check request status- Indicates success or failure of request.
        if subitem == "Status":
            if response_json[item][subitem] == True:
                print("Status is True")
            else:
                print("Request Failed")
        
        if subitem == "StopMonitoringDelivery":
            print("Entered StopMonitoringDelivery")
            for subsubitem in response_json[item][subitem]:
                # print("subsub: ", subsubitem)
                pass
            if subsubitem == 'MonitoredStopVisit':
                # print("Entered MonitoredStopVisit")
                for subsubsubitem in response_json[item][subitem][subsubitem]:
                    # print("subsubsubitem:", subsubsubitem)
                    for foursub in response_json[item][subitem][subsubitem][0]:
                        # print("foursub: ", foursub)
                        if foursub == "MonitoredVehicleJourney":
                            # print("MonitoredVehicleJourney:", response_json[item][subitem][subsubitem][0]['MonitoredVehicleJourney'])

                            #Check that trip is monitiored
                            # print(response_json[item][subitem][subsubitem][0]['MonitoredVehicleJourney']['Monitored'])

                            # Data for the stop
                            # print(response_json[item][subitem][subsubitem][0]['MonitoredVehicleJourney']['MonitoredCall'])
                            
                            # Convert Expected Arrival Time from string to DateTime object 
                            expected_arrival_time_str_UTC = response_json[item][subitem][subsubitem][0]['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
                            expected_arrival_time_UTC = datetime.strptime(expected_arrival_time_str_UTC, '%Y-%m-%dT%H:%M:%SZ')

                            # Correct timezone (UTC to PT)
                            original_timezone = pytz.timezone('UTC')
                            target_timezone = pytz.timezone('US/Pacific')

                            expected_arrival_time_UTC = original_timezone.localize(expected_arrival_time_UTC)
                            expected_arrival_time_PT = expected_arrival_time_UTC.astimezone(target_timezone)


                            print("ExpectedArrivalTime: ", expected_arrival_time_PT)


                            

