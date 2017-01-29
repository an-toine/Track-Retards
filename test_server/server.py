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
		start_page=self.get_arguments("start_page")
		num_train=self.get_arguments("headsign")
		#Train 889951 is cancelled and 96559 is delayed by 10 minutes
		if num_train != []:
			if num_train[0] == "889951":
				#No start page ? Return the complete list of disrptions
				if start_page == []:
					output = ""
					with open("test_server/889951/disruptions_889951","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(output))
				#Otherwise, return the last disruption, and update it
				else:
					output = ""
					with open("test_server/889951/last_disruption_889951","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(self._update_template(output)))

			elif num_train[0] == "96559":
				if start_page == []:
					output = ""
					with open("test_server/96559/disruptions_96559","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(output))
				else:
					output = ""
					with open("test_server/96559/last_disruption_96559","r") as fichier:
						output = fichier.read()
					return self.write(json.loads(self._update_template(output)))
		else:
			self.set_status(404)
			return self.finish("Please specify a train number !")

#Handler used to return data about trips for cancelled train (no info in the disruption element)
class TripsHandler(tornado.web.RequestHandler):
	def get(self,trip_id):
		#The route ID of train 889951
		if trip_id == "OCE:SN889951F05003":
			output = ""
			#Read and return data
			with open("test_server/889951/trip_889951","r") as fichier:
				output = fichier.read()
			return self.write(json.loads(output))

#Set routes for App
handlers = [(r"/v1/coverage/sncf/disruptions",DisruptionsHandler),
(r"/v1/coverage/sncf/trips/(OCE:[A-Z0-9]{2,})/vehicle_journeys",TripsHandler)]

#Print access logs to stdout
enable_pretty_logging()
#Create App and serve requests on port 8080
application = tornado.web.Application(handlers)
server = tornado.httpserver.HTTPServer(application)
server.listen(8080)
tornado.ioloop.IOLoop.current().start()