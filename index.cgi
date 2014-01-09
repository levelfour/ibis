#!/usr/bin/env python
# coding: utf-8
import ibis

if __name__ == "__main__":
	v = ibis.View()
	v.layout('view/layout.html')
	v.render('view/content.html')
	for v in ibis.post:
		print "form[{}]: {}".format(v, ibis.post[v])
