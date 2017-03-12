#!/usr/bin/python
# coding: utf8

from datetime import datetime, timedelta
import json, urllib.request, base64
from libsncf.Event import event
from libsncf.Tools import tools
from libsncf.Trip import trip

#Class used to store informations about a cancelation
class canceled(event):
	def __init__(self, disruption, num_train, object_tools):
		#Save the cause of the cancelation and the trip id
		cause = disruption["disruptions"][0]["messages"][0]["text"]
		trip_id = disruption["disruptions"][0]["impacted_objects"][0]["pt_object"]["trip"]["id"]
		#Get information about the trip with the trip id
		trip_object = trip(object_tools.get_trip(trip_id))
		#Instanciate the parent class, event
		event.__init__(self, cause, trip_object.departure_city, trip_object.arrival_city, trip_object.departure_datetime, num_train)

	def __str__(self):
		#Function called when the object is casted to string
		return("Train numero "+str(self._num_train)+" "+self._departure_city+" => "+self._arrival_city+
		"\n/!\\ Train supprimé /!\\"
		"\nHeure de depart prévue : "+self.departure_date+
		"\nCause : "+self.cause)