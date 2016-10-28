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
cloudy = 25
mixed = 50
sunny = 75

# Debug, show output
debug = True

##### End configuration #####


import requests,time,pigpio

# Make sure autoBrightness is enabled
if not int(open('/var/www/html/autoBrightness.txt', 'r').read(1)):
	exit()
	
# Get weather from Yahoo to determine max brightness
url = "https://query.yahooapis.com/v1/public/yql?q=select item.condition, astronomy.sunrise, astronomy.sunset from weather.forecast where woeid=" + woeid + "&format=json"

try:
	data = requests.get(url, timeout=5).json()

	weatherCode = int(data['query']['results']['channel']['item']['condition']['code'])
	weatherText = data['query']['results']['channel']['item']['condition']['text']
	sunrise = data['query']['results']['channel']['astronomy']['sunrise']
	sunset = data['query']['results']['channel']['astronomy']['sunset']
	
except:
	print("Error: Unable to connect to Yahoo! API")
		
	weatherCode = 25
	weatherText = "Mixed"
	sunrise = "7:00 am"
	sunset = "7:00 pm"


# Set max brightness based on weather
if weatherCode < 23 or weatherCode in [26,27,28,41,42,43]: 
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

# Calc sunrise/sunset timeframes. 
# Sunrise/set starts 40 minutes before actual time, and 
# ends 20 minutes after actual time, gradually changing brightness during the hour.

sunriseTime = str(cTime[0]) + '-' + str(cTime[1]) + '-' + str(cTime[2]) + ' ' + sunrise

sunriseStart = int(time.mktime(time.strptime(sunriseTime, "%Y-%m-%d %I:%M %p"))) - 1800
sunriseEnd = sunriseStart + 3600

sunsetTime = str(cTime[0]) + '-' + str(cTime[1]) + '-' + str(cTime[2]) + ' ' + sunset

sunsetStart = int(time.mktime(time.strptime(sunsetTime, "%Y-%m-%d %I:%M %p"))) - 2400
sunsetEnd = sunsetStart + 3600


# Determine the brightness
if now >= sunriseStart and now <= sunriseEnd:
	elapsed = now - sunriseStart
	percent = elapsed / 3600
	brightness = maxBright * percent
	timeOfDay = "Sunrise"
		
elif now > sunriseEnd and now < sunsetStart:
	brightness = maxBright
	timeOfDay = "Day"

elif now >= sunsetStart and now <= sunsetEnd:
	elapsed = sunsetEnd - now
	percent = elapsed / 3600
	brightness = maxBright * percent
	timeOfDay = "Sunset"
	
else:
	brightness = 0
	timeOfDay = "Night"

if debug:
	print(timeOfDay + ", Brightness: " + str(brightness * 2.55))

# Change the brightness quicker if it's brighter as 
# changes seem to be less noticable at higher brightness levels
def getChangeAmt(brightness):
	if currentBrightness > 200:
		return 10
	elif currentBrightness > 100:
		return 5
	elif currentBrightness > 50:
		return 3
	else:
		return 1


# Set the brightness gradually
pi = pigpio.pi()
currentBrightness = pi.get_PWM_dutycycle(pin)
targetBrightness = brightness * 2.55

# Brightness increasing
if targetBrightness > currentBrightness:
	while currentBrightness <= targetBrightness:
		pi.set_PWM_dutycycle(pin, currentBrightness)
		
		amt = getChangeAmt(currentBrightness)
			
		currentBrightness = currentBrightness + amt
		time.sleep(0.05)

# Brightness decreasing
elif targetBrightness < currentBrightness:
	while currentBrightness >= targetBrightness:
		pi.set_PWM_dutycycle(pin, currentBrightness)
		
		amt = getChangeAmt(currentBrightness)
		
		currentBrightness = currentBrightness - amt
		time.sleep(0.05)
		
		
		


