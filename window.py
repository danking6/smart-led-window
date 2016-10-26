#!/usr/bin/env python

import json,urllib,time,pigpio

# GPIO pin to use (change if needed)
pin = 21
pi = pigpio.pi()

# Make sure autoBrightness is enabled
file = open('/var/www/html/autoBrightness.txt', 'r')

if not int(file.read(1)):
	exit()

# Get weather from Yahoo to determine max brightness
url = "https://query.yahooapis.com/v1/public/yql?q=select%20item.condition,astronomy.sunrise,astronomy.sunset%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22syracuse%2C%20ny%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"

response = urllib.urlopen(url)
data = json.loads(response.read())

weatherCode = int(data['query']['results']['channel']['item']['condition']['code'])
weatherText = data['query']['results']['channel']['item']['condition']['text']
sunrise = data['query']['results']['channel']['astronomy']['sunrise']
sunset = data['query']['results']['channel']['astronomy']['sunset']

print "Weather code: " + str(weatherCode) + " (" + weatherText + "), Sunrise: " + sunrise + ", Sunset: " + sunset

# Set max brightness based on weather
if weatherCode < 23 or (weatherCode > 25 and weatherCode < 29):
	maxBright = 35
elif weatherCode >= 32 and weatherCode <= 36:
	maxBright = 75
else:
	maxBright = 50

print "Maxbrightness: " + str(maxBright)

# Current time
cTime = time.localtime()
now = time.time()

# Calc sunrise/sunset timeframes
sunriseTime = str(cTime[0]) + '-' + str(cTime[1]) + '-' + str(cTime[2]) + ' ' + sunrise

sunriseStart = int(time.mktime(time.strptime(sunriseTime, "%Y-%m-%d %I:%M %p"))) - 1800
sunriseEnd = sunriseStart + 3600

sunsetTime = str(cTime[0]) + '-' + str(cTime[1]) + '-' + str(cTime[2]) + ' ' + sunset

sunsetStart = int(time.mktime(time.strptime(sunsetTime, "%Y-%m-%d %I:%M %p"))) - 1800
sunsetEnd = sunsetStart + 3600


# Determine the brightness
if now >= sunriseStart and now <= sunriseEnd:
	elapsed = now - sunriseStart
	percent = elapsed / 3600
	brightness = maxBright * percent
	
	print "Sunrise, Brightness: " + str(brightness * 2.55)
		

elif now > sunriseEnd and now < sunsetStart:
	brightness = maxBright
	print "Day, Brightness:" + str(maxBright * 2.55)

elif now >= sunsetStart and now <= sunsetEnd:
	elapsed = sunsetEnd - now
	percent = elapsed / 3600
	brightness = maxBright * percent
	
	print "Sunset, Brightness: " + str(brightness * 2.55)

else:
	brightness = 0
	print "Night, Brightness: 0"

# Set the brightness gradually
currentBrightness = pi.get_PWM_dutycycle(pin)
targetBrightness = brightness * 2.55

if targetBrightness > currentBrightness:
	while currentBrightness <= targetBrightness:
		pi.set_PWM_dutycycle(pin, currentBrightness)
		currentBrightness = currentBrightness + 2
		time.sleep(0.05)

elif targetBrightness < currentBrightness:
	while currentBrightness >= targetBrightness:
		pi.set_PWM_dutycycle(pin, currentBrightness)
        currentBrightness = currentBrightness - 2
		time.sleep(0.05)

