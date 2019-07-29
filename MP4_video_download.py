import requests
import json
import sys
import local_settings

###
# Setup Information
###


# automatically manage cookies between requests
session = requests.Session()

# Enter your credentials
username = ""
password = ""
api_key = ""

if username == "" or password == "" or api_key == "":
    
    # look to see if there are credentials in local_settings.py
    username = local_settings.username
    password = local_settings.password
    api_key = local_settings.api_key

    if username == "" or password == "" or api_key == "":
        print("Please put in your credentials")
        sys.exit()

# Put in valid start time and endtime in EEN format.  
# All times in our system are in the UTC timezone.
# For example, November 21, 2018 01:23:45 AM would translate to 20181121012345.000
# (the last three digits are for microseconds)

start_timestamp = ""
end_timestamp =   ""

if start_timestamp == "" or end_timestamp == "":
    print("Please put in a start and ending time")
    sys.exit()


# Translating the HTTP response codes to make the status messages easier to read
HTTP_STATUS_CODE = { 
    200: 'OK', 
    202: 'ACCEPTED',
    400: 'Bad Request, please check what you are sending',
    401: 'User needs to Login first', 
    403: 'User does not have access to that',
    500: 'API had a problem (500)',
    502: 'API had a problem (502)',
    503: 'API had a problem (503)'
    }




###
# Step 1: login (part 1)
# make sure put in valid credentials
###

url = "https://login.eagleeyenetworks.com/g/aaa/authenticate"

payload = json.dumps({'username': username, 'password': password})
headers = {'content-type': 'application/json', 'authorization': api_key }

response = session.request("POST", url, data=payload, headers=headers)

print ("Step 1: %s" % HTTP_STATUS_CODE[response.status_code])
token = response.json()['token']



###
# Step 2: login (part 2)
###

url = "https://login.eagleeyenetworks.com/g/aaa/authorize"

querystring = {"token": token}

payload = json.dumps({ 'token': token })
headers = {'content-type': 'application/json', 'authorization': api_key }

response = session.request("POST", url, data=payload, headers=headers)

print("Step 2: %s" % HTTP_STATUS_CODE[response.status_code])

current_user = response.json()



###
# Step 3: get list of devices
###

url = "https://login.eagleeyenetworks.com/g/device/list"

payload = ""
headers = {'authorization': api_key }
response = session.request("GET", url, data=payload, headers=headers)

print("Step 3: %s" % HTTP_STATUS_CODE[response.status_code])

device_list = response.json()

# filter everything but the cameras
camera_id_list = [i[1] for i in device_list if i[3] == 'camera']



###
# Step 4: get list of videos for a specific camera (needs camera_id, start_time, end_time)
###

url = "https://login.eagleeyenetworks.com/asset/list/video.flv"

querystring = {"id": camera_id_list[0], "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "options": "coalesce"}

payload = ""
headers = {'authorization': api_key }
response = session.request("GET", url, data=payload, params=querystring, headers=headers)

print("Step 4: %s" % HTTP_STATUS_CODE[response.status_code])

video_list = response.json()



###
# Step 5: Download the video in MP4 format, returns the video if it is able to complete in ~30 seconds.
# Returns JSON with job ID if it can not complete the request in 30 seconds.
###


url = "https://login.eagleeyenetworks.com/asset/play/video.mp4"

querystring = {"id": camera_id_list[0], "start_timestamp": video_list[0]['s'], "end_timestamp": video_list[0]['e']}

payload = ""
headers = { 'authorization': api_key }

response = session.request("GET", url, data=payload, params=querystring, headers=headers)

print("Step 5: %s" % HTTP_STATUS_CODE[response.status_code])

if response.status_code == 200:
    # this is the actual media object, save to a file

    local_filename = "%s-%s.mp4" % (camera_id_list[0], video_list[0]['s'])

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024): 
            if chunk: 
                f.write(chunk)

if response.status_code == 202:
    # this is the job information, wait before requesting again
    print(response.json())



