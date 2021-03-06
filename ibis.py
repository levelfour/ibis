#!/usr/bin/env python
# coding: utf-8
import os, sys, traceback
import cgi
import re
import logging

LOG_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/tmp/log/debug.log"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

#********************************************************************
#********************************************************************
#   MODULE MODE
#********************************************************************
#********************************************************************

# print CGI debug info
def info():
	print cgi.test()

# output log to logger
def debug(msg):
	global logger
	logger.debug(msg)

# output error log to logger
def error(msg):
	global logger
	logger.error(msg)
	quit()

######################################################################
# + class: Get
# + desc: GET request data
######################################################################
class Get:
	def __init__(self, server):
		self.__index = 0
		self.__keys = []
		if "QUERY_STRING" in server:
			self.__qs = cgi.parse_qs(server["QUERY_STRING"])
			for key in self.__qs:
				self.__keys += [key]
		else:
			self.__qs = {}
	
	def __getitem__(self, key):
		if key in self.__qs:
			if len(self.__qs[key]) == 1:
				return self.__qs[key][0]
			else:
				return self.__qs[key]
		else:
			ibis.error_log("undefined key `{}` for GET data".format(key))

	def __iter__(self):
		return self

	def next(self):
		self.__index += 1
		if self.__index > len(self.__qs):
			self.__index = 0
			raise StopIteration
		else:
			return self.__keys[self.__index - 1]

######################################################################
# + class: Post
# + desc: POST request data
######################################################################
class Post:
	def __init__(self):
		self.__form = cgi.FieldStorage()
		self.__index = 0
		self.__keys = []
		for key in self.__form:
			self.__keys += [key]
	
	def __getitem__(self, key):
		if key in self.__form:
			return self.__form.getvalue(key)
		else:
			ibis.error_log("undefined key `{}` for POST data".format(key))

	def __iter__(self):
		return self

	def next(self):
		self.__index += 1
		if self.__index > len(self.__form):
			self.__index = 0
			raise StopIteration
		else:
			return self.__keys[self.__index - 1]

######################################################################
# + class: Request
# + desc: combine Get and Post with $_SERVER
######################################################################
class Request:
	def __init__(self):
		self.server = {}
		for key in os.environ:
			self.server[key] = os.environ[key]
		self.post = Post()
		self.get = Get(self.server)

	@classmethod
	def isGet(cls):
		if "REQUEST_METHOD" in os.environ:
			return os.environ["REQUEST_METHOD"] == "GET"
		else:
			return False

	@classmethod
	def isPost(cls):
		if "REQUEST_METHOD" in os.environ:
			return os.environ["REQUEST_METHOD"] == "POST"
		else:
			return False

	def isAjax(self):
		if "HTTP_X_REQUESTED_WITH" in self.server \
				and self.server["HTTP_X_REQUESTED_WITH"].lower() == "xmlhttprequest":
			return True
		else:
			return False

######################################################################
# constants for view
######################################################################
DEFAULT_LAYOUT = """\
<html lang="ja">
<head>
	<title>default</title>
	<meta charset="utf-8" />
	<style>
		body {
			font-family: "Lucida Grande", "segoe UI", "ヒラギノ丸ゴ ProN W4",
			"Hiragino Maru Gothic ProN", Meiryo, Arial, sans-serif;
		}
	</style>
</head>
<body>
	$$__CONTENT__$$
</body>
</html>"""

ERROR_CONTENT = """\
<style>
.error_table {border-collapse: collapse;}
.error_table th {color: white;background-color: red;}
.error_table td {background-color: orange;}
.error_table tr {border: none;}
.error_table th, .error_table td {
	text-align: left;
	font-size: large;
	border: solid 3px black;
	border-bottom: none;
	box-sizing: border-box;
}
.error_table tr:last-child td {border-bottom: solid 3px black;}
</style>
<table class="error_table">
	<tr><th colspan=4 style="font-size: x-large;">Ibis Error</th></tr>
	<tr><th colspan=4>EXCEPTION POINT</th></tr>
	<tr><th>FILE</th><th>LINE</th><th>FUNCTION</th><th>CODE</th></tr>
	<tr>
		<td>$$__EXCEPTION_FILE__$$</td>
		<td>$$__EXCEPTION_LINE__$$</td>
		<td>$$__EXCEPTION_FUNC__$$</td>
		<td>$$__EXCEPTION_TEXT__$$</td>
	</tr>
	<tr><th colspan=4>STACK INFO</th></tr>
	<tr><th>FILE</th><th>LINE</th><th>FUNCTION</th><th>CODE</th>
	</tr>
	@@<tr>
		<td>$@__ERROR_FILE__$@</td>
		<td>$@__ERROR_LINE__$@</td>
		<td>$@__ERROR_FUNC__$@</td>
		<td>$@__ERROR_TEXT__$@</td>
	</tr>@@
	<tr><th colspan=4>ERROR INFO</th></tr>
	<tr><td colspan=4>$$__ERROR_MESSAGE__$$</td></tr>
</table>"""

######################################################################
# + class: ibis
# + desc: render View, log, get HTTP request
######################################################################
class ibis():
	logger = logging.getLogger("ibis")
	log_format = '%(asctime)s - %(levelname)s(%(name)s) # %(message)s'
	request = Request()

	def __init__(self):
		self.__open_log_file()
		self.__set_var = {}
		self.__set_arr = {}
		self.__layout = DEFAULT_LAYOUT

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
								format=ibis.log_format,
								datefmt=DATE_FORMAT,)
		except Exception, (msg):
			print msg
			quit()

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
		if info[2] != None:
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
			self.set("__CONTENT__", ERROR_CONTENT)
			self.__layout = self.__expand(self.__layout)
			print self.__layout
		else:
			print msg
		quit()

	def debug(self, msg=""):
		self.logger.debug(msg)

#********************************************************************
#********************************************************************
#   SCRIPT MODE
#********************************************************************
#********************************************************************
import cgi
import cgitb
import sqlite3
from xml.etree.ElementTree import *

SCHEMA_PATH = "./schema.xml"
MODEL_BUILD_PATH = "./model.py"

######################################################################
# Model Templetes
######################################################################
__MODEL_FILE_INIT = """\
###############################
# Ibis Model
###############################
import os, sys
import sqlite3
import re\n
sys.path.append("{ibis_path}")
import ibis
_app = ibis.ibis()\n
class ModelQuery:
	def __init__(self):
		self.conn = sqlite3.connect("{db}.sqlite3")
		self.c = self.conn.cursor()
		self.column = []

	def __del__(self):
		self.conn.close()
		del self

	def create_where(self, list):
		if not isinstance(list, type(dict())):
			_app.error_log("condition is not dict")
		if not "condition" in list or list["condition"] == "all":
			return ""
		elif not isinstance(list["condition"], type(dict())):
			_app.error_log("condition is not dict")
		else:
			r_like = re.compile("\s*like\s+[\\'|\\"]?([^\s\\'\\"]+)[\\'|\\"]?s*", re.IGNORECASE)
			r_comp = re.compile("\s*(==|!=|=|>=|>|<=|<)\s*(\S+)\s*")
			r_val = re.compile("\s*(\S+)\s*")
			sql = "where "
			for col_name in list["condition"]:
				if isinstance(list["condition"][col_name], str):
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
						_app.error_log("wrong pattern for sql")
				elif isinstance(list["condition"][col_name], int):
					sql += "{{}} = {{}}".format(col_name, list["condition"][col_name])
			sql = re.sub(" and $", "", sql)
			return sql

	def create_order(self, list):
		r = re.compile("^\s*(\S+)\s+(asc|desc)\s*$", re.IGNORECASE)
		if not isinstance(list, type(dict())):
			_app.error_log("condition is not dict")
		elif not "order" in list:
			return ""
		elif not isinstance(list["order"], str) or r.findall(list["order"]) == []:
			_app.error_log("wrong format for order condition\\n{{\\"order\\": \\"field_name [asc|desc]\\"}}")
		else:
			# param : {{`field_name`: `asc or desc`}}
			param =  r.findall(list["order"])[0]
			return "order by {{}} {{}}".format(param[0], param[1])

class Model:
	def __init__(self):
		self.__index = 0
		self.__data = {{}}
		self.column = []

	# is there enough column set in self
	def suffice(self):
		for column in self.column:
			if not column["name"] in self.__data:
				if column["dflt"] != None:
					self.__data = column["dflt"]
				elif column["pk"] != True:
					return False
		return True

	def has_field(self, col_name):
		for i in range(len(self.column)):
			if self.column[i]["name"] == col_name:
				return True
		return False

	def __getitem__(self, index):
		if isinstance(index, basestring):
			if self.has_field(index):
				if index in self.__data:
					return self.__data[index]
				else:
					return None
			else:
				_app.error_log("no field such as '{{}}'".format(index))
		elif isinstance(index, int):
			if 0 <= index and index < len(self.column):
				if self.column[index]["name"] in self.__data:
					return self.__data[self.column[index]["name"]]
				else: # index not yet set
					return None
			else: # invalid index
				raise IndexError
		else:
			return None

	def __setitem__(self, index, value):
		if self.has_field(index):
			self.__data[index] = value
		else:
			_app.error_log("no field such as '{{}}'".format(index))

	def next(self):
		if self.__index > len(self.column):
			self.__index = 0
			raise StopIteration
		else:
			self.__index += 1
			if self.column[self.__index]["name"] in self.__data:
				return self.__data[self.column[self.__index]["name"]]
			else:
				return None
"""
__MODEL_QUERY = """
class {table}_query(ModelQuery):
	def __init__(self):
		ModelQuery.__init__(self)
		# col_info: (id,name,type,notnull,dflt_value,pk)
		self.column = self.conn.cursor().execute("pragma table_info({table})").fetchall()

	def insert(self, {arglist}):
		self.c.execute('{insert_sql}', ({columnlist}))
		self.conn.commit()

	def add(self, record):
		column_list = []
		if not isinstance(record, {table}):
			_app.error_log("invalid type of argument for add method")
		elif not record.suffice():
			_app.error_log("model do not have enough field")
			quit()
		for column in record:
			column_list += [column]
		self.c.execute('{add_sql}', column_list)
		self.conn.commit()

	def update(self, cond={{}}, value={{}}):
		if value == {{}}:
			_app.error_log("no update value set")	
		sql = "update {table} set "
		where = self.create_where(cond)
		for col in self.column[{NAME}]:
			if col in value:
				sql += "{{}} = '{{}}', ".format(col, value[col])
		sql = re.sub(", $", " "+where , sql)
		self.c.execute(sql)
		self.conn.commit()

	def delete(self, cond):
		sql = "delete from {table} {{}}".format(self.create_where(cond))
		self.c.execute(sql)
		self.conn.commit()

	def find(self, cond={{}}):
		records = []
		if "limit" in cond and isinstance(cond["limit"], int):
			limiter = "limit {{}}".format(cond["limit"])
		else:
			limiter = ""
		sql = "select * from {table} {{}} {{}} {{}}".format(
			self.create_where(cond),
			self.create_order(cond),
			limiter)
		self.c.execute(sql)
		for record in self.c:
			col_dict = {{}} # {{'col_name': 'col_value',...}}
			for col in range(len(self.column)):
				col_name = self.column[col][{NAME}]
				col_dict[col_name] = record[col]
			records += [{table}(col_dict)]
		return records 

	def show(self, cond={{}}):
		for record in self.find(cond):
			info = "|"
			for column in record:
				info += str(column) + "|"
			print info

	def describe(self):
		print "|id|name|type|notnull|dflt|pk|"
		for col in self.column:
			info = "|"
			for c in col:
				info += str(c) + "|"
			print info
"""

__MODEL_CLASS_INIT = """
class {table}(Model):
	# second arg col_list: {{'col_name': 'col_value',...}}
	def __init__(self, col_list={{}}):
		Model.__init__(self)
"""

__MODEL_COL_INIT = """\
		self.column += [{{{{
			"name":"{name}",
			"type":"{type}",
			"notnull":{notnull},
			"dflt":"{dflt}",
			"pk":{pk}}}}}]
		if "{name}" in col_list:
			self["{name}"] = col_list["{name}"]
"""

######################################################################
# Function
######################################################################

# create model.py module (used by client script)
def __create_model(db_name, struct):
	with open(MODEL_BUILD_PATH, "w") as model:
		model.write(__MODEL_FILE_INIT.format(
			ibis_path=os.path.dirname(os.path.abspath(__file__)),
			db=db_name))
		for table in struct:
			column_num = len(struct[table])
			insert_sql = "insert into {0} values(".format(table)
			add_sql = "insert into {0} values(".format(table)
			column_list = ""
			model_class = __MODEL_CLASS_INIT
			init_arg = ""
			for i in range(column_num):
				column = struct[table][i]
				col_name = column["name"]
				model_class += __MODEL_COL_INIT.format(
						name=col_name,
						type=column["type"],
						notnull=column["notnull"],
						dflt=column["dflt"],
						pk=column["pk"])
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
			model_class = re.sub("$", "\n", model_class)
			model.write(model_class.format(table=table))
			model.write(__MODEL_QUERY.format(
				table=table,
				arglist=re.sub(",$", "", column_list),
				columnlist=column_list,
				insert_sql=insert_sql,
				add_sql=add_sql,
				ID=0,NAME=1,TYPE=2,NOTNULL=3,DFLT=4,PK=5,))

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
			ibis.error_log("no column in table `%s`" % table_name)
		db_struct[table_name] = []
		for column in table.findall(".//column"):
			name	= column.get("name")
			ctype	= column.get("type")
			notnull	= bool(column.get("required", True))
			dflt	= column.get("defaultValue")
			pk		= bool(column.get("primaryKey", False))
			db_struct[table_name] += [{
				"name":name, 
				"type":ctype, 
				"notnull":notnull, 
				"dflt":dflt, 
				"pk":pk}]
			sql += "{} {} {} {} ".format(
					name, 
					ctype, 
					"not null" if notnull else "",
					"default '{}'".format(dflt) if dflt else "")
			if pk:
				sql += "primary key "
				#if column.get("autoIncrement"):
				sql += "autoincrement "
			sql += ", "
		sql = re.sub(", $", ");", sql)
		c.execute(sql) # create table
	conn.commit()
	conn.close()

	__create_model(db_name, db_struct)

# do not output CGI header when this was executed by shell
if not __name__ == "__main__" and "SERVER_SOFTWARE" in os.environ:
	cgitb.enable()
	print "Content-Type: text/html\n\n"
	global request
	request = Request()
elif __name__ == "__main__":
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
					error(msg)
			else:
				try:
					with open(SCHEMA_PATH, "r") as xmlfile:
						__create_orm(xmlfile)
				except IOError:
					error("prepare XML schema file named `%s`" % SCHEMA_PATH)
		else:
			print "show help" # TODO
