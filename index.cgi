#!/usr/bin/env python
# coding: utf-8
import os
import logging

LOG_FILE_PATH = "tmp/log/debug.log"

print "Content-Type: text/html\n\n"

class View:
	def __init__(self):
		self.__layout = ""
		try:
			if os.path.exists(LOG_FILE_PATH):
				self.__log_file = open(LOG_FILE_PATH, "a")
			else:
				self.__log_file = open(LOG_FILE_PATH, "w")
			logging.basicConfig(filename=LOG_FILE_PATH,
					            level=logging.DEBUG)
		except Exception, (msg):
			print msg
			quit()

	def __del(self):
		self.__logfile.close()

	def layout(self, filename):
		try:
			with open(filename, "r") as lf:
				self.__layout = lf.read()
		except IOError, (msg):
			self.error_log(msg)

	def render(self, filename):
		try:
			with open(filename, "r") as f:
				content = f.read()
		except IOError, (msg):
			self.error_log(msg)

		try:
			html = self.__layout.replace("%%content%%", content)
		except:
			pass
		print html

	def log(msg=""):
		logging.debug(msg)

	def error_log(msg=""):
		logging.error(msg)
		quit()

############################################

if __name__ == "__main__":
	v = View()
	v.layout('layout.html')
	v.render('content.html')
