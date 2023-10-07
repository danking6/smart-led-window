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

# Latitude/longitude for location
lat = 00.00
lon = -00.00

# Maximum brightness level
maxBright = 65

# Config file, persistent configs
confFile = '/var/www/html/window.conf'

# Debug, show output
debug = True

##### End configuration #####


import requests,time,pigpio,json,datetime,os
from suntime import Sun, SunTimeException

# Load config file for cache/settings
f = open(confFile, 'r')
settings = json.loads(f.read())
f.close()

if not int(settings['auto']):
	if debug:
		print('Auto brightness disabled, exiting...')
	exit()
	

# Current time
cTime = time.localtime()
now = time.time()


sun = Sun(lat, lon)

# Get today's sunrise and sunset 
sunrise = sun.get_sunrise_time().timestamp()
sunset = sun.get_sunset_time().timestamp()

# Sunrise: start brightening 20 mins before, end 70 mins after
sunriseStart = sunrise - 1200
sunriseEnd = sunriseStart + 5400

# Sunset: start dimming 75 mins before, end 15 mins after
sunsetStart = sunset - 4500
sunsetEnd = sunsetStart + 5400

if debug:
	print("sunriseStart: " + str(sunriseStart) + "\nsunriseEnd:    " + str(sunriseEnd))
	print("\nsunsetStart: " + str(sunsetStart) + "\nsunsetEnd: " + str(sunsetEnd) + "\nnow:          " + str(now))

#exit()

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
try:
	currentBrightness = pi.get_PWM_dutycycle(pin)
except:
	os.system("/usr/bin/pigs p 21 255")
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
