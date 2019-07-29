import websocket
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



#Constants for device list call array
DEVICE_ID_INDEX = 1
DEVICE_NAME_INDEX = 2
DEVICE_STATUS_INDEX = 10

#Bitmask recording
STATUS_BITMASK_ONLINE           = 0x100000
STATUS_BITMASK_ON               = 0x020000
STATUS_BITMASK_CAMERA_STREAMING = 0x040000
STATUS_BITMASK_VIDEO_RECORDING  = 0x080000

CLI_STATUS_STRING = "[{}] - Status Hex: {} - Status Clean: {}"

#This function parses out the status in decimal format to a dictionary
#The dictionary has the keys (https://apidocs.eagleeyenetworks.com/#status-bitmask):
# - device_internet_online: Determines if the device is registered online to the cloud
# - camera_on: Determines if the camera is on
# - camera_streaming: Determines the bridge is actively streaming from the camera
# - camera_recording: Determines that the camera is actively recording
def parseStatusDecimal(status):
    ret = { 'device_internet_online': False,
            'camera_on': False,
            'camera_streaming': False,
            'camera_recording': False, }

    #Use bitmasking specified in https://apidocs.eagleeyenetworks.com/#status-bitmask
    #We use the bitmask operations to get the status from the integer. Each bit location
    #specifices a status for the camera.  For example, STATUS_BITMASK_ONLINE is equal to
    #0x100000 in hex which is b100000000000000000000 in binary. If the 21rst bit is enabled
    #in the status integer then that means the camera is online. You can get just that bit
    #through bit masking operations. In this case we do a bitmask AND operation to get each
    #status.
    ret['device_internet_online'] = bool(status & STATUS_BITMASK_ONLINE)
    ret['camera_on'] = bool(status & STATUS_BITMASK_ON)
    ret['camera_streaming'] = bool(status & STATUS_BITMASK_CAMERA_STREAMING)
    ret['camera_recording'] = bool(status & STATUS_BITMASK_VIDEO_RECORDING)

    return ret


#This function takes in a hexidecimal string and parses out the status
def parseStatusHex(status):
    #Convert the status hex string to decimal base 10 integer
    decimal_status = int(status, 16)
    return parseStatusDecimal(decimal_status)



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
# Step 4: subscribe to websocket pollstream
# listening for thumbnail events
###


#Websockets are based on push events from the server. Establishing a websocket poll
#connection to the Eagle Eye API will give you event updates as they happen in real
#time. We will listen to event status changes for 10 seconds before exiting the 
#application.

#To connect to the API we need to know the account ID. We can get that information
#from the user object returned after a successful login in Step 2



auth_key = session.cookies.get_dict()['auth_key']
account_id = current_user['owner_account_id']

#We create the websocket connection. Make sure we put in the auth_key in the HTTP
#Cookie attribute instead of passing it as a query parameter (A= in previous calls.
ws = websocket.WebSocket()
ws.connect('wss://login.eagleeyenetworks.com/api/v2/Device/{}/Events'.format(account_id), cookie='auth_key={}'.format(auth_key))

#Now that we have connected we need to send a JSON structure to tell the API what devices
#and events we are listening for (https://apidocs.eagleeyenetworks.com/#websocket-polling)
register_msg = { "cameras": {} }
for d in camera_id_list:
    register_msg['cameras'][d] = { 'resource': ['status'] }
    data = json.dumps(register_msg)

#Send the register event data structure to the API
print("Registering for status events {}".format(data))
ws.send(data)


#Now we continue to recieve information as the API will push
#any new status changes for the cameras we have registered to
#observe status change events.
while True:
    data = ws.recv()
    jdata = json.loads(data) #convert the json string to a python dictionary/array
    for device_id, device_data in jdata['data'].items():
        ret = parseStatusDecimal(device_data['status'])
        print(CLI_STATUS_STRING.format(device_id, hex(device_data['status']), ret))

ws.close()


