#!/usr/bin/python
# coding: utf8

import unittest
from Settings import settings
from libsncf.Tools import tools
from libsncf.DisruptionFactory import disruptionFactory
from libsncf.Delay import delay
from libsncf.Canceled import canceled

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
		disruption = self._object_tools.get_disruptions("889951")
		self.assertEqual(disruption["disruptions"][0]["severity"]["name"],"trip canceled")

	#Test trip downloading
	def test_trip(self):
		trip = self._object_tools.get_trip("OCE:SN889951F05003")
		self.assertEqual(trip["vehicle_journeys"][0]["stop_times"][11]["stop_point"]["name"],"St-Etienne-Châteaucreux")

#Test case for the DisruptionsFactory methods

class FactoryTest(unittest.TestCase):
	#Set up the test
	def setUp(self):
		self._settings = settings("retards.cfg")
		self._object_tools = tools(self._settings)
		self._train_delayed = self._object_tools.get_disruptions("96559")
		self._train_canceled = self._object_tools.get_disruptions("889951")

	#Test delayed trains
	def test_delay(self):
		factory = disruptionFactory(self._train_delayed,"96559",self._object_tools)
		event = factory.get_event()
		#Check whether the event is of the correct type
		self.assertIsInstance(event,delay)
		#Control the delay in minutes
		self.assertEqual(event.get_delay(in_minutes=True),"10")

	#Test canceled trains
	def test_cancel(self):
		factory = disruptionFactory(self._train_canceled,"889951",self._object_tools)
		event = factory.get_event()
		#Check whether the event is of the correct type
		self.assertIsInstance(event,canceled)
		#Control the arrival city is correct
		self.assertEqual(event.arrival_city,"St-Etienne-Ch\u00e2teaucreux")