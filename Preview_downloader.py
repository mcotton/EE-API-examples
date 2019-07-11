import requests
import json
import sys


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
    print("Please put in your credentials")
    sys.exit()



camera = ""


# which folder should these prveviews download into?
# using the folder name as a label for the images

label = "open"


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
# Step 3: get the one selected camrea
###

camera_id_list = [camera]



###
# Step 4: get list of preview for a specific camera (needs camera_id, start_time, end_time)
###

url = "https://login.eagleeyenetworks.com/asset/list/image"

querystring = {"id": camera_id_list[0], "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "asset_class": "all"}

payload = ""
headers = {'authorization': api_key }
response = session.request("GET", url, data=payload, params=querystring, headers=headers)

print("Step 4: %s" % HTTP_STATUS_CODE[response.status_code])

preview_list = response.json()



###
# Step 5: Download the video in MP4 format, returns the video if it is able to complete in ~30 seconds.
# Returns JSON with job ID if it can not complete the request in 30 seconds.
###




for item in preview_list:

    url = "https://login.eagleeyenetworks.com/asset/asset/image.jpeg"

    querystring = {"id": camera_id_list[0], "timestamp": item['s'], "asset_class": "all" }

    payload = ""
    headers = { 'authorization': api_key }

    response = session.request("GET", url, data=payload, params=querystring, headers=headers)

    print("Step 5: %s" % HTTP_STATUS_CODE[response.status_code])

    if response.status_code == 200:
        # this is the actual media object, save to a file

        local_filename = "%s/%s-%s.jpg" % (label, camera_id_list[0], item['s'])

        print(f"Saving {local_filename}")

        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024): 
                if chunk: 
                    f.write(chunk)

    if response.status_code == 400:
        # this is the job information, wait before requesting again
        print(url)
        print(querystring)
        print(response.json())



