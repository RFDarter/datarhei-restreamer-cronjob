# Datarhei Restreamer Cronjob

With this simple python script you will be able to set times when a stream should be started or stopped.

## Installation
```git clone https://github.com/RFDarter/datarhei-restreamer-cronjob.git```


## Setup

Modify the config.json

`url": "http://<url-to-your-restreamer>:8080/api"`
set the correct url to your restreamer server

`"username": "admin"`
admin is the default username

`"password": "datarhei"`
datarhei is the default passwort

## Specify jobs

Under `commands` you can add a list of jobs the script will run at the specifed time.
You can `start` or `stop` a stream

```json
  "commands": [
    {
      "action": "stop",
      "time": "00:41:00",
      "stream_id": "restreamer-ui:egress:youtube:7f2d09cf-ac79-4660-8d73-74ec65d12d9e"
    },
    {
      "action": "start",
      "time": "00:41:30",
      "stream_id": "restreamer-ui:egress:youtube:7f2d09cf-ac79-4660-8d73-74ec65d12d9e"
    },
    {
      "action": "stop",
      "time": "00:42:00",
      "stream_id": "restreamer-ui:egress:youtube:7f2d09cf-ac79-4660-8d73-74ec65d12d9e"
    },
    {
      "action": "start",
      "time": "00:42:15",
      "stream_id": "restreamer-ui:egress:youtube:7f2d09cf-ac79-4660-8d73-74ec65d12d9e"
    }
  ]
```

if you run 
```py restreamer-cronjob.py -list_streams```
you will get a list of streams that are set up in your restreamer


## Run it

Simply run
```py restreamer-cronjob.py```
to run the script