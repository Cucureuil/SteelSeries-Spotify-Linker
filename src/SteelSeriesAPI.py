from json import loads, dumps
from time import sleep
from os import environ, path
import logging
import requests

GAME = "SPOTIFY_LINKER"
GAME_DISPLAY_NAME = "SteelSeries Spotify Linker"
AUTHOR = "Firewe"
EVENT = "UPDATE"


class SteelSeriesAPI:
    LOGGING_PREFIX = "[SteelSeriesAPI]"

    def __init__(self):
        self.path = path.join(environ.get('PROGRAMDATA'), 'SteelSeries', 'SteelSeries Engine 3', 'coreProps.json')
        self.address = ""
        self.retrieve_address()

    def retrieve_address(self):
        fetched = False
        while not fetched:
            try:
                with open(self.path, "r") as f:
                    self.address = "http://" + loads(f.readline())["address"]
                    self.register_game()
                    self.bind_game_event()
                    logging.info(self.LOGGING_PREFIX + " Found local address API : " + self.address)
                    return self.address
            except ConnectionError:
                logging.error(
                    self.LOGGING_PREFIX + " Could not connect to API, is steelseries engine running? Retry in 5s...")
            except OSError:
                logging.error(
                    self.LOGGING_PREFIX + "Could not register application, is steelseries engine running? Retry in "
                                          "5s...")

            fetched = False
            sleep(5)

    def bind_game_event(self):
        self.send_data("/bind_game_event", {
            "game": GAME,
            "event": EVENT,
            "value_optional": True,
            "handlers": [
                {
                    "device-type": "screened-128x48",
                    "zone": "one",
                    "mode": "screen",
                    "datas": [
                      {
                        "has-text": False,
                        "image-data": [5 for _ in range(768)]
                      }
                    ]
                }
            ]
        })

        logging.info(self.LOGGING_PREFIX + " Binding game event")

    def send_frame(self, image):
        self.send_data("/game_event", {
            "game": GAME,
            "event": EVENT,
            "data": {
                "frame": {
                    "image-data": image
                }
            }
        })

    def register_game(self):
        self.send_data("/game_metadata", {
            "game": GAME,
            "game_display_name": GAME_DISPLAY_NAME,
            "developer": AUTHOR,
            "deinitialize_timer_length_ms": 2000
        })

    def send_data(self, endpoint, data):
        requests.post(
            self.address + endpoint,
            data=dumps(data),
            headers={'Connection': 'close', 'Content-Type': 'application/json'}
        )
