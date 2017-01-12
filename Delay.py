#!/usr/bin/python
# coding: utf8

from datetime import datetime, timedelta
from Event import event

#Class used to store the details of a delay
class delay(event):

	def __init__(self, disruption, num_train):
		#Collect data to instanciate the parent object
		stops_list = disruption["impacted_objects"][0]["impacted_stops"]
		last_stop = disruption["impacted_objects"][0]["impacted_stops"][len(stops_list)-1]
		cause = last_stop["cause"]
		departure_city = stops_list[0]["stop_point"]["name"]
		arrival_city = last_stop["stop_point"]["name"]
		departure_date = datetime.strptime(stops_list[0]["base_departure_time"],"%H%M%S")
		#Instanciate the parent object
		event.__init__(self, cause, departure_city, arrival_city, departure_date, num_train)
		base_arrival = last_stop["base_arrival_time"]
		amended_arrival = last_stop["amended_arrival_time"]
		#Store time data in the approtiate format
		self._base_arrival_date = datetime.strptime(base_arrival,"%H%M%S")
		self._amended_arrival_date = datetime.strptime(amended_arrival,"%H%M%S")

	def __str__(self):
		#Function called when the object is casted to string
		return("Train numero "+str(self._num_train)+" "+self._departure_city+" => "+self._arrival_city+
		"\nHeure de depart prévue : "+self.departure_date+
		"\nHeure d'arrivée prévue : "+self.base_arrival_date+
		"\nHeure d'arrivée effective : "+self.amended_arrival_date+
		"\nRetard : "+self.get_delay()+
		"\nCause : "+self.cause)

	@property
	def base_arrival_date(self):
		return datetime.strftime(self._base_arrival_date,"%H:%M:%S")

	@base_arrival_date.setter
	def base_arrival_date(self, value):
		self._base_arrival_date = value

	@property
	def amended_arrival_date(self):
		return datetime.strftime(self._amended_arrival_date,"%H:%M:%S")

	@amended_arrival_date.setter
	def amended_arrival_date(self, value):
		self._amended_arrival_date = value


	def get_delay(self,in_minutes=False):
		#Method used to compute the delay contained in this object.
		#The delay can be outputed as a string or in minutes
		if self._amended_arrival_date is not None and self._base_arrival_date is not None:
			if in_minutes == False:
				return str(self._amended_arrival_date - self._base_arrival_date)
			else:
				delay = self._amended_arrival_date - self._base_arrival_date
				return str(round(delay.total_seconds()/60))
		else:
			return 0