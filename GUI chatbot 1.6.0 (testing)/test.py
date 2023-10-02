import datetime
import json
import pprint
import sys
import time
import tkinter.messagebox

import gcsa.google_calendar
from dateutil import parser
from beautiful_date import Sept, days
from gcsa.event import Event

import functools


print(datetime.datetime.now())