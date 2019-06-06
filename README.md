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

*make sure to edit the last line of `Dockerfile` to run the correct <file>*


## Files


| File | Description |
| :---  | :--- |
| MP4\_video_download.py | Shows how to login, get list of cameras, pull video clip from first camera |
| Webhook\_video\_download.py | Same as above but uses prefect API to get webhooks when video is in the cloud |
| List\_bridges\_in\_sub\_accounts.py | Prints out the bridge information for all bridges in all sub-accounts |
| Reseller\_Camera\_Monitor.py | Subscribes to status changes for every device in every sub-account |
| Listen\_for\_thumbnails.py | Listen for thumbnail events using websockets to our poll stream |
| Listen\_for\_roi\_motion.py | Same as above but listening for ROI events |
