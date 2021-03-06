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





def bootstrap():
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


    def on_message(ws, data):
        print("received a new message: ", data)
            
    def on_error(ws, error):
        print("### on_error handler ###")
        print(error)    
    
    def on_close(ws):
        print("### on_close handler ###")
        bootstrap()
    
    def on_open(ws):
        # Now that we have connected we need to send a JSON structure to tell the API what devices
        # and events we are listening for (https://apidocs.eagleeyenetworks.com/#websocket-polling)
        register_msg = { "cameras": {} }
        for d in camera_id_list:
            register_msg['cameras'][d] = { 'resource': ['event'], 'event': ['ROMS', 'ROMU', 'ROME'] }
            data = json.dumps(register_msg)
        print("Registering for status events")
        ws.send(data)


    auth_key = session.cookies.get_dict()['auth_key']
    account_id = current_user['owner_account_id']


    # Open websocket and attach callback handlers
    ws = websocket.WebSocketApp('wss://login.eagleeyenetworks.com/api/v2/Device/{}/Events'.format(account_id), cookie='auth_key={}'.format(auth_key),
                                  on_message = on_message,
                                  on_error = on_error,
                                  on_close = on_close,
                                  )

    
    # Open the websocket and run forever
    ws.on_open = on_open
    ws.run_forever()


if __name__ == '__main__':
    bootstrap()
