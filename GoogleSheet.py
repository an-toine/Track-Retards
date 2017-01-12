#!/usr/bin/python
# coding: utf8

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from Delay import delay
from Event import event
from Canceled import canceled
from datetime import datetime

#Class used to save data in a Google Sheet document
class googleSheet(object):

	def __init__(self,settings):
		self._google = settings.google
		self._SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
		#OAuth client token file
		self._CLIENT_SECRET_FILE = self._google["sheets_secret_file"]
		#Application name, as defined in the Google API dashboard
		self._APPLICATION_NAME = 'Retards SNCF'
		#Method used to request an access to the user account
		self._credentials = self._get_credentials()

	def _get_credentials(self):
		#Credentials are saved in the file specified in the settings
		credential_path = (self._google["sheets_credentials_file"])
		#Check the access
		store = Storage(credential_path)
		credentials = store.get()
		#If access is not granted, ask for it
		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(self._CLIENT_SECRET_FILE, self._SCOPES)
			flow.user_agent = self._APPLICATION_NAME
			credentials = tools.run_flow(flow, store, None)
		#Return obtained credentials
		return credentials

	def upload_data(self, event):
		#Persist an event in Google Sheets
		credentials = self._credentials
		#Login on the platform
		http = credentials.authorize(httplib2.Http())
		#Get the service
		discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
		service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
		#Set the id of the document and the tab containing the table
		spreadsheetId = self._google["sheets_spreadsheet_id"]
		rangeName = self._google["sheets_tab_name"]+'!A1'
		#Define values to store, in the right order
		if type(event) is delay:
			values = [
			[
				datetime.strftime(datetime.now(),"%d/%m/%y"),
				event.num_train,
				event.departure_city+" => "+event.arrival_city,
				event.departure_date,
				event.base_arrival_date,
				event.amended_arrival_date,
				event.get_delay(),
				event.cause
			]
			]
		else:
			values = [
			[
				datetime.strftime(datetime.now(),"%d/%m/%y"),
				event.num_train,
				event.departure_city+" => "+event.arrival_city,
				event.departure_date,
				"Train supprimé",
				"n/a",
				"n/a",
				event.cause
			]
			]
		body = { 'values': values }
		#Persist values at the end of the existing values
		result = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=rangeName,valueInputOption="USER_ENTERED", body=body).execute()