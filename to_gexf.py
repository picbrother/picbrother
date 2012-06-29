#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
from gexf import Gexf
from unac import unac


# mysql
DB_HOST		= "localhost"
DB_USER		= "root"
DB_PSWD		= "root"
DB_NAME		= "picbrother"

try:
 conn = MySQLdb.connect (host = DB_HOST,
                         user = DB_USER,
                         passwd = DB_PSWD,
                         db = DB_NAME,
                         use_unicode=True)
except MySQLdb.Error, e:
 print "Error %d: %s" % (e.args[0], e.args[1])
 sys.exit (1)

cursor = conn.cursor ()

if __name__ == '__main__':
	gexf = Gexf("PIC BROTHER","Le graph du pic !")
	graph = gexf.addGraph("undirected","static","Picbrother graph")
	cursor.execute ("SELECT id, fb_id, first_name, last_name FROM  `T_USER` ")
	rows = cursor.fetchall ()
	for row in rows:
		print "%s, %s, %s, %s" % (row[0], row[1], row[2], row[3])
		#graph.addNode(row[0],u"#%s => %s %s" % (row[1],row[2],row[3])) #  ==>  Probléme d'accent... Comment faire ?
		graph.addNode(str(row[0]),unac.unac_string("%s %s" % (row[2],row[3]), "utf-8"))
	print "Nombre de user ajoute : %d" % cursor.rowcount
	cursor.execute ("SELECT U1.user_id, U2.user_id, COUNT( * ) weight FROM  `J_PHOTO_USER` U1,  `J_PHOTO_USER` U2 WHERE U1.photo_id = U2.photo_id AND U1.user_id != U2.user_id GROUP BY U1.user_id, U2.user_id")
	rows = cursor.fetchall ()
	edge_id = 0
	for row in rows:
		print "%s, %s, %s, %s" % (edge_id,row[0], row[1], row[2])
		graph.addEdge(str(edge_id),str(row[0]),str(row[1]),str(row[2]))
		edge_id+=1
	print "Nombre de liens ajoute : %d" % cursor.rowcount  	
	output_file=open("output.gexf","w")
	print "coucou"
	gexf.write(output_file)
