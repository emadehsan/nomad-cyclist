import json
from datetime import datetime
from pprint import pprint


# converts the GoogleMap's distance matrix json response to a 2D list of distance between cities
def gmapMatrixTo2dList(gmapResponse):
	if gmapResponse is None or gmapResponse['status'] != 'OK':
		print('#gmapMatrixTo2dList: gmapResponse is None or status is not OK')
		return None

	rows = gmapResponse['rows']

	matrix = [] # 2d list
	for row in rows:
		matrixRow = []
		for el in row['elements']:
			if el['status'] == 'OK':
				matrixRow.append(el['distance']['value'])
			else:
				matrixRow.append(-1)
		matrix.append(matrixRow)
	return matrix

# find distance matrix (even for more than 10 locations)
def convolveAndComputeDistMatrix(points):
	# points: array contains coordinates of all the points/coords to be routed
	'''
	the process of going over the matrix
	Google Maps Matrix API has limits: https://developers.google.com/maps/documentation/distance-matrix/usage-and-billing#other-usage-limits
	* Each query sent to the Distance Matrix API generates elements, 
		where the number of origins times the number of destinations equals the number of elements.
	* Maximum of 25 origins or 25 destinations per request.
	* Maximum 100 elements per server-side request.
	'''

	mat = []

	n = len(points) # rows
	m = n # cols
	step = 10 # n*m = 10*10 = 100 which is the limit by Google Maps for Matrix API

	# '''
	# generate placeholder matrix that will store distance values
	for i in range(n):
		row = []
		for j in range(m):
			row.append(-1)
		mat.append(row)

	from pprint import pprint
	pprint(mat)
	# '''


	# now convolve over the whole matrix 
	# (like deep learning filter convolves)
	for i in range(0, n, step):
		for j in range(0, m, step):

			# indexes (representing a small square matrix)
			# included in current convolve step
			rowIndexes = []
			colIndexes = []

			# the i,j values define the boundries of small square (convolution step)
			lowerI = i
			upperI = -1
			lowerJ = j
			upperJ = -1

			if i + step < n:
				rowIndexes = list( range(i, i+step, 1) )
				print('rowIndexes', rowIndexes)

				upperI = i+step-1
			else:
				# else we might be going out of range (index out of bound)
				rowIndexes = list( range(i, n, 1) ) # the remaining rows
				print('rowIndexes', rowIndexes)

				upperI = n-1

			if j + step < m:
				colIndexes = list( range(j, j+step, 1) )
				print('colIndexes', colIndexes)

				upperJ = j+step-1
			else:
				colIndexes = list( range(j, m, 1) )
				print('colIndexes', colIndexes)

				upperJ = m-1


			# now go over rows and columns in current convolve step
			# these cols and rows are represented by rowIndexes & colIndexes
			originList = []
			for idx in rowIndexes:
				originList.append(points[idx])

			# origins must be in the format:
			# 'lat,lng|lat,lng|lat,lng'
			origins = '|'.join(originList)

			destinationList = []
			for idx in colIndexes:
				destinationList.append(points[idx])
			destinations = '|'.join(destinationList)

			# the element in this request are at max 100 (10 origins 10 destinations = 10*10 = 100)
			# which is max elements allowed in a single request

			# get distance matrix for provided origins and destinations
			gmapResponse = gmapMatrix(origins, destinations)

			saveGmapResponse(gmapResponse, lowerI, upperI, lowerJ, upperJ)
			# convert the response in to a 2d Matrix in Python
			distMat100 = gmapMatrixTo2dList(gmapResponse)

			print('distMat100')
			pprint(distMat100)

			# indexes for traversing through retrieved distance matrix
			x = 0
			y = 0
			# store values back to mat at corresponding indexes
			for rowIdx in rowIndexes:
				y = 0 # reset
				for colIdx in colIndexes:
					# TODO read from response
					print('x,y', x, y)
					mat[rowIdx][colIdx] = distMat100[x][y]

					y += 1
				x += 1

			# let's check state of mat at every update
			pprint(mat)

	return mat # complete distance matrix

