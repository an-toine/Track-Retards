#!/usr/bin/python
# coding: utf8

import tweepy
import emoji
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
			replace_dict = {'num_train': event.num_train, 'departure_city': event.departure_city, 'arrival_city': event.arrival_city, 'delay': event.get_delay(in_minutes=True)}
			message = self._twitter["status_delayed_train"].format(**replace_dict)
		else:
			replace_dict = {'num_train': event.num_train, 'departure_city': event.departure_city, 'arrival_city': event.arrival_city}
			message = self._twitter["status_cancelled_train"].format(**replace_dict)
		#Publish the message
		self._post(emoji.emojize(message, use_aliases=True))

	def post_stats(self, stats):
		if stats.range_type == 'MONTHLY':
			range_word = "ce mois"
		else:
			range_word = "cette semaine"
		if stats.disrupted_trip_count > 0:
			punctuality_rate = round((stats.normal_trip_count / stats.trip_count) * 100,2)
			last_punctuality_rate = (stats.last_normal_trip_count / stats.last_trip_count) * 100
			average_delay = 0
			if stats.disruption_time_sum is not None:
				average_delay = round((stats.disruption_time_sum / stats.trip_count),2)

			replace_dict = {"num_train": stats._num_train, "num_events": stats.disrupted_trip_count, "range": range_word, "num_cancelled": stats._canceled_trip_count, "avg_delay": average_delay, "punc_rate": punctuality_rate}

			if stats.disrupted_trip_count > stats.last_disrupted_trip_count:
				output = self._twitter["status_stats_downward"].format(**replace_dict)
			elif stats.disrupted_trip_count < stats.last_disrupted_trip_count:
				output = self._twitter["status_stats_upward"].format(**replace_dict)
			else:
				output = self._twitter["status_stats_stable"].format(**replace_dict)
		else:
			replace_dict = {"num_train": stats._num_train, "range": range_word}
			output = self._twitter["status_stats_normal"].format(**replace_dict)

		self._post(emoji.emojize(output, use_aliases=True))

	def post_message(self, message):
		if len(message)<280:
			self._post(emoji.emojize(message, use_aliases=True))
		else:
			print("Trop de caractères dans le message à envoyer sur Twitter !")
