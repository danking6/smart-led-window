#!/usr/bin/env python3

# ------------------------------------------------------------
# File:   window.py
# Author: Dan King
#
# This script needs pigpiod to be running (http://abyz.co.uk/rpi/pigpio/)
# ------------------------------------------------------------


##### Configuration #####

# GPIO pin number
pin = 21

# Yahoo! woeid (location ID)
woeid = "12762731"

# Brightness levels (percent)
cloudy = 20
mixed = 40
sunny = 75

# Config file, persistent configs
confFile = '/var/www/html/window.conf'

# Debug, show output
debug = True

##### End configuration #####


import requests,time,pigpio,json

# Load config file for cache/settings
f = open(confFile, 'r')
settings = json.loads(f.read())
f.close()

if not int(settings['auto']):
	if debug:
		print('Auto brightness disabled, exiting...')
	exit()
	
# Get weather from Yahoo to determine max brightness
url = "https://query.yahooapis.com/v1/public/yql?q=select item.condition, astronomy.sunrise, astronomy.sunset from weather.forecast where woeid=" + woeid + "&format=json"

try:
	data = requests.get(url, timeout=10).json()

	weatherCode = int(data['query']['results']['channel']['item']['condition']['code'])
	weatherText = data['query']['results']['channel']['item']['condition']['text']
	sunrise = data['query']['results']['channel']['astronomy']['sunrise']
	sunset = data['query']['results']['channel']['astronomy']['sunset']
	
	# Save/cache values
	settings['auto'] = 1
	settings['weather'] = weatherCode
	settings['sunrise'] = sunrise
	settings['sunset'] = sunset
	
	f = open(confFile, 'w')
	f.write(json.dumps(settings))
	f.close()
	
except:
	print("Error: Unable to connect to Yahoo! API")
	
	# Use settings from cache
	weatherCode = settings['weather']
	weatherText = ""
	sunrise = settings['sunrise']
	sunset = settings['sunset']


# Set max brightness based on weather
if weatherCode < 23 or weatherCode in [26,41,42,43]: 
	maxBright = cloudy
elif weatherCode >= 32 and weatherCode <= 36:
	maxBright = sunny
else:
	maxBright = mixed

if debug:
	print("Weather code: " + str(weatherCode) + " (" + weatherText + "), Sunrise: " + sunrise + ", Sunset: " + sunset)
	print("Max brightness: " + str(maxBright))

# Current time
cTime = time.localtime()
now = time.time()


# Sunrise: start brightening 15 mins before, end 75 mins after
sunriseTime = str(cTime[0]) + '-' + str(cTime[1]) + '-' + str(cTime[2]) + ' ' + sunrise
sunriseStart = int(time.mktime(time.strptime(sunriseTime, "%Y-%m-%d %I:%M %p"))) - 900
sunriseEnd = sunriseStart + 5400

# Sunset: start dimming 75 mins before, end 15 mins after
sunsetTime = str(cTime[0]) + '-' + str(cTime[1]) + '-' + str(cTime[2]) + ' ' + sunset
sunsetStart = int(time.mktime(time.strptime(sunsetTime, "%Y-%m-%d %I:%M %p"))) - 4500
sunsetEnd = sunsetStart + 5400


# Determine the current brightness
if now >= sunriseStart and now <= sunriseEnd:
	elapsed = now - sunriseStart
	percent = elapsed / 5400
	brightness = maxBright * percent
	timeOfDay = "Sunrise"
		
elif now > sunriseEnd and now < sunsetStart:
	brightness = maxBright
	timeOfDay = "Day"

elif now >= sunsetStart and now <= sunsetEnd:
	elapsed = sunsetEnd - now
	percent = elapsed / 5400
	brightness = maxBright * percent
	timeOfDay = "Sunset"
	
else:
	brightness = 0
	timeOfDay = "Night"

if debug:
	print(timeOfDay + ", Brightness: " + str(brightness * 2.55))

# Change the brightness quicker at the beginning of the
# transition, then slowing near the end
def getChangeAmt(current, target):
	return round(abs(current-target) / 10) + 1
	
	
# Set the brightness gradually
pi = pigpio.pi()
currentBrightness = pi.get_PWM_dutycycle(pin)
targetBrightness = brightness * 2.55

# Brightness increasing
if targetBrightness > currentBrightness:
	while currentBrightness <= targetBrightness:
		pi.set_PWM_dutycycle(pin, currentBrightness)
		
		amt = getChangeAmt(currentBrightness, targetBrightness)
			
		currentBrightness = currentBrightness + amt
		time.sleep(0.05)

# Brightness decreasing
elif targetBrightness < currentBrightness:
	while currentBrightness >= targetBrightness:
		pi.set_PWM_dutycycle(pin, currentBrightness)
		
		amt = getChangeAmt(currentBrightness, targetBrightness)
		
		currentBrightness = currentBrightness - amt
		time.sleep(0.05)