def getCities():
	# locations to visit
	cities = [
		{
			"name": "Xi'an, Shaanxi, China",
			"location": [34.341576, 108.939774]
		},
		{
			"name": "Lanzhou, China",
			"location": [36.061089, 103.834305]
		},
		{
			"name": "Dunhuang, Jiuquan, China",
			"location": [40.141300,94.657936]
		},
		{
			"name": "Gaochang, Turpan, China",
			"location": [43.143360, 88.864410]
		},
		{
			"name": "Urumqi, Xinjiang, China",
			"location": [43.803399,87.607403]
		},
		{
			# (Chinese border city to Khazakhstan)
			"name": "Khorgas, Ili, Xinjiang, China",
			"location": [44.213956,80.411253]
		},
		{
			# (Khazak border city to China)
			"name": "Horgos, Қорғас, Kazakhstan",
			"location": [44.2236981,80.3839588]
		},
		{
			"name": "Almaty, Kazakhstan",
			"location": [43.272158,76.886459]
		},
		{
			"name": "Bishkek, Kyrgyzstan",
			"location": [42.884091,74.577522]
		},
		{
			"name": "Tashkent, Uzbekistan",
			"location": [41.296164,69.269102]
		},
		{
			"name": "Dushanbe, Tajikistan",
			"location": [38.562798,68.785803]
		},
		{
			"name": "Baysun, Uzbekistan",
			"location": [38.181622,67.199971]
		},
		{
			"name": "Samarqand, Uzbekistan",
			"location": [39.653592,66.977775]
		},
		{
			"name": "Bukhara, Uzbekistan",
			"location": [39.778952,64.409729]
		},
		{
			"name": "Merv, Turkmenistan",
			"location": [37.663824,62.162512]
		},
		{
			"name": "Ashgabat, Turkmenistan",
			"location": [37.954981,58.373949]
		},
		{
			"name": "Tehran, Iran",
			"location": [35.700837,51.391144]
		},
		{
			"name": "Tabriz, Iran",
			"location": [38.093347,46.276612]
		},
		{
			"name": "Ankara, Turkey",
			"location": [39.913276,32.814361]
		},
		{
			"name": "Istanbul, Turkey",
			"location": [41.022576,28.961477]
		}
	]
	return cities


def citiesToStringCoordinates(cities):
	# extracts the location from city dicts and converts them to 'lat,lng' format

	coordsAsStr = []
	for city in cities:
		strCoord = ','.join(map(str, city['location']))
		coordsAsStr.append(strCoord)

	return coordsAsStr


def getCurrentTimeAsString():
	# add current time to file name to avoid overwriting
	tm = str( datetime.now() )
	tm = tm.replace(' ', '')
	return tm


def saveGmapResponse(gmapResponse, lowerI, upperI, lowerJ, upperJ):
	# save the response to files. for debugging
	tm = getCurrentTimeAsString()

	saveTo = f'./backup/gmap-response-{lowerI}_{upperI}x{lowerJ}_{upperJ}-{tm}.json'
	jsonData = json.dumps(gmapResponse)
	
	with open(saveTo, 'w') as f:
		f.write(jsonData)


def saveCompleteDistMatrix(data):
	# saves the complete distance matrix computed from multiple requests to gmap APIs
	# to a file

	# convert distMatComplete to json
	
	jsonData = json.dumps(data)
	tm = getCurrentTimeAsString()

	saveTo = f'./backup/matrix-{tm}.json'

	with open(saveTo, 'w') as f:
		f.write(jsonData)

# loads saved distance matrix
def exampleDistanceMatrix(distMatrixFile):
	with open(distMatrixFile, 'r') as f:
		data = f.read()
		matrix = json.loads(data)
		return matrix


# a method to see the maximum & minimum values in the matrix (other than 0 & -1)
def matrixStats(matrix):
	# start with hardcoded values bcz we know that 0 & -1 values exit in the matrix
	min = 0
	max = 0
	for row in matrix:
		for el in row:
			if el > max:
				max = el

			# assign min, the first non 0, -1 value
			if min in [0, -1]:
				min = el

			if el not in [0, -1] and el < min:
				min = el

	print('min', min)
	print('max', max)