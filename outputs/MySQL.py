#!/usr/bin/python

from peewee import *
from libsncf.Delay import delay
from libsncf.Event import event
from libsncf.Canceled import canceled
from libsncf.Trip import trip as TripSncf
import datetime

_db = MySQLDatabase(None)

class mysql(object):
	def __init__(self, settings, tools):
		_db.init(settings.mysql["mysql_db"], host=settings.mysql["mysql_host"], port=settings.mysql["mysql_port"], user=settings.mysql["mysql_user"], passwd=settings.mysql["mysql_password"])
		try:
			_db.connect()
		except OperationalError:
			print("Connexion impossible au serveur MySQL {}:{}/{} avec le user {}".format(
				settings.mysql["mysql_host"],
				settings.mysql["mysql_port"],
				settings.mysql["mysql_db"],
				settings.mysql["mysql_user"]))
			exit(1)
		_db.create_tables([train, disruption, city, trip],safe=True)
		self._tools = tools

	def __del__(self):
		try:
			_db.close()
		except:
			pass

	def close_connection(self):
		_db.close()

	def save_item(self, item):
		if type(item) is delay:
			train_entity, nb_lines = train.get_or_create(id_train=item.num_train)
			disruption_entity = disruption.create(disruption_type="Delayed",disruption_cause=item.cause,disruption_delay=item.get_delay(in_minutes=True))
			arrival_city_entity, nb_lines = city.get_or_create(name=item.arrival_city)
			departure_city_entity, nb_lines = city.get_or_create(name=item.departure_city)
			departure_datetime = item.get_departure_datetime()
			arrival_datetime = item.get_base_arrival_datetime()
			trip_entity = trip.get_or_create(trip_departure_date=departure_datetime,trip_arrival_date=arrival_datetime,trip_train=train_entity,trip_departure_city=departure_city_entity,trip_arrival_city=arrival_city_entity,trip_disruption=disruption_entity)

		elif type(item) is canceled:
			train_entity, nb_lines = train.get_or_create(id_train=item.num_train)
			disruption_entity = disruption.create(disruption_type="Canceled",disruption_cause=item.cause,disruption_delay=None)
			arrival_city_entity, nb_lines = city.get_or_create(name=item.arrival_city)
			departure_city_entity, nb_lines = city.get_or_create(name=item.departure_city)
			departure_datetime = item.get_departure_datetime()
			arrival_datetime = None
			trip_entity = trip.get_or_create(trip_departure_date=departure_datetime,trip_arrival_date=arrival_datetime,trip_train=train_entity,trip_departure_city=departure_city_entity,trip_arrival_city=arrival_city_entity,trip_disruption=disruption_entity)

	def save_normal_trip(self, num_train):
		trip_id = self._tools.headsign_to_tripid(num_train)
		trip_object = TripSncf(self._tools.get_trip(trip_id))
		train_entity, nb_lines = train.get_or_create(id_train=num_train)
		disruption_entity = None
		arrival_city_entity, nb_lines = city.get_or_create(name=trip_object.arrival_city)
		departure_city_entity, nb_lines = city.get_or_create(name=trip_object.departure_city)
		trip_entity = trip.get_or_create(trip_departure_date=trip_object.departure_datetime,trip_arrival_date=trip_object.arrival_datetime,trip_train=train_entity,trip_departure_city=departure_city_entity,trip_arrival_city=arrival_city_entity,trip_disruption=disruption_entity)

	def populate_stats(self, stats_object):
		#Fetch the number of trips on this date range
		stats_object.trip_count = (trip
			.select()
			.join(train)
			.where((train.id_train == stats_object.num_train)
				& (trip.trip_departure_date > stats_object.start_range)
				& ((trip.trip_arrival_date < stats_object.end_range)
				| (trip.trip_arrival_date.is_null(True))))
			.count())
		#Quick check to avoid division by zero later
		if stats_object.trip_count == 0:
			print("Il n'y a pas assez de données pour le train {}. Le calcul des statistiques est impossible.".format(stats_object.num_train))
			exit(1)

		#Fetch the number of disrupted trips on this date range
		stats_object.disrupted_trip_count = (trip
			.select()
			.join(train)
			.where((train.id_train == stats_object.num_train)
				& (trip.trip_departure_date > stats_object.start_range)
				& ((trip.trip_arrival_date < stats_object.end_range)
				| (trip.trip_arrival_date.is_null(True)))
				& (trip.trip_disruption.is_null(False)))
			.count())
		
                #Number of canceled Trains
		stats_object.canceled_trip_count = (trip
			.select()
			.join(train)
			.where((train.id_train == stats_object.num_train)
				& (trip.trip_departure_date > stats_object.start_range)
				& (trip.trip_arrival_date.is_null(True)))
			.count())
		
                #Fetch the number of normal trips on this date range
		stats_object.normal_trip_count = (trip
			.select()
			.join(train)
			.where((train.id_train == stats_object.num_train)
				& (trip.trip_departure_date > stats_object.start_range)
				& ((trip.trip_arrival_date < stats_object.end_range)
				| (trip.trip_arrival_date.is_null(True)))
				& (trip.trip_disruption.is_null(True)))
			.count())

		#Last on this date range
		stats_object.last_trip_count = (trip
			.select()
			.join(train)
			.where((train.id_train == stats_object.num_train)
				& (trip.trip_departure_date > stats_object.last_start_range)
				& ((trip.trip_arrival_date < stats_object.last_end_range)
				| (trip.trip_arrival_date.is_null(True))))
			.count())
		stats_object.last_disrupted_trip_count = (trip
			.select()
			.join(train)
			.where((train.id_train == stats_object.num_train)
				& (trip.trip_departure_date > stats_object.last_start_range)
				& ((trip.trip_arrival_date < stats_object.last_end_range)
				| (trip.trip_arrival_date.is_null(True)))
				& (trip.trip_disruption.is_null(False)))
			.count())
		stats_object.last_normal_trip_count = (trip
			.select()
			.join(train)
			.where((train.id_train == stats_object.num_train)
				& (trip.trip_departure_date > stats_object.last_start_range)
				& ((trip.trip_arrival_date < stats_object.last_end_range)
				| (trip.trip_arrival_date.is_null(True)))
				& (trip.trip_disruption.is_null(True)))
			.count())
		query_disruption_type_count = (trip
			.select(fn.COUNT(trip.trip_departure_date).alias('count'), disruption.disruption_cause.alias('cause'))
			.join(disruption)
			.where((trip.trip_train_id == stats_object.num_train)
				& (trip.trip_departure_date > stats_object._start_range)
				& ((trip.trip_arrival_date < stats_object._end_range)
				| (trip.trip_arrival_date.is_null(True))))
			.group_by(disruption.disruption_cause)
			.order_by(SQL('count').desc()))
		tmp = []
		for elmnt in query_disruption_type_count:
			tmp.append((elmnt.trip_disruption.cause,elmnt.count))
		stats_object.disruption_type_count = tmp
		stats_object.disruption_time_sum = (disruption
			.select(fn.SUM(disruption.disruption_delay))
			.join(trip)
			.where((trip.trip_train_id == stats_object.num_train)
				& (trip.trip_departure_date > stats_object._start_range)
				& (trip.trip_arrival_date < stats_object._end_range)
				& (disruption.disruption_type == "delayed"))
			.scalar()
		)
		return stats_object

class MySQLModel(Model):
	class Meta:
		database = _db

class train(MySQLModel):
	id_train = PrimaryKeyField()

class disruption(MySQLModel):
	id_disruption = PrimaryKeyField()
	disruption_type = CharField(max_length=20, null=False)
	disruption_cause = CharField(max_length=60, null=True)
	disruption_delay = IntegerField(null=True)

class city(MySQLModel):
	id_city = PrimaryKeyField()
	name = CharField(max_length=50, null=False)

class trip(MySQLModel):
	trip_departure_date = DateTimeField(null=False)
	trip_arrival_date = DateTimeField(null=True)
	trip_train = ForeignKeyField(train, related_name="trips")
	trip_departure_city = ForeignKeyField(city, related_name="trips_departure")
	trip_arrival_city = ForeignKeyField(city, related_name="trips_arrival")
	trip_disruption = ForeignKeyField(disruption, related_name="trips", null=True)

	class Meta:
		primary_key = CompositeKey('trip_departure_date','trip_train','trip_departure_city','trip_arrival_city')
