import logging
logging.getLogger('').setLevel(logging.DEBUG)
import os

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    logging.error('Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using "sudo" to run your script')

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

import urllib
import urllib2

import calendar
from datetime import datetime
import calendar
_EPOCH_BASE = calendar.timegm(datetime(1970, 1, 1).timetuple())

LED_MATRIX_ROWS = 16
LED_MATRIX_COLS = 32
GPIO.setmode(GPIO.BCM)

POT_MIN = 0    # Set this to the observed potentiometer minimum
POT_MAX = 1024 # Set this to the observed potentiometer maximum
_POT_RANGE = (POT_MAX+1) - POT_MIN

SPEECH_TMP_FILE='/tmp/speech.wav'
PICO_CMD='pico2wave -l en-US --wave "%s" "%s";aplay "%s"'
_BASE_URL = 'ziggy-214721.appspot.com/settarget'

def getDateAsUTCTimestamp(naive_datetime):
  " Convert datetime to the unix timestamp, UTC seconds since the epoch. "
  timestamp_utc = calendar.timegm(naive_datetime.timetuple())
  unix_ts = (timestamp_utc - _EPOCH_BASE)
  return unix_ts

def sendTargetDateToCloud(target_datetime, base_url):
  timestamp = getDateAsUTCTimestamp(target_datetime)
  query_params = urllib.urlencode({'datetime':'{}'.format(timestamp)})
  query = 'https://{}?{}'.format(base_url, query_params)
  logging.debug("sending {}".format(query))
  request = urllib2.urlopen(query)
  response = request.read()
  logging.debug("response received: {}".format(response))

def connectToCloudService():
  " Returns reference to timestore cloud service. "
  return _BASE_URL

def getDateUpButton():
  " Returns True if up button is pressed "
  return False

def getDateDownButton():
  " Returns True if down button is pressed "
  return False 

def getPotentiometerValue():
  return 127

def getTimeOfDay():
  " Return time of day potentiometer, scaled and truncated to 0:23. "
  raw = getPotentiometerValue()
  tod = ((raw - POT_MIN)*1.0 / _POT_RANGE) + POT_MIN
  return int(tod)

def scrollDate(target, days_delta):
  """
  Args
    target base date
    days_delta number of days to increment target date.
  Returns adjusted date
  """
  d = target + datetime.timedelta(days=days_delta)
  return d

def displayDate(target_date):
  " Display the date and time. "
  print(target_date.strftime('%b, %d %Y\n'))
  print(target_date.strftime('%H:%M'))

def speakDate(target_date):
  " Speak the date and time, be well spoken. " 
  dow = calendar.day_name[target_date.weekday()]
  month = target_date.strftime('%B')
  day = target_date.strftime('%d')
  if day[-1:] == '1':
    suffix = 'st'
  if day[-1:] == '2':
    suffix = 'nd'
  if day[-1:] == '3':
    suffix = 'rd'
    suffix = 'th'
  hour = target_date.hour
  daypart = 'A M '
  if hour == 0:
    hour = 12
  elif hour > 12:
    hour -= 12
    daypart = 'P M '
  spoken_datetime = '{} {} on {}, the {}{} of {}'.format(hour, daypart, dow, day, suffix, month)
  try:
    os.system(PICO_CMD % (SPEECH_TMP_FILE, spoken_datetime, SPEECH_TMP_FILE))
  except Exception, e:
    logging.exception('Error speaking')

def main():
  datetime_service = connectToCloudService()
  target_date = datetime.now()
  previous_target_date = datetime.now()

  while True:
    if getDateDownButton():
      target_date = scrollDate(target_date, -1)   
    elif getDateUpButton():
      target_date = scrollDate(target_date, 1)   
    target_hour = getTimeOfDay()
    target_date.replace(hour=target_hour, minute=0)
    if target_date != previous_target_date:
      displayDate(target_date)
      speakDate(target_date)
      sendTargetDateToCloud(target_date, datetime_service)
      previous_target_date = target_date

main()
