#!/usr/bin/env python
# coding: utf-8
import os, sys, traceback
import re
import logging

LOG_FILE_PATH = "tmp/log/debug.log"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def __debug(msg):
	global logger
	logger.debug(msg)

def __error(msg):
	global logger
	logger.error(msg)
	quit()

######################################################################
# + class: IbisObject
# + desc: root object in Ibis library
######################################################################
class IbisObject:
	def __init__(self):
		self.logger = logging.getLogger(self.__class__.__name__)
		self.log_format = '%(asctime)s - %(levelname)s(%(name)s) # %(message)s'
		self.__open_log_file()

	def __del__(self):
		self.log_file.close()
		del self

	def __open_log_file(self):
		try:
			if os.path.exists(LOG_FILE_PATH):
				self.log_file = open(LOG_FILE_PATH, "a")
			else:
				self.log_file = open(LOG_FILE_PATH, "w")
				os.chmod(LOG_FILE_PATH, 0666)
			logging.basicConfig(filename=LOG_FILE_PATH,
					            level=logging.DEBUG,
								format=self.log_format,
								datefmt=DATE_FORMAT,)
		except Exception, (msg):
			__error(msg)

	def log(self, msg=""):
		self.logger.debug(msg)

	def error_log(self, msg=""):
		self.logger.error(msg)

######################################################################
# + class: View
# + desc: render HTML
######################################################################
class View(IbisObject):
	def __init__(self):
		IbisObject.__init__(self)
		self.__set_var = {}
		self.__set_arr = {}
		self.layout('lib/default/layout.html')

	def layout(self, filename):
		try:
			with open(filename, "r") as lf:
				self.__layout = lf.read()
		except Exception, (msg):
			self.error_log(msg)

	def render(self, filename):
		try:
			with open(filename, "r") as f:
				content = f.read()
		except Exception, (msg):
			self.error_log(msg)

		self.set("__CONTENT__", content)
		self.__layout = self.__expand(self.__layout)
		print self.__layout

	def set(self, var_name, value):
		if isinstance(value, str):
			self.__set_var[var_name] = value
		else:
			self.error_log("ERROR: set method need str value")

	def push(self, array_name, value):
		if isinstance(value, str):
			if not array_name in self.__set_arr:
				self.__set_arr[array_name] = []
			self.__set_arr[array_name].append(value)
		else:
			self.error_log("ERROR: push method need str array")

	# expand set variable ($$***$$) and set array (@@ $@***$@ @@)
	def __expand(self, string):
		# expand set array
		for arr in re.findall("@@(.*)@@", string, re.DOTALL):
			string = string.replace("@@"+arr+"@@", self.__expand_array(arr))
		# expand set variable
		for var in re.findall("\$\$(.*)\$\$", string):
			if var in self.__set_var:
				string = string.replace("$$"+var+"$$", self.__expand(self.__set_var[var]))
			else:
				string = string.replace("$$"+var+"$$", "")
		return string

	# expand set array (@@ ... @@) in `string`
	def __expand_array(self, string):
		try:
			array_names = []	# array names included in `string`
			array_len = 0		# max length of arrays
			for array_name in re.findall("\$@(.*)\$@", string):
				array_names.append(array_name)
				# find longest array length
				if array_name in self.__set_arr \
						and len(self.__set_arr[array_name]) > array_len:
					array_len = len(self.__set_arr[array_name])
			# output element by `array_len` times
			expanded_str = ""
			for i in range(array_len):
				element = string
				for array_name in array_names:
					if len(self.__set_arr[array_name]) > i:
						value = self.__set_arr[array_name][i]
						element = element.replace("$@"+array_name+"$@", value)
					else:
						element = element.replace("$@"+array_name+"$@", "")
				expanded_str += element
			return expanded_str
		except Exception, (msg):
			self.error_log(msg)

	def error_log(self, msg=""):
		self.logger.error(msg)
		info = sys.exc_info()
		tb_info = traceback.extract_tb(info[2])[0]
		# push stack info
		for st_info in traceback.extract_stack():
			self.push('__ERROR_FILE__', str(st_info[0]))
			self.push('__ERROR_LINE__', str(st_info[1]))
			self.push('__ERROR_FUNC__', str(st_info[2]))
			self.push('__ERROR_TEXT__', str(st_info[3]))
		# push current stack info
		self.set('__EXCEPTION_FILE__', str(tb_info[0]))
		self.set('__EXCEPTION_LINE__', str(tb_info[1]))
		self.set('__EXCEPTION_FUNC__', str(tb_info[2]))
		self.set('__EXCEPTION_TEXT__', str(tb_info[3]))
		self.set('__ERROR_MESSAGE__', str(msg))
		self.render('lib/error/error.html')
		quit()

######################################################################
# Shell Mode
######################################################################
import cgitb
import sqlite3
from xml.etree.ElementTree import *

SCHEMA_PATH = "./schema.xml"
MODEL_BUILD_PATH = "./model.py"

__MODEL_FILE_INIT = """\
###############################
# Ibis Model
###############################
import sqlite3
import re\n
class ModelQuery:
	def __init__(self):
		self.conn = sqlite3.connect("{0}.sqlite3")
		self.c = self.conn.cursor()

	def __del__(self):
		self.conn.close()
		del self

	def create_where(self, list):
		if not isinstance(list, type(dict())):
			print "ERROR(TODO): condition is not dict"
			quit()
		if len(list) == 0 or list["condition"] == "all":
			return ""
		elif not isinstance(list["condition"], type(dict())):
			print "ERROR(TODO): condition is not dict"
			quit()
		else:
			r_like = re.compile("\s*like\s+(\S+)\s*", re.IGNORECASE)
			r_comp = re.compile("\s*(==|!=|=|>=|>|<=|<)\s*(\S+)\s*")
			r_val = re.compile("\s*(\S+)\s*")
			sql = "where "
			for col_name in list["condition"]:
				if r_like.findall(list["condition"][col_name]) != []:
					for pattern in r_like.findall(list["condition"][col_name]):
						sql += "{{}} like '{{}}' and ".format(col_name, pattern)
				elif r_comp.findall(list["condition"][col_name]) != []:
					for cond in r_comp.findall(list["condition"][col_name]):
						operator = cond[0]
						value = cond[1]
						sql += "{{}} {{}} '{{}}' and ".format(col_name, operator, value)
				elif r_val.findall(list["condition"][col_name]) != []:
					value = r_val.findall(list["condition"][col_name])[0]
					sql += "{{}} = '{{}}' and ".format(col_name, value)
				else:
					print "ERROR(TODO): wrong pattern for sql"
					quit()
			sql = re.sub(" and $", "", sql)
			return sql

class Model:
	def __init__(self):
		self.__index = 0
		self.__data = {{}}
		self.field = []

	# is there enough column set in self
	def suffice(self):
		for column in self:
			if column == None:
				return False
		return True

	def __getitem__(self, index):
		if isinstance(index, basestring):
			if index in self.field:
				if index in self.__data:
					return self.__data[index]
				else:
					return None
			else:
				print "ERROR(TODO): no field such as '{{}}'".format(index)
		elif isinstance(index, int):
			if 0 <= index and index < len(self.field):
				if self.field[index] in self.__data:
					return self.__data[self.field[index]]
				else: # index not yet set
					return None
			else: # invalid index
				raise IndexError
		else:
			return None

	def __setitem__(self, index, value):
		if index in self.field:
			self.__data[index] = value
		else:
			print "ERROR(TODO): no field such as '{{}}'".format(index)

	def next(self):
		if self.__index > len(self.field):
			self.__index = 0
			raise StopIteration
		else:
			self.__index += 1
			if self.field[self.__index] in self.__data:
				return self.__data[self.field[self.__index]]
			else:
				return None
"""
__MODEL_QUERY = """
class {table}_query(ModelQuery):
	def insert(self, {arglist}):
		self.c.execute('{insert_sql}', ({columnlist}))
		self.conn.commit()

	def add(self, record):
		column_list = []
		if not isinstance(record, {table}):
			pass # ERROR(TODO)
		elif not record.suffice():
			print "ERROR(TODO): model do not have enough field"
			quit()
		for column in record:
			column_list += [column]
		self.c.execute('{add_sql}', column_list)
		self.conn.commit()

	def delete(self, cond):
		sql = "delete from {table} {{}}".format(self.create_where(cond))
		self.c.execute(sql)
		self.conn.commit()

	def find(self, cond={{}}):
		records = []
		sql = "select * from {table} {{}}".format(self.create_where(cond))
		self.c.execute(sql)
		col_info = self.conn.cursor().execute("pragma table_info({table})").fetchall()
		for record in self.c:
			col_dict = {{}} # {{'col_name': 'col_value',...}}
			for col in range(len(record)):
				col_name = col_info[col][1] # col_info: (id,name,type,notnull,dflt_value,pk)
				col_dict[col_name] = record[col]
			records += [{table}(col_dict)]
		return records 

	def show(self, cond={{}}):
		for record in self.find(cond):
			info = "|"
			for column in record:
				info += str(column) + "|"
			print info
"""

