import json
import pprint
import sys

import gcsa.google_calendar
from dateutil import parser
from beautiful_date import Sept, days
from gcsa.event import Event


with open("hyperparameters.json", "r") as file:
    hyperparameters = json.load(file)


def init_gc():
    global gc
    gc = gcsa.google_calendar.GoogleCalendar(credentials_path=hyperparameters["path_to_OAuth_credentials"],
                                             token_path=None)
    return gc

init_gc()

start = 1/Sept/2023
end = start + 7 * days
event = Event('Vacation',
              start=start,
              end=end)

