import requests
import config
import codecs
import json
from datetime import datetime
import pytz

# Perform API Request
def api_request(api_key=config.api_key, agency=config.agency, stop_code=config.stop_code):
    url = f'http://api.511.org/transit/StopMonitoring?api_key={api_key}&agency={agency}&stopCode={stop_code}&format=JSON'

    response = requests.get(url)
    status = response.status_code
    if status == 200:
        print("Succesful Request")
    else:
        print(f'Request Fail: {status}')

    # JSON formatted resopnse, method from: https://groups.google.com/g/511sfbaydeveloperresources/c/K40TiNf8ydA
    response_json = json.loads(codecs.decode(response.content, encoding='utf-8-sig'))
    return response_json


# Extract needed information from JSON and reate bus_info dictionary
def get_bus_info(response_json):
    count = 0
    bus_info = {"bus1":{}, "bus2":{}, "bus3":{}}

    for item in response_json:
        # print("item: ", item)
        
        for subitem in response_json[item]:
            # print("subitem: ", response_json[item][subitem])

            # Check request status- Indicates success or failure of request.
            if subitem == "Status":
                if response_json[item][subitem] == True:
                    print("Status is True")
                else:
                    print("Request Failed")
            
            if subitem == "StopMonitoringDelivery":
                # print("Entered StopMonitoringDelivery")
                for subsubitem in response_json[item][subitem]:
                    # print("subsub: ", response_json[item][subitem][subsubitem])
                    pass
                if subsubitem == 'MonitoredStopVisit':
                    # print("Entered MonitoredStopVisit")
                    for subsubsubitem in response_json[item][subitem][subsubitem]:
                        # print("subsubsubitem type:", type(subsubsubitem))
                        for foursub in subsubsubitem['MonitoredVehicleJourney']:
                            if foursub == 'Monitored':
                                monitored_status = subsubsubitem['MonitoredVehicleJourney']['Monitored']
                                if count == 0:
                                    bus_info['bus1']['status'] = monitored_status
                                if count == 1:
                                    bus_info['bus2']['status'] = monitored_status
                                if count == 2:
                                    bus_info['bus3']['status'] = monitored_status
                    
                            # Data for the stop
                            if foursub == 'MonitoredCall':
                                # Convert Expected Arrival Time from string to DateTime object 
                                expected_arrival_time_str_UTC = subsubsubitem['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
                                expected_arrival_time_UTC = datetime.strptime(expected_arrival_time_str_UTC, '%Y-%m-%dT%H:%M:%SZ')

                                # Correct timezone (UTC to PT)
                                original_timezone = pytz.timezone(config.original_timezone)
                                target_timezone = pytz.timezone(config.target_timezone)

                                expected_arrival_time_UTC = original_timezone.localize(expected_arrival_time_UTC)  # Assign timezone to exisisting time
                                expected_arrival_time_PT = expected_arrival_time_UTC.astimezone(target_timezone)
                            
                                if count == 0:
                                    bus_info['bus1']['predicted_arrival_time'] = expected_arrival_time_PT
                                if count == 1:
                                    bus_info['bus2']['predicted_arrival_time'] = expected_arrival_time_PT
                                if count == 2:
                                    bus_info['bus3']['predicted_arrival_time'] = expected_arrival_time_PT
                            
                                count = count + 1
                                    
    return bus_info

response_json = api_request()
print(get_bus_info(response_json))