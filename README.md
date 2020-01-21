# Eagle Eye Networks API Examples

## Introduction
This repo is for helping our Technology Partners understand how to use our API.  For more information please see our [API Documentation](https://apidocs.eagleeyenetworks.com/apidocs).


## Installation
You can install it locally by running
 `pip install -r requirements.txt`
 
 `python <file>`

Or you can run this inside of Docker

`docker build --tag=apiexamples .`

`docker run -it apiexamples`

*make sure to edit the last line of `Dockerfile` to run the correct file*

The examples are now looking for local settings in a file named `local_settings.py`

It should contain the following:

```
# Enter your credentials
username = ""
password = ""
api_key = ""
```

## Files


| File | Description |
| :---  | :--- |
| MP4\_video_download.py | Shows how to login, get list of cameras, pull video clip from first camera |
| Webhook\_video\_download.py | Same as above but uses prefect API to get webhooks when video is in the cloud |
| List\_bridges\_in\_sub\_accounts.py | Prints out the bridge information for all bridges in all sub-accounts |
| List\_bridges\_and\_cameras\_in\_sub\_accounts.py | Prints out number of attached bridges and cameras in all sub-accounts |
| Listen\_for\_previews.py | Listen for preview image events using websockets to our poll stream |
| Listen\_for\_thumbnails.py | Listen for thumbnail events using websockets to our poll stream |
| Listen\_for\_roi\_motion.py | Same as above but listening for ROI events |
| Listen\_for\_status\_changes.py | Subscribes to status changes for an account, simplified version |
| Preview_downloads.py | Downloads all preview images between time range |
| Output\_live\_stream\_URLs.py | format command to play live stream in VLC |
| testing_poll_events.py | Listens for camera connect/disconnet events |
