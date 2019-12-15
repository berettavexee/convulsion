#!/usr/bin/python3
#
# A small script to scrap convulsions-sonore agenda
#
# Todo: 
#	city date and hour in the json filename
#	generate an ICS

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import  URLError
import re
import json
import datetime, time
import os.path
import pandas as pd

city = "Paris"
outputfilename = "output.json"
Reflesh_interval = 6 * 3600 #Dump refresh interval in second 

def getpage():
	req = Request('http://www.convulsions-sonores.info/5.html')
	try:
		response = urlopen(req)
	except URLError as e:
		if hasattr(e, 'reason'):
			print('We failed to reach a server.')
			print('Reason: ', e.reason)
		elif hasattr(e, 'code'):
			print('The server couldn\'t fulfill the request.')
			print('Error code: ', e.code)
		exit()
	else:
		print('Page successfully downloaded')
	return response

def parsing(response):
	# Parse the page and extract event row 
	soup = BeautifulSoup(response, 'html.parser')
	table = soup.select("#content_container")
	rows = table[0].find_all('p')
	print('Events detected:', len(rows))
	# filter
	# Regex Paris Zip code 
	pattern = re.compile("(75|92|93|94)\d{3}")
	city_table = []
	for row in rows:
		row = row.get_text().replace('\n','')
		if pattern.search(row) is not None:
			city_table.append(row)
	print('Events for', city, len(city_table))
	#
	# split the string with some regex
	#
	event_table = []
	for row in city_table:
		#split
		splited_row =re.split("@|(\d{2}/\d{2}):|[(](\d{2}h\d{2})|(\d{5})|-", row)
		#remove empty items and whitespace item
		splited_row = list(filter(None, splited_row))
		splited_row = list(filter(str.strip, splited_row))
		#clean up lost parentheses 
		splited_row[-1] = splited_row[-1].replace(')', '')
		#Strip random head and tail whitespace
		splited_row = [value.strip() for value in splited_row]
		event_table.append(splited_row)
	print('Events parsed:', len(event_table))
	return event_table

def saveJSON(table, filename):
	# Save as JSON
	with open(filename, 'w') as filehandle:  
		json.dump(table, filehandle)

def openJSON(filename):
	# Open JSON table
	with open(filename, 'r') as filehandle:
		table = json.load(filehandle)
	return table

def check_for_existing_table(filename):
	# check if a previous table dump exist and return the modification date
	# Retunr None if the file don't exist or the time in second since the last modification 
	if os.path.isfile(filename):
		print("Previous dump exist:", filename)
		mtime = os.path.getmtime(filename)
		print("last modification:", time.ctime(mtime))
		print("file age:", str(datetime.timedelta(seconds = round(time.time() - mtime))))
		return round(time.time() - mtime)
	else:
		print ("Previous dump do not exist") 
	return None

def fixdate(event_table):
	# Add year date and fix typos
	year = 2019
	month = 1
	for row in event_table:
		# ugly hack to fix typo error in the page
		if int(row[0][-2:]) < month and month > 10:
			year += 1 
		else:
			month = int(row[0][-2:])
		row[0] = row[0] + '/' + str(year)
	return event_table

def fixadress(event_table):
	# removed
	return event_table

def printevent(event_table): 
	for row in event_table:
		print(row)

# Main 
dump_age = check_for_existing_table(outputfilename)
if dump_age == None or dump_age > Reflesh_interval:
	response = getpage()
	event_table = parsing(response)
	event_table = fixdate(event_table)
	event_table = fixadress(event_table)
	saveJSON(event_table, outputfilename)
else:
	event_table = openJSON(outputfilename)
df = pd.DataFrame(event_table)
print(df.columns)
#printevent(event_table)
exit()

