import time
import requests
import json
import urllib.parse
import logging
import argparse
from datetime import datetime

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_URL = "url"

CONF_COMMANDS = "commands"
CONF_TIME = "time"
CONF_ACTION = "action"
CONF_STREAM_ID = "stream_id"

ACTION_START = "start"
ACTION_STOP = "stop"

list_commands = []

with open("config.json", "r") as f:
    config = json.load(f)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()

file_handler = logging.FileHandler("restreamer-cronjob.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)


parser = argparse.ArgumentParser(description="Restreamer start/stop a stream")

parser.add_argument(
    "-list_streams",
    action="store_true",
    help="List all available streams on restreamer",
    required=False,
)


def login_to_api() -> str:
    login_data = {"username": config[CONF_USERNAME], "password": config[CONF_PASSWORD]}
    response = requests.post(f"{config[CONF_URL]}/login", json=login_data)

    if response.status_code == 200:
        logger.info("Login to api successfull")
        return response.json().get("access_token")
    else:
        logger.error(
            f"Error while login into restreamer api: {response.status_code}, {response.text}"
        )
        return None


def command_stream_api(stream_id, action):
    token = login_to_api()
    if token is None:
        return

    post_data = {"command": f"{action}"}
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    encoded_stream_id = urllib.parse.quote(stream_id)
    response = requests.put(
        f"{config[CONF_URL]}/v3/process/{encoded_stream_id}/command",
        headers=headers,
        json=post_data,
    )
    if response.status_code == 200:
        logger.info(f"Successfully executed action `{action}` on stream: {stream_id}")
    else:
        logger.error(
            f"Error while issuing start/stop command: {response.status_code}, {response.text}"
        )


def list_all_streams():
    token = login_to_api()
    if token is None:
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{config[CONF_URL]}/v3/process", headers=headers)

    if response.status_code == 200:
        streams = response.json()
        logger.info("Avaliable Streams:")
        for stream in streams:
            logger.info(f"Stream ID: {stream['id']}")
    else:
        logger.error(
            f"Error while getting streams: {response.status_code}, {response.text}"
        )


def check_config() -> bool:
    ret = True
    if CONF_USERNAME not in config:
        logger.error("No username is set")
        ret = False
    if CONF_PASSWORD not in config:
        logger.error("No password is set")
        ret = False
    if CONF_URL not in config:
        logger.error("No urls is set")
        ret = False

    if "commands" not in config:
        logger.warning("No Commands set - nothing to do")
        return False

    for command in config[CONF_COMMANDS]:
        all_fields = True
        if CONF_TIME not in command:
            logger.warning(f"Command does not include {CONF_TIME}, command is skipped")
            all_fields = False
        if CONF_ACTION not in command:
            logger.warning(
                f"Command does not include {CONF_ACTION}, command is skipped"
            )
            all_fields = False
        if CONF_STREAM_ID not in command:
            logger.warning(
                f"Command does not include {CONF_STREAM_ID}, command is skipped"
            )
            all_fields = False

        if command[CONF_ACTION] not in [ACTION_START, ACTION_STOP]:
            logger.warning(
                f"Action can only be {ACTION_START} or {ACTION_STOP} - action is: {command[CONF_ACTION]}"
            )
            all_fields = False

        if all_fields:
            # check if time is valide and parse it to seconds since midnight
            try:
                time = datetime.strptime(command[CONF_TIME], "%H:%M")
                command[CONF_TIME] = time.hour * 3600 + time.minute * 60
            except ValueError:
                try:
                    time = datetime.strptime(command[CONF_TIME], "%H:%M:%S")
                    command[CONF_TIME] = (
                        time.hour * 3600 + time.minute * 60 + time.second
                    )
                except ValueError:
                    logger.error(
                        f"{command[CONF_TIME]} is not a valid time format. Format should be `HH:MM` of `HH:MM:SS`"
                    )
                    return False
            logger.info(f"adding command to list: {command}")
            list_commands.append(command)

    return ret


def main():
    args = parser.parse_args()
    if args.list_streams:
        list_all_streams()
        return

    if not check_config():
        logger.error("config failed")
        return

    if login_to_api() is None:
        logger.error("Login failed are the cedentials correct?")
        return

    while True:
        # current_time = datetime.now().strftime("%H:%M")
        now = datetime.now()

        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        print(seconds_since_midnight)
        for command in list_commands:
            if seconds_since_midnight == command[CONF_TIME]:
                logger.info(
                    f"trying to issue action `{command[CONF_ACTION]}` on stream_id: {command[CONF_STREAM_ID]}"
                )
                command_stream_api(command[CONF_STREAM_ID], command[CONF_ACTION])
        time.sleep(1)


if __name__ == "__main__":
    main()
