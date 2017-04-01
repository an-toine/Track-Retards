#!/usr/bin/python
# coding: utf8

import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import calendar
import emoji

class stats(object):

	def __init__(self, range_type, num_train):
		self._num_train = num_train
		self._trip_count = None
		self._disrupted_trip_count = None
		self._canceled_trip_count = None
		self._normal_trip_count = None
		self._last_trip_count = None
		self._last_disrupted_trip_count = None
		self._last_normal_trip_count = None
		self._disruption_type_count = []
		self._disruption_time_sum = None
		self._range_type = range_type
		if range_type == "WEEKLY":
			self._start_range, self._end_range, self._last_start_range, self._last_end_range = self._get_week_range()
		elif range_type == "MONTHLY":
			self._start_range, self._end_range, self._last_start_range, self._last_end_range = self._get_month_range()

	def _get_week_range(self):
		now = datetime.datetime.now()
		year,week,day_of_week = now.isocalendar()
		if day_of_week == 1:
			start_date = now.replace(hour=0,minute=0,second=0,microsecond=0)
		else:
			start_date = now-datetime.timedelta(day_of_week)+datetime.timedelta(1)
			start_date = start_date.replace(hour=0,minute=0,second=0,microsecond=0)
		end_date = start_date+datetime.timedelta(6)
		end_date = end_date.replace(hour=23,minute=59,second=59,microsecond=0)
		return start_date, end_date, start_date - datetime.timedelta(7), end_date - datetime.timedelta(7)

	def _get_month_range(self):
		now = datetime.datetime.now()
		start_date = now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
		first_day, num_days = calendar.monthrange(now.year,now.month)
		end_date = now.replace(day=num_days,hour=23,minute=59,second=59,microsecond=0)
		last_start_date = start_date - relativedelta(months=1)
		last_end_date = end_date - relativedelta(months=1)
		return start_date, end_date, last_start_date, last_end_date

	def __str__(self):
		punctuality_rate = (self._normal_trip_count / self._trip_count) * 100
		last_punctuality_rate = (self._last_normal_trip_count / self._last_trip_count) * 100
		average_delay = 0
		if self._disruption_time_sum is not None:
			average_delay = round((self._disruption_time_sum / self._trip_count),2)
		
		if self._disrupted_trip_count > self._last_disrupted_trip_count:
			adjective = "en baisse"
		elif self._disrupted_trip_count < self._last_disrupted_trip_count:
			adjective = "en hausse"
		else:
			adjective = "stable"

		if self._last_disrupted_trip_count > 1:
			disruption_word = "perturbations"
		else:
			disruption_word = "perturbation"

		if self._disrupted_trip_count > 1:
			trip_word = "voyages"
		else:
			trip_word = "voyage"

		output = "Du {} au {}, le train {} a été perturbé {} {} sur {}, soit un taux de ponctualité de {}%, {} par rapport à la periode précédente ({} {}, {}%, de ponctualité).".format(self._start_range.strftime("%d/%m/%Y"),
				self._end_range.strftime("%d/%m/%Y"),
				self._num_train,
				self._disrupted_trip_count,
				trip_word,
				self._trip_count,
				round(punctuality_rate,2),
				adjective,
				self._last_disrupted_trip_count, 
				disruption_word,
				round(last_punctuality_rate,2))

		if average_delay > 0:
			output = output+"\n\nLe retard moyen est de {} minutes.".format(average_delay)

		if len(self._disruption_type_count) > 0:
			output = output+"\n\nCauses de perturbation :\n"
			for elmnt in self._disruption_type_count:
				if elmnt[1] == 1:
					output = output+"\n* {} : {} problème".format(elmnt[0],elmnt[1])
				else:
					output = output+"\n* {} : {} problèmes".format(elmnt[0],elmnt[1])
		return output

	def get_twitter_post(self):
		if self._range_type == 'MONTHLY':
			range_word = "ce mois ci"
		else:
			range_word = "cette semaine"
		if self._disrupted_trip_count > 0:
			punctuality_rate = round((self._normal_trip_count / self._trip_count) * 100,2)
			last_punctuality_rate = (self._last_normal_trip_count / self._last_trip_count) * 100
			average_delay = 0
			if self._disruption_time_sum is not None:
				average_delay = round((self._disruption_time_sum / self._trip_count),2)
			
			if self._disrupted_trip_count > self._last_disrupted_trip_count:
				adjective = emoji.emojize("en baisse :chart_with_downwards_trend:",use_aliases=True)
			elif self._disrupted_trip_count < self._last_disrupted_trip_count:
				adjective = emoji.emojize("en hausse :chart_with_upwards_trend:",use_aliases=True)
			else:
				adjective = emoji.emojize("stable :arrow_right:",use_aliases=True)

			canceled_block = ""
			if self._canceled_trip_count > 0:
				canceled_block = "dont {} suppressions, ".format(self._canceled_trip_count)

			output = "@SNCF #train {} perturbé {} fois {}, {}retard moyen de {} minutes, ponctualité de {}%, {}".format(self._num_train,
				self._disrupted_trip_count,
				range_word,
				canceled_block,
				average_delay,
				punctuality_rate,
				adjective)
		else:
			output = emoji.emojize("@SNCF le #train {} n'a pas été perturbé {} :tada: Pourvu que ça dure...".format(self._num_train, range_word),use_aliases=True)

		return output

	@property
	def num_train(self):
		return self._num_train

	@property
	def start_range(self):
		return self._start_range

	@property
	def end_range(self):
		return self._end_range

	@property
	def last_start_range(self):
		return self._last_start_range

	@property
	def last_end_range(self):
		return self._last_end_range

	@property
	def trip_count(self):
		return self._trip_count

	@trip_count.setter
	def trip_count(self, value):
		self._trip_count = value

	@property
	def disrupted_trip_count(self):
		return self._disrupted_trip_count

	@disrupted_trip_count.setter
	def disrupted_trip_count(self, value):
		self._disrupted_trip_count = value

	@property
	def canceled_trip_count(self):
		return self._canceled_trip_count

	@canceled_trip_count.setter
	def canceled_trip_count(self, value):
		self._canceled_trip_count = value

	@property
	def normal_trip_count(self):
		return self._normal_trip_count

	@normal_trip_count.setter
	def normal_trip_count(self, value):
		self._normal_trip_count = value

	@property
	def last_trip_count(self):
		return self._last_trip_count

	@last_trip_count.setter
	def last_trip_count(self, value):
		self._last_trip_count = value

	@property
	def last_disrupted_trip_count(self):
		return self._last_disrupted_trip_count

	@last_disrupted_trip_count.setter
	def last_disrupted_trip_count(self, value):
		self._last_disrupted_trip_count = value

	@property
	def last_normal_trip_count(self):
		return self._last_normal_trip_count

	@last_normal_trip_count.setter
	def last_normal_trip_count(self, value):
		self._last_normal_trip_count = value

	@property
	def disruption_type_count(self):
		return self._disruption_type_count

	@disruption_type_count.setter
	def disruption_type_count(self, value):
		self._disruption_type_count = value

	@property
	def disruption_time_sum(self):
		return self._disruption_time_sum

	@disruption_time_sum.setter
	def disruption_time_sum(self, value):
		self._disruption_time_sum = value