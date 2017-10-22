#!/usr/bin/python
# coding: utf8

import tweepy
from libsncf.Delay import delay
from libsncf.Event import event
from libsncf.Canceled import canceled
from datetime import datetime

class twitter(object):

	def __init__(self,settings):
		self._twitter = settings.twitter
		# Set auth parameters, firstly Consumer Key, secondly Consumer Secret
		self._auth = tweepy.OAuthHandler(self._twitter["consumer_key"],self._twitter["consumer_secret"])
		# Set access token to use RALeBot account, firstly Access Token, secondly Access Token Secret
		self._auth.set_access_token(self._twitter["access_token"],self._twitter["access_token_secret"])
		# Auth on Twitter
		try:
			self._api = tweepy.API(auth_handler=self._auth, compression=True)
		except tweepy.TweepError:
			print("Impossible de se connecter à Twitter")

	def _post(self, message):
		#Private method for sending a message on Twitter
		try:
			self._api.update_status(message)
		except tweepy.TweepError:
			print("Erreur lors de l'envoi du message sur Twitter")

	def post_event(self, event):
		#Public method to publish an avent
		message = ""
		#Define the pattern of messages to send to our beloved SNCF
		if type(event) is delay:
			message = "@SNCFTERAURA, mon #train {} {}/{} était en #retard de {} minutes, une explication? #TER @auvergnerhalpes".format(event.num_train,event.departure_city,event.arrival_city,event.get_delay(in_minutes=True))
		else:
			message = "@SNCFTERAURA, mon #train {} {}/{} était #supprimé, une explication? #TER @auvergnerhalpes".format(event.num_train,event.departure_city,event.arrival_city)
		#Publish the message
		self._post(message)

	def post_message(self, message):
		if len(message)<140:
			self._post(message)
