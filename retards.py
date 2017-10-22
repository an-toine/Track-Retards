#!/usr/bin/python
# coding: utf8

import json, urllib.request, base64, argparse, time, re
from datetime import datetime, timedelta
from libsncf.Delay import delay
from libsncf.DisruptionFactory import disruptionFactory
from libsncf.Tools import tools
from libsncf.Stats import stats
from Settings import settings

try:
	from outputs.GoogleSheet import googleSheet
	google_sheet_not_available = False
except ImportError:
	google_sheet_not_available = True

try:
	from outputs.Twitter import twitter
	twitter_not_available = False
except Exception:
	twitter_not_available = True

try:
	from outputs.MySQL import mysql
	mysql_not_available = False
except Exception as e:
	print(str(e))
	mysql_not_available = True

if __name__ == '__main__':
	#Deal with command line arguments
	parser = argparse.ArgumentParser(description='Programme permettant de récupérer les retards pour un numéro de train')
	parser.add_argument('num_train', action="store", type=int, help="Numéro du train à récupérer")
	parser.add_argument('--config', action="store", type=str, default="retards.cfg", help="Emplacement du fichier de configuration")
	parser.add_argument('--show-stats', action="store_true", default=False, dest="show_stats", help="Afficher des statistiques pour ce train. Cette option requiert MySQL")
	parser.add_argument('--weekly', action="store_true", default=False, dest="weekly_stats", help="Afficher des statistiques hebdomadaires pour ce train.")
	parser.add_argument('--monthly', action="store_true", default=False, dest="monthly_stats", help="Afficher des statistiques mensuelles pour ce train.")
	parser.add_argument('--no-google-sheets', action="store_true", default=False, dest="no_google_sheet", help="Ne pas envoyer les données sur Google Sheets")
	parser.add_argument('--no-twitter', action="store_true", default=False, dest="no_twitter", help="Ne pas envoyer les données sur Twitter")
	parser.add_argument('--no-mysql', action="store_true", default=False, dest="no_mysql", help="Ne pas envoyer les données sur MySQL")
	parser.add_argument('--version', action='version', version='%(prog)s 1.0')
	results = parser.parse_args()
	num_train = results.num_train

	#Load configuration
	settings = settings(results.config)

	#Create "tool" object to interact with SNCF API
	object_tools = tools(settings)

	#If stats must be displayed
	if(results.show_stats and not mysql_not_available):
		mysql_service = mysql(settings, object_tools)
		if results.monthly_stats:
			stats_object = stats("MONTHLY", num_train)
		else:
			stats_object = stats("WEEKLY", num_train)
		stats_object = mysql_service.populate_stats(stats_object)
		print(str(stats_object))
		if(not results.no_twitter and not twitter_not_available):
			#Instanciate a Twitter object with settings
			twitter_service = twitter(settings)
			twitter_service.post_message(stats_object.get_twitter_post())
		mysql_service.close_connection()
		exit(0)
	
	#Get disruptions for this train
	response = object_tools.get_disruptions(num_train)
	#Create the appropriate event for the disruption
	factory = disruptionFactory(response,num_train,object_tools)
	#Get this event
	event = factory.get_event()

	#There are two ways used to browse disruptions. If the first doesn't find the disruption,
	#we retrieve disruptions using the second way, just to be sure to not miss anything...
	if event is None:
		#Get disruptions for this train
		response = object_tools.get_disruptions(num_train,True)
		#Create the appropriate event for the disruption
		factory = disruptionFactory(response,num_train,object_tools)
		#Get this event
		event = factory.get_event()

	mysql_service = None

	if event is None:
		print("Aucun retard pour ce train")
		#If MySQL is not canceled by the user, and the import of required modules succeeded
		if(not results.no_mysql and not mysql_not_available):
			#Instanciate a MySQL object with settings
			mysql_service = mysql(settings, object_tools)
			mysql_service.save_normal_trip(num_train)
			mysql_service.close_connection()
		exit(0)
	elif type(event) is delay:
		#Sometime, a delay event is reported by SNCF, even if there is 0 minute of delay 
		if event.get_delay(in_minutes=True) == "0":
			print("Aucun retard pour ce train")
			#If MySQL is not canceled by the user, and the import of required modules succeeded
			if(not results.no_mysql and not mysql_not_available):
				#Instanciate a MySQL object with settings
				mysql_service = mysql(settings, object_tools)
				mysql_service.save_normal_trip(num_train)
				mysql_service.close_connection()
			exit(0)

	#Display the event
	print(str(event))

	#If Google Sheet is not canceled by the user, and the import of required modules succeeded
	if(not results.no_google_sheet and not google_sheet_not_available):
		#Instanciate a Google Sheet object with settings
		sheet = googleSheet(settings)
		sheet.upload_data(event)

	#If Twitter is not canceled by the user, and the import of required modules succeeded
	if(not results.no_twitter and not twitter_not_available):
		#Instanciate a Twitter object with settings
		twitter_service = twitter(settings)
		twitter_service.post_event(event)

	#If MySQL is not canceled by the user, and the import of required modules succeeded
	if(not results.no_mysql and not mysql_not_available):
		#Instanciate a MySQL object with settings
		mysql_service = mysql(settings, object_tools)
		mysql_service.save_item(event)
		mysql_service.close_connection()