__MODEL_CLASS_INIT = """
class {table}(Model):
	# second arg col_list: {{'col_name': 'col_value',...}}
	def __init__(self, col_list={{}}):
		Model.__init__(self)
"""

__MODEL_COL_INIT = """\
		self.field += ["{col_name}"]
		if "{col_name}" in col_list:
			self["{col_name}"] = col_list["{col_name}"]
"""

# create model.py module (used by client script)
def __create_model(db_name, struct):
	with open(MODEL_BUILD_PATH, "w") as model:
		model.write(__MODEL_FILE_INIT.format(db_name))
		for table in struct:
			column_num = len(struct[table])
			insert_sql = "insert into {0} values(".format(table)
			add_sql = "insert into {0} values(".format(table)
			column_list = ""
			model_class = __MODEL_CLASS_INIT
			init_arg = ""
			for i in range(column_num):
				col_name = struct[table][i][0]
				model_class += __MODEL_COL_INIT.format(col_name=col_name)
				init_arg += col_name + ", "
				add_sql += "?,"
				if col_name != "id":
					insert_sql += "?,"
					column_list += col_name + ", "
				else:
					insert_sql += "null, "
			insert_sql = re.sub(",$", ")", insert_sql)
			add_sql = re.sub(",$", ")", add_sql)
			init_arg = re.sub(",$", "", init_arg)
			column_list = re.sub(" $", "", column_list)
			model.write(model_class.format(
				table=table,
				arglist=init_arg))
			model.write(__MODEL_QUERY.format(
				table=table,
				arglist=re.sub(",$", "", column_list),
				columnlist=column_list,
				insert_sql=insert_sql,
				add_sql=add_sql,))

# construct sqlite3 database
def __create_orm(schema):
	tree = parse(schema)
	db_struct = {}
	db_name = tree.getroot().get("name")
	conn = sqlite3.connect("%s.sqlite3" % db_name)
	c = conn.cursor()

	print "DATABASE: %s" % db_name
	for table in tree.findall(".//table"):
		table_name = table.get("name")
		print "    TABLE: `%s`" % table_name
		sql = "create table if not exists %s (" % table_name
		# no table column -> exception
		if len(table.findall(".//column")) == 0:
			__error("no column in table `%s`" % table_name)
		db_struct[table_name] = []
		for column in table.findall(".//column"):
			name = column.get("name")
			type = column.get("type")
			db_struct[table_name].append([name, type])
			if name == "id" and type == "integer":
				sql += "{0} {1} primary key autoincrement, ".format(name, type)
			else:
				sql += "{0} {1}, ".format(name, type)
		sql = re.sub(", $", ");", sql)
		c.execute(sql) # create table
	conn.commit()
	conn.close()

	__create_model(db_name, db_struct)

# do not output CGI header when this was executed by shell
if not __name__ == "__main__":
	cgitb.enable()
	print "Content-Type: text/html\n\n"
else:
######################################################################
# main stream
######################################################################
	global logger # logger for Ibis script
	logger = logging.getLogger("IbisLog")
	logging.basicConfig(level=logging.DEBUG)
	argc = len(sys.argv)
	if argc < 2:
		print "show help"	# TODO
	else:
		command = sys.argv[1]
		if command == "orm":
			if argc >= 3:
				filename = sys.argv[2]
				try:
					with open(filename, "r") as xmlfile:
						__create_orm(xmlfile)
				except IOError, (msg):
					__error(msg)
			else:
				try:
					with open(SCHEMA_PATH, "r") as xmlfile:
						__create_orm(xmlfile)
				except IOError:
					__error("prepare XML schema file named `%s`" % SCHEMA_PATH)
		else:
			print "show help" # TODO
