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
    
    # look to see if there are credentials in local_settings.py
    import local_settings

    username = local_settings.username
    password = local_settings.password
    api_key = local_settings.api_key

    if username == "" or password == "" or api_key == "":
        print("Please put in your credentials")
        sys.exit()



# Translating the HTTP response codes to make the status messages easier to read
HTTP_STATUS_CODE = { 
    200: 'OK', 
    202: 'ACCEPTED',
    400: 'Bad Request, please check what you are sending',
    401: 'User needs to Login first', 
    403: 'User does not have access to that',
    408: "Request Timeout",
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
camera_id_list = [i[1] for i in device_list if (i[3] == 'camera' and i[0] != None)]


###
# Step 4: subscribe to  pollstream
# listening for  events
###


url = "https://login.eagleeyenetworks.com/poll"

payload = ""
headers = {'authorization': api_key }


register_msg = { "cameras": {} }
for d in camera_id_list:
    register_msg['cameras'][d] = { "resource": ["pre"] }

payload = json.dumps(register_msg)

response = session.request("POST", url, data=payload, headers=headers)

print("Step 4: %s" % HTTP_STATUS_CODE[response.status_code])

print(response.json())



###
# Step 5: immediately open a new request to see if the server has a new event
# keep making requests until the session expires
###


while True:

    url = "https://login.eagleeyenetworks.com/poll"

    payload = ""
    headers = {'authorization': api_key }

    try:
        response = session.request("GET", url, data=payload, headers=headers)
    
        print("Step 5: %s" % HTTP_STATUS_CODE[response.status_code])

        if response.json:
            print(response.json())

    except requests.exceptions.ConnectionError:
        # upstream issues can cause the connection to be interrupted, just make another request
        pass

    



