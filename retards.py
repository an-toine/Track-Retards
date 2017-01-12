#!/usr/bin/python
# coding: utf8

import json, urllib.request, base64, argparse, time, re
from datetime import datetime, timedelta
from Delay import delay
from GoogleSheet import googleSheet
from DisruptionFactory import disruptionFactory
from Twitter import twitter
from Tools import tools
from Settings import settings


if __name__ == '__main__':
	#Deal with command line arguments
	parser = argparse.ArgumentParser(description='Programme permettant de récupérer les retards pour un numéro de train')
	parser.add_argument('num_train', action="store", type=int, help="Numéro du train à récupérer")
	parser.add_argument('--config', action="store", type=str, help="Emplacement du fichier de configuration")
	parser.add_argument('--no-google-sheets', action="store_true", default=False, dest="no_google_sheet", help="Ne pas envoyer les données sur Google Sheets")
	parser.add_argument('--no-twitter', action="store_true", default=False, dest="no_twitter", help="Ne pas envoyer les données sur Twitter")
	parser.add_argument('--version', action='version', version='%(prog)s 1.0')
	results = parser.parse_args()
	num_train = results.num_train

	#Load configuration
	settings = settings(results.config)

	#Create "tool" object to interact with SNCF API
	object_tools = tools(settings)
	
	#Get disruptions for this train
	response = object_tools.get_disruptions(num_train)

	#Create the appropriate event for the disruption
	factory = disruptionFactory(response,num_train)

	#Get this event
	event = factory.get_event()

	if event is None:
		print("Aucun retard pour ce train")
		exit(0)
	elif type(event) is delay:
		#Sometime, a delay event is reported by SNCF, even if there is 0 minute of delay 
		if event.get_delay(in_minutes=True) == "0":
			print("Aucun retard pour ce train")
			exit(0)

	#Display the event
	print(str(event))

	#If Google Sheet is not canceled by the user
	if(not results.no_google_sheet):
		#Instanciate a Google Sheet object with settings
		sheet = googleSheet(settings)
		sheet.upload_data(event)

	#If Twitter is not canceled by the user
	if(not results.no_twitter):
		#Instanciate a Twitter object with settings
		twitter_service = twitter()
		twitter_service.post_event(event)