#!/usr/bin/python
# coding: utf8

from datetime import datetime

#Parent of Canceled and Delay class
class event(object):

	def __init__(self, cause, departure_city, arrival_city, departure_date, num_train):
		#Store data in the object when instanciated
		self._num_train = num_train
		self._cause = cause
		self._departure_city = departure_city
		self._arrival_city = arrival_city
		self._departure_date = departure_date

	@property
	def num_train(self):
		return self._num_train

	@num_train.setter
	def num_train(self, value):
		self._num_train = value

	@property
	def departure_city(self):
		return self._departure_city

	@departure_city.setter
	def departure_city(self, value):
		self._departure_city = value

	@property
	def arrival_city(self):
		return self._arrival_city

	@arrival_city.setter
	def arrival_city(self, value):
		self._arrival_city = value

	@property
	def departure_date(self):
		return datetime.strftime(self._departure_date,"%H:%M:%S")

	def get_departure_datetime(self):
		now = datetime.now()
		return self._departure_date.replace(now.year,now.month,now.day)

	@departure_date.setter
	def departure_date(self, value):
		self._departure_date = value

	@property
	def cause(self):
		return self._cause

	@cause.setter
	def cause(self, value):
		self._cause = value