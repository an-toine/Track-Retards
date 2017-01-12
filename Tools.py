#!/usr/bin/python
# coding: utf8

import json, urllib.request, base64, argparse, time, re

#Class used to download data from the SNCF API
class tools(object):

	def __init__(self,settings):
		#Store the access token from the settings to auth on the API
		self._token_sncf = settings.sncf["token"]

	def _create_headers(self):
		#Headers used to authenticate on the API
		user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0"
		#Basic HTTP auth, the token is the username, no password used
		auth = base64.encodestring(('%s:%s' % (self._token_sncf,'')).encode()).decode().replace('\n', '')
		headers = {
			"Authorization"	: "Basic %s" % auth,
			"User-Agent" : "%s" % user_agent
		}
		return headers

	def _browse_disruptions(self,url,last_page=False):
		#Recursive method to find the last disruption for a train
		if last_page is False:
			#If we are not on the last page, we download the first result
			request = urllib.request.Request(url, None, self._create_headers())
		else:
			#To request the last disruption, we concatenate the number of the last page
			url = url+"&start_page="+str(last_page)
			request = urllib.request.Request(url, None, self._create_headers())
		json_obj = None
		try:
			#Download the previously crafted url
			with urllib.request.urlopen(request) as response:
				page = response.read()
				json_obj = json.loads(page.decode('utf-8'))
		except Exception as e:
			if isinstance(e, urllib.error.HTTPError):
				if e.code == 404:
					#404 : train not found
					print("Le serveur a retourné une erreur 404, le numéro de train n'existe probablement pas")
					exit(1)
			else:
				print("Une erreur s'est produite : "+str(e))
		
		if last_page == False:
			#If we aren't on the last page (first call of the method), we extract the number of last one
			last = None
			for link in json_obj["links"]:
				if link["type"] == "last":
					last = int(round(float(re.split("=",link["href"])[1])))
			if last == None:
				#No last page : just one element, send back the object
				return json_obj
			else:
				#Last page found : call this method to download the last page, and therefore, the last element
				return self._browse_disruptions(url,last_page=last)
		else:
			#We are on the last (most recent) disruption, we just send it back
			return json_obj

	def get_disruptions(self,num_train):
		#Public method to download the last disruption for a train number
		url = "https://api.sncf.com/v1/coverage/sncf/disruptions?count=1&headsign="+str(num_train)
		return self._browse_disruptions(url)

	def get_trip(self,trip_id):
		#Method used to download informations about a trip id
		url = "https://api.sncf.com/v1/coverage/sncf/trips/"+trip_id+"/vehicle_journeys"
		request = urllib.request.Request(url, None, self._create_headers())
		json_obj = None
		try:
			#Download output, parse it and return it
			with urllib.request.urlopen(request) as response:
				page = response.read()
				json_obj = json.loads(page.decode('utf-8'))
				return(json_obj)
		except Exception as e:
			if isinstance(e, urllib.error.HTTPError):
				if e.code == 404:
					#404 : train not found
					print("Le serveur a retourné une erreur 404, le numéro de train n'existe probablement pas")
					exit(1)
			else:
				print("Une erreur s'est produite : "+str(e))