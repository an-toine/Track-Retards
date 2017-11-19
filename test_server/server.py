#!/usr/bin/python

import json
import datetime
from tornado.log import enable_pretty_logging
import tornado.web
import tornado.ioloop
import tornado.httpserver

#Handler used to return data about disruptions for route disruptions
class DisruptionsHandler(tornado.web.RequestHandler):
	#Update disruptions templates to match the execution time
	def _update_template(self,template):
		begin_application_period = datetime.datetime.now()-datetime.timedelta(hours=4)
		end_application_period = datetime.datetime.now()+datetime.timedelta(hours=4)
		updated_at = datetime.datetime.now()-datetime.timedelta(hours=1)
		template = template.replace("{{date_updated_at}}",updated_at.strftime("%Y%m%dT%H%M%S"))
		template = template.replace("{{date_end_application}}",end_application_period.strftime("%Y%m%dT%H%M%S"))
		template = template.replace("{{date_begin_application}}",begin_application_period.strftime("%Y%m%dT%H%M%S"))
		return template

	#Handle GET requests
	def get(self):
		count=self.get_arguments("count")
		num_train=self.get_arguments("headsign")
		#Train 860171 is cancelled and 6785 is delayed by 15 minutes
		if num_train != []:
			if num_train[0] == "860171":
				#No start page ? Return the complete list of disrptions
				if len(count) == 1:
					output = ""
					with open("test_server/860171/disruptions_count1_860171","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(output))
				#Otherwise, return the last disruption, and update it
				else:
					output = ""
					with open("test_server/860171/last_disruption_860171","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(self._update_template(output)))

			elif num_train[0] == "6785":
				if len(count) == 1:
					output = ""
					with open("test_server/6785/disruptions_count1_6785","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(output))
				else:
					output = ""
					with open("test_server/6785/disruptions_6785","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(self._update_template(output)))

			elif num_train[0] == "13020":
				if len(count) == 1:
					output = ""
					with open("test_server/13020/disruptions_count1_13020","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(output))
				else:
					output = ""
					with open("test_server/13020/disruptions_13020","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(self._update_template(output)))
		else:
			self.set_status(404)
			return self.finish("Please specify a train number !")

#Handler used to return data about trips for cancelled train (no info in the disruption element)
class TripsHandler(tornado.web.RequestHandler):
	def get(self,trip_id):
		#The route ID of train 860171
		if trip_id == "OCE:SN860171F01005":
			output = ""
			#Read and return data
			with open("test_server/860171/trip_860171","r") as fichier:
				output = fichier.read()
			return self.write(json.loads(output))

#Handler returning data used when converting headsign to trip id
class HeadsignToTripidHandler(tornado.web.RequestHandler):
	def get(self):
		num_train=self.get_arguments("headsign")
		if num_train[0] == "860171":
			output = ""
			#Read and return data
			with open("test_server/860171/headsign_to_tripid_860171","r") as fichier:
				output = fichier.read()
			return self.write(json.loads(output))

#Set routes for App
handlers = [(r"/v1/coverage/sncf/disruptions",DisruptionsHandler),
(r"/v1/coverage/sncf/trips/(OCE:[A-Z0-9]{2,})/vehicle_journeys",TripsHandler),
(r"/v1/coverage/sncf/trips",HeadsignToTripidHandler)]

#Print access logs to stdout
enable_pretty_logging()
#Create App and serve requests on port 8080
application = tornado.web.Application(handlers)
server = tornado.httpserver.HTTPServer(application)
server.listen(8080)
tornado.ioloop.IOLoop.current().start()