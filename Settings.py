#!/usr/bin/python
# coding: utf8

import configparser

#Class used to parse the config file and to store its options
class settings(object):
	def __init__(self, config_file):
		#Allow null values
		self._config_parser = configparser.ConfigParser(allow_no_value=True)
		#If no config file is issued, we try to load one in the current directory
		self._config_parser.read(config_file)
		if len(self._config_parser.sections()) == 0:
			raise FileNotFoundError("Impossible de charger le fichier de configuration !")
		
		#Load data
		self._sncf = {}
		self._twitter = {}
		self._google = {}
		self._mysql = {}
		self._sncf["token"] = self._config_parser.get("SNCF", "token")
		self._sncf["server_name"] = self._config_parser.get("SNCF", "server_name")
		self._twitter["consumer_key"] = self._config_parser.get("Twitter", "consumer_key")
		self._twitter["consumer_secret"] = self._config_parser.get("Twitter", "consumer_secret")
		self._twitter["access_token"] = self._config_parser.get("Twitter", "access_token")
		self._twitter["access_token_secret"] = self._config_parser.get("Twitter", "access_token_secret")
		self._twitter["status_delayed_train"] = self._config_parser.get("Twitter", "status_delayed_train")
		self._twitter["status_cancelled_train"] = self._config_parser.get("Twitter", "status_cancelled_train")
		self._twitter["status_stats_upward"] = self._config_parser.get("Twitter", "status_stats_upward")
		self._twitter["status_stats_downward"] = self._config_parser.get("Twitter", "status_stats_downward")
		self._twitter["status_stats_stable"] = self._config_parser.get("Twitter", "status_stats_stable")
		self._twitter["status_stats_normal"] = self._config_parser.get("Twitter", "status_stats_normal")
		self._google["sheets_secret_file"] = self._config_parser.get("Google-Sheets", "secret_file")
		self._google["sheets_credentials_file"] = self._config_parser.get("Google-Sheets", "credentials_file")
		self._google["sheets_spreadsheet_id"] = self._config_parser.get("Google-Sheets", "spreadsheet_id")
		self._google["sheets_tab_name"] = self._config_parser.get("Google-Sheets", "tab_name")
		self._mysql["mysql_host"] = self._config_parser.get("MySQL", "mysql_host")
		self._mysql["mysql_port"] = int(self._config_parser.get("MySQL", "mysql_port"))
		self._mysql["mysql_user"] = self._config_parser.get("MySQL", "mysql_user")
		self._mysql["mysql_password"] = self._config_parser.get("MySQL", "mysql_password")
		self._mysql["mysql_db"] = self._config_parser.get("MySQL", "mysql_db")

	@property
	def sncf(self):
		return self._sncf

	@property
	def twitter(self):
		return self._twitter

	@property
	def google(self):
		return self._google

	@property
	def mysql(self):
		return self._mysql