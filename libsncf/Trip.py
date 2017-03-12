#!/usr/bin/python
# coding: utf8

from datetime import datetime

class trip(object):

	def __init__(self, trip_json):
		self._departure_city = trip_json["vehicle_journeys"][0]["stop_times"][0]["stop_point"]["name"]
		last_stop = len(trip_json["vehicle_journeys"][0]["stop_times"])-1
		self._arrival_city = trip_json["vehicle_journeys"][0]["stop_times"][last_stop]["stop_point"]["name"]
		now = datetime.now()
		self._departure = trip_json["vehicle_journeys"][0]["stop_times"][0]["departure_time"]
		departure_datetime = datetime.strptime(self._departure,"%H%M%S")
		departure_datetime = departure_datetime.replace(now.year,now.month,now.day)
		self._departure_datetime = departure_datetime
		self._arrival = trip_json["vehicle_journeys"][0]["stop_times"][last_stop]["arrival_time"]
		arrival_datetime = datetime.strptime(self._arrival,"%H%M%S")
		arrival_datetime = arrival_datetime.replace(now.year,now.month,now.day)
		self._arrival_datetime = arrival_datetime

	@property
	def departure_city(self):
		return self._departure_city

	@property
	def arrival_city(self):
		return self._arrival_city

	@property
	def departure(self):
		return self._departure

	@property
	def departure_datetime(self):
		return self._departure_datetime

	@property
	def arrival(self):
		return self._arrival

	@property
	def arrival_datetime(self):
		return self._arrival_datetime