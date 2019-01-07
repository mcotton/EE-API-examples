
import threading
import websocket # pip install websocket-client
import requests
import getpass
import logging
import pickle
import json
import time
import os

logging.basicConfig()

STATUS_MESSAGE = {
        0: "OFF",# user off
        1: "OFL",# Offline
        2: "OFF",# user off
        3: "SNR",#streaming not recording
        4: "OFF",# user off
        5: "N/A",
        6: "OFF",# user off
        7: "N/A",
        8: "OFF",# user off
        9: "OFL",# Offline
        10:"OFF",# user off
        11:"ON",# all good
        12:"OFF",# user off
        13:"SNR",#streaming not recording
        14:"OFF",# user off
        15:"REC"# recording all good
        }

COOKIEPATH = ".cookies"
cookies = None
if os.path.exists(COOKIEPATH):
    with open(COOKIEPATH, 'r') as fp:
        cookies = requests.utils.cookiejar_from_dict(pickle.load(fp))

def connect(user, password):
    """ Connect to EagleEye Session """
    session = requests.Session()
    if cookies:
        session.cookies = cookies
    session.auth = (user, password)
    authen_url = "https://login.eagleeyenetworks.com/g/aaa/authenticate"

    resp = session.post(authen_url, json={'username':user,
                                          'password':password})

    if resp.status_code == 200:
        token = resp.json()['token']
        authorize_url = 'https://login.eagleeyenetworks.com/g/aaa/authorize'
        resp = session.post(authorize_url, json={'token':token})
        return session
    return resp.raise_for_status()

def get_user(session):
    resp = session.get("https://login.eagleeyenetworks.com/g/user")
    if resp.status_code == 200:
        return resp.json()
    return resp.raise_for_status()

def get_account_list(session):
    resp = session.get("https://login.eagleeyenetworks.com/g/account/list")
    if resp.status_code == 200:
        return resp.json()
    return resp.raise_for_status()

def get_device_list(session):
    resp = session.get("https://login.eagleeyenetworks.com/g/device/list")
    if resp.status_code == 200:
        return resp.json()
    return resp.raise_for_status()

def switch_account(session, account_id):
    resp = session.post("https://login.eagleeyenetworks.com/g/aaa/switch_account",
                        json={'account_id':account_id})
    if resp.status_code == 200:
        return resp.json()
    return resp.raise_for_status()


def subscribe_notifications(session, account_id="", devices={}, callback=None, name=None):
    """
        Devices should be camera id: {resources, event}
        see https://apidocs.eagleeyenetworks.com/#initialize-poll

        Callback should accept two variables:
            first the websocket
            second the message
    """
    if name == None:
        import string, random
        name = "".join([random.choice(string.ascii_letters) for ii in xrange(10)])
    uri_format = "wss://login.eagleeyenetworks.com/api/v2/Device/{}/Events"
    subscribe = {"cameras": devices}
    cc = "; ".join(["{}={}".format(kk, vv) for kk, vv in session.cookies.iteritems()])
    def hold_socket():
        print("Opening {}".format(name))
        ws.on_open = on_open
        ws.run_forever()

    def on_mess(ws, message):
        print("MSG {}: {}".format(name, message))

    def on_open(ws):
        ws.send("{}".format(json.dumps(subscribe)))
        print("Subscribed to {}".format(subscribe))

    def on_close(ws):
        print("Closed Subscription {}".format(name))


    def on_err(ws, error):
        print("ERR {} Subscription: {}".format(name, error))

    if callback:
        ws = websocket.WebSocketApp(uri_format.format(account_id),
                                    on_message=callback,
                                    on_error=on_err,
                                    on_close=on_close,
                                    cookie=cc)
    else:
        ws = websocket.WebSocketApp(uri_format.format(account_id),
                                    on_message=on_mess,
                                    on_error=on_err,
                                    on_close=on_close,
                                    cookie=cc)

    tt = threading.Thread(target=hold_socket)
    tt.setDaemon(True)
    tt.start()


if __name__ == "__main__":

    username = input("Username: ")
    password = getpass.getpass("Password: ")

    sess = connect(username, password)
    user = get_user(sess)
    dom = user['active_brand_subdomain']
    account = user['active_account_id']
    print(account)
    sub_accounts = [each[0] for each in get_account_list(sess) if each[0] != account]
    print(sub_accounts)

    accounts_and_devices = {}
    global_devs = {'r':0}
    for acc in sub_accounts:

        print("creating connection for {}".format(acc))
        accounts_and_devices[acc] = {'cameras': []}
        accounts_and_devices[acc]['connection'] = connect(username, password)
        switch_account(accounts_and_devices[acc]['connection'], acc)
        devices = get_device_list(accounts_and_devices[acc]['connection'])
        for dev in devices:
            if dev[3] == "camera":
                if dev[5] == "ATTD":
                    print("found {}".format(dev[1], dev[5]))
                    accounts_and_devices[acc]['cameras'].append(dev[1])
                    global_devs[dev[1]] = {'c':0, 's':"F", 'e':0}

        subscribe_cams = {}
        for cam in accounts_and_devices[acc]['cameras']:
            subscribe_cams[cam] = {"resource":["status"]}
        if subscribe_cams:
            def message_call(ws, message):
                global global_devs
                message = json.loads(message)
                devices = message['data'].keys()
                for dev in devices:
                    data = global_devs[dev]
                    stat = message['data'][dev].get("status", None)
                    if stat:
                        stat = message['data'][dev]['status']
                        on_status = STATUS_MESSAGE[((0x1E0000 & stat) >> 17)]
                        data['c'] += 1
                        data['s'] = on_status
                    else:
                        data['e'] += 1
                        err = message['data'][dev].get("error", None)
                        print("Err for dev {}: {}".format(dev, message))
                    global_devs[dev] = data
                    global_devs['r'] += 1

            subscribe_notifications(accounts_and_devices[acc]['connection'], acc, subscribe_cams, message_call, name=acc)

    while (True):
        print(global_devs)
        time.sleep(1)

