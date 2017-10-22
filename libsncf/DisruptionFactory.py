#!/usr/bin/python
# coding: utf8

from datetime import datetime
from libsncf.Delay import delay
from libsncf.Canceled import canceled

#Factory creating the right object for a specified disruption
class disruptionFactory(object):

	def __init__(self, response, num_train, object_tools):
		#We assume that the train is not (yet) canceled
		self._canceled_train = False
		self._response = response
		self._num_train = num_train
		self._object_tools = object_tools
		#There should be just one disruption, but just in case, we loop on it
		for disruption in response["disruptions"]:
			if "impacted_stops" in disruption["impacted_objects"][0]:
				for impact in disruption["impacted_objects"][0]["impacted_stops"]:
					if impact["arrival_status"] == "deleted":
						self._canceled_train = True
			#If the effect of the disruption on the train is "NO_SERVICE", the train is canceled
			elif "effect" in disruption["severity"]:
				if disruption["severity"]["effect"] == "NO_SERVICE":
					self._canceled_train = True

	@property
	def canceled_train(self):
		return self._canceled_train

	@canceled_train.setter
	def canceled_train(self, value):
		self._canceled_train = value

	@property
	def object_tools(self):
		return self._object_tools

	@object_tools.setter
	def object_tools(self, value):
		self._object_tools = value

	def get_event(self):
		#This method returns the appropriate object to store the disruption
		if self._canceled_train :
			for elmnt in self._response["disruptions"]:
				#Collect time information about the cancelation
				updated_at_date = datetime.strptime(elmnt["updated_at"],"%Y%m%dT%H%M%S")
				begin_application_date = datetime.strptime(elmnt["application_periods"][0]["begin"],"%Y%m%dT%H%M%S")
				end_application_date = datetime.strptime(elmnt["application_periods"][0]["end"],"%Y%m%dT%H%M%S")
				today = datetime.now().strftime("%Y%m%d")
				#If the disruption was updated today, and we are in the range of the application period
				if datetime.now().day == end_application_date.day and datetime.now().day == begin_application_date.day and updated_at_date.strftime("%Y%m%d") == today:
					#Return a canceled object
					return canceled(self._response, self._num_train, self._object_tools)
				else:
					return None
		else:
			disruption = None
			for elmnt in self._response["disruptions"]:
				#Collect time information about the delay
				updated_at_date = datetime.strptime(elmnt["updated_at"],"%Y%m%dT%H%M%S")
				begin_application_date = datetime.strptime(elmnt["application_periods"][0]["begin"],"%Y%m%dT%H%M%S")
				end_application_date = datetime.strptime(elmnt["application_periods"][0]["end"],"%Y%m%dT%H%M%S")
				today = datetime.now().strftime("%Y%m%d")
				#If the disruption was updated today, and we are in the range of the application period
				if datetime.now().day == end_application_date.day and datetime.now().day == begin_application_date.day and updated_at_date.strftime("%Y%m%d") == today:
					disruption = elmnt
			
			#If no delay was identified
			if disruption is None:
				return None
			#If one was identified, return the delay object
			else:
				return delay(disruption, self._num_train)
