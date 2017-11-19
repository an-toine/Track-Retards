#!/usr/bin/python
# coding: utf8

import unittest
from Settings import settings
from libsncf.Tools import tools
from libsncf.DisruptionFactory import disruptionFactory
from libsncf.Delay import delay
from libsncf.Canceled import canceled
from libsncf.Trip import trip

#Test case for the settings manager
class SettingsTest(unittest.TestCase):
	#Check if settings are loaded correctly
	def test_correct_load(self):
		my_settings = settings("retards.cfg")
		self.assertEqual(my_settings.sncf["server_name"],"http://127.0.0.1:8080/")

	#Check load of a non existant file
	def test_incorrect_load(self):
		self.assertRaises(FileNotFoundError, settings, "not_existing_file.cfg")

#Test case for the Tools methods
class ToolsTest(unittest.TestCase):
	#Set up the test
	def setUp(self):
		self._settings = settings("retards.cfg")
		self._object_tools = tools(self._settings)

	#Test disruption downloading
	def test_disruption(self):
		disruption = self._object_tools.get_disruptions("860171")
		self.assertEqual(disruption["disruptions"][0]["severity"]["name"],"trip delayed")

	#Test trip downloading
	def test_trip(self):
		trip = self._object_tools.get_trip("OCE:SN860171F01005")
		self.assertEqual(trip["vehicle_journeys"][0]["stop_times"][7]["stop_point"]["name"],"Bressuire")

	#Test conversion from headsign to trip id
	def test_headsign_to_tripid(self):
		trip_id = self._object_tools.headsign_to_tripid("860171")
		self.assertEqual(trip_id,"OCE:SN860171F01005")

#Test case for the Trip methods
class TripTest(unittest.TestCase):
	#Set up the test
	def setUp(self):
		self._settings = settings("retards.cfg")
		self._object_tools = tools(self._settings)
		self._trip = trip(self._object_tools.get_trip("OCE:SN860171F01005"))

	#Test Trip methods
	def test_trip(self):
		self.assertEqual(self._trip.departure_city,"Tours")
		self.assertEqual(self._trip.arrival_city,"Bressuire")
		self.assertEqual(self._trip.departure,"200000")
		self.assertEqual(self._trip.arrival,"214500")

#Test case for the DisruptionsFactory methods
class FactoryTest(unittest.TestCase):
	#Set up the test
	def setUp(self):
		self._settings = settings("retards.cfg")
		self._object_tools = tools(self._settings)
		self._train_delayed = self._object_tools.get_disruptions("6785", True)
		self._train_canceled = self._object_tools.get_disruptions("860171", True)

	#Test delayed trains
	def test_delay(self):
		factory = disruptionFactory(self._train_delayed,"6785",self._object_tools)
		event = factory.get_event()
		#Check whether the event is of the correct type
		self.assertIsInstance(event,delay)
		#Control the delay in minutes
		self.assertEqual(event.get_delay(in_minutes=True),"15")

	#Test canceled trains
	def test_cancel(self):
		factory = disruptionFactory(self._train_canceled,"860171",self._object_tools)
		event = factory.get_event()
		#Check whether the event is of the correct type
		self.assertIsInstance(event,canceled)
		#Control the arrival city is correct
		self.assertEqual(event.arrival_city,"Bressuire")