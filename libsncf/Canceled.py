#!/usr/bin/python
# coding: utf8

from datetime import datetime, timedelta
import json, urllib.request, base64
from libsncf.Event import event
from libsncf.Tools import tools

#Class used to store informations about a cancelation
class canceled(event):
	def __init__(self, disruption, num_train, object_tools):
		#Save the cause of the cancelation and the trip id
		cause = disruption["disruptions"][0]["messages"][0]["text"]
		trip_id = disruption["disruptions"][0]["impacted_objects"][0]["pt_object"]["trip"]["id"]
		#Get information about the trip with the trip id
		trip = object_tools.get_trip(trip_id)
		departure_city = trip["vehicle_journeys"][0]["stop_times"][0]["stop_point"]["name"]
		last_stop = len(trip["vehicle_journeys"][0]["stop_times"])-1
		departure_city = trip["vehicle_journeys"][0]["stop_times"][0]["stop_point"]["name"]
		departure = trip["vehicle_journeys"][0]["stop_times"][0]["departure_time"]
		departure_date = datetime.strptime(departure,"%H%M%S")
		arrival_city = trip["vehicle_journeys"][0]["stop_times"][last_stop]["stop_point"]["name"]
		#Instanciate the parent class, event
		event.__init__(self, cause, departure_city, arrival_city, departure_date, num_train)

	def __str__(self):
		#Function called when the object is casted to string
		return("Train numero "+str(self._num_train)+" "+self._departure_city+" => "+self._arrival_city+
		"\n/!\\ Train supprimé /!\\"
		"\nHeure de depart prévue : "+self.departure_date+
		"\nCause : "+self.cause)