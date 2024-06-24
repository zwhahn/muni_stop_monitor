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

def convert_UTC_to_PT(expected_arrival_time_UTC):
    # Correct timezone (UTC to PT)
    original_timezone = pytz.timezone(config.original_timezone)
    target_timezone = pytz.timezone(config.target_timezone)

    # Assign timezone to original time then convert
    expected_arrival_time_UTC = original_timezone.localize(expected_arrival_time_UTC)
    expected_arrival_time_PT = expected_arrival_time_UTC.astimezone(target_timezone)
    return expected_arrival_time_PT

# Calculate if bus is late, on_time, or early
def calculate_ProgressStatus(scheduled_time, expected_time):
    difference = expected_time - scheduled_time
    if abs(difference.total_seconds()) <= 120:
        return 'OnTime'
    if difference.total_seconds() > 120:
        return 'Late'
    if difference.total_seconds() < -120:
        return 'Early'


# Extract needed information from JSON and reate bus_info dictionary
def get_bus_info(response_json):
    count = 0
    bus_info = {"bus1":{}, "bus2":{}, "bus3":{}}
    bus_keys = list(bus_info.keys())

    for content in response_json:
        print("content", content)
        for header in response_json[content]:

            # Check request status- Indicates success or failure of request.
            if header == "Status":
                if response_json[content][header] == True:
                    print("Status is True")
                else:
                    print("Request Failed")
            
            if header == "StopMonitoringDelivery":
                # print("Entered StopMonitoringDelivery")
                for StopMonitoringDelivery_var in response_json[content][header]:
                    # print("StopMonitoringDelivery_var: ", StopMonitoringDelivery_var)
                    if StopMonitoringDelivery_var == 'MonitoredStopVisit':
                        # print("Entered MonitoredStopVisit")
                        for MonitoredStopVisit_var in response_json[content][header][StopMonitoringDelivery_var]:
                            for MonitoredVehicleJourney_var in MonitoredStopVisit_var['MonitoredVehicleJourney']:
                                if count > len(bus_keys):
                                    break
                                # Check bus is monitored
                                if MonitoredVehicleJourney_var == 'Monitored':
                                    monitored_status = MonitoredStopVisit_var['MonitoredVehicleJourney']['Monitored']
                                    bus_info[bus_keys[count]]['status'] = monitored_status
                        
                                # Find epected arrival time and aimed arrival time
                                if MonitoredVehicleJourney_var == 'MonitoredCall':
                                    # Convert Expected Arrival Time from string to DateTime object 
                                    expected_arrival_time_str_UTC = MonitoredStopVisit_var['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
                                    aimed_arrival_time_str_UTC = MonitoredStopVisit_var['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime']

                                    expected_arrival_time_UTC = datetime.strptime(expected_arrival_time_str_UTC, '%Y-%m-%dT%H:%M:%SZ')
                                    aimed_arrival_time_UTC = datetime.strptime(aimed_arrival_time_str_UTC, '%Y-%m-%dT%H:%M:%SZ')

                                    # Correct timezone (UTC to PT)
                                    expected_arrival_time_PT = convert_UTC_to_PT(expected_arrival_time_UTC)
                                    aimed_arrival_time_PT = convert_UTC_to_PT(aimed_arrival_time_UTC)
                                    
                                    bus_info[bus_keys[count]]['ExpectedArrivalTime'] = expected_arrival_time_PT
                                    bus_info[bus_keys[count]]['AimedArrivalTime'] = aimed_arrival_time_PT

                                    bus_info[bus_keys[count]]['ProgressStatus'] = calculate_ProgressStatus(aimed_arrival_time_PT, expected_arrival_time_PT)

                                    count = count + 1
    return bus_info

response_json = api_request()
# print(response_json)
bus_info = get_bus_info(response_json)
print(bus_info)