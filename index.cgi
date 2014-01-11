#!/usr/bin/env python
# coding: utf-8
import ibis

if __name__ == "__main__":
	app = ibis.ibis()
	v = ibis.View()
	v.layout('view/layout.html')
	v.render('view/content.html')

	for v in app.request.post:
		print "post[{}] = {}<br />".format(v, app.request.post[v])

	print "<br />"
	
	print "This request is {}GET<br />".format("" if app.request.isGet() else "not ")
	print "This request is {}POST<br />".format("" if app.request.isPost() else "not ")
	print "This request is {}Ajax<br />".format("" if app.request.isAjax() else "not ")
