from django.http import HttpResponse
from django.http import JsonResponse
from multiprocessing import Process, Queue
from manageQueue import startworker, getQueue


import json
import socket, socks
import traceback
import psycopg2

def index(request):
	if request.method == 'POST':

		# Connection to the DB
		connection = psycopg2.connect(database="oniongatherer", user='postgres', password='')
		
		# Extraction of website and onions address
		req = json.loads(request.read())
		website = req["website"]
		onionsPost = req["onions"]

		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
		dictionary = dict()
		q = getQueue()

		for i in range(0, len(onionsPost)):
			onion = str(onionsPost[i])

			cur = connection.cursor()
			cur.execute("select * from onions where url LIKE (%s)", [onion]);

			# Insert the tuple ((onion, website)) in the queue iff it was not there, otherwise get the current status

			if(cur.fetchall() == []):
				status = '0'
				q.put((onion, website))
				
			else:
				cur.execute("select status from onions where url LIKE (%s)", [onion]);
				status = (cur.fetchall())
				status = status[0][0]

			connection.commit()
			dictionary[onionsPost[i]] = status

		data = {}
		
		data['onions'] = dictionary
		json_data = json.dumps(data)
		connection.close()
		
	else:
		return HttpResponse("debug")

	return JsonResponse({'onions' : dictionary})
