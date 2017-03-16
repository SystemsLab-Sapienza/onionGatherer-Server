import psycopg2
import subprocess
import socket, socks
import datetime
import traceback

from multiprocessing import Pool, Queue, Process

q = None

'''
	Input: urlTuple, a tuple of ((hiddenServiceAddress, website)). The website represents the one in which we gather it.
	Output: a triple ((hiddenServiceAddress, website, httpStatus))

	It allows to get the httpStatus of each hidden service
'''
def getStatus(urlTuple):
	try:
		httpStatus = subprocess.check_output(['torsocks','curl','-o','/dev/null','--silent','--write-out','%{http_code}', str(urlTuple[0])])
	except subprocess.CalledProcessError, e:
		if e.output == '000':
			httpStatus = e.output

		# TODO
		# Check the return status can only be '000'

	return ((urlTuple[0], urlTuple[1], httpStatus))

'''
	Output: the shared queue

	It allows to get the shared queue that contains the hidden service addresses to analyze
'''
def getQueue():
	global q
	if q != None:
		return q
	else:
		q = Queue()
		p = Process(target=startworker)
		p.start()
		return q


'''
	Input: 	connection, necessary in order to establish a connection to database
			array, containing the hidden services triples ((hiddenServiceAddress, website, httpStatus))

	It allows to insert the hidden service addresses into the database
'''

def insertInDatabase(connection, array):
	
	now = datetime.datetime.now()

	argsStatus = []
	for element in array:
		httpStatus = element[2]
		if(httpStatus.startswith('2') or httpStatus.startswith('3')):
			status = '1'
		else:
			status = '-1'


		argsStatus.append((element[0], element[1], status))

	records_list_template = ','.join(['%s'] * len(argsStatus))
	insertStatus = 'INSERT INTO onions (url, website, status) VALUES {0}'.format(records_list_template)
		
	with connection:
		with connection.cursor() as cur:
			try:
				cur.execute(insertStatus, argsStatus)
			except:
				print traceback.print_exc()


'''
	It allows to assign the "analyzing" - hidden services to a pool of 30 process in order to exploit the parallelization
'''
def startworker():
	connection = psycopg2.connect(database="oniongatherer", user='postgres', password='')
	p = Pool(30)
	i = 0
	array = []
	while True:
		onionTuple = q.get()
		with connection:
			with connection.cursor() as cur:
				cur.execute("SELECT * FROM onions WHERE url LIKE (%s)", [str(onionTuple[0])]);
				if cur.fetchall() == []:
					flag = False
					for tempTuple in array:
						if onionTuple[0] == tempTuple[0]:
							flag = True
					if flag == False:
						array.append((onionTuple[0], onionTuple[1]))
						i = (i + 1) % 30
						if i == 29 or q.empty() == True:
							if p == None:
								p = Pool(30)
							createPool(array, connection, p)
							array = []
							if q.empty()==True:
								p.close()
								p = None

'''
	Input: 	array, containing the hidden services triples ((hiddenServiceAddress, website, httpStatus))
			connection, necessary in order to establish a connection to database
			p, Pool of processes
'''

def createPool(array, connection, p):
	
	statuses = p.map(getStatus, array)
	insertInDatabase(connection, statuses)
