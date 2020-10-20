# import requests
from pprint import pprint
import traceback
import json
from datetime import datetime
import ortools
import pandas as pd


from tsp_helpers import ObjVal, SolVal, newSolver

from distance_matrix import getCities, exampleDistanceMatrix

from tsp import solve_model_p

# path: list of city indecies
def calcPathStats(D, path, cityNames, cityIndexOffset=0):
    # number of cities
    n = len(D) 
    # output table
    table = []
    distance = ['Distance', 0]
    totalDistance = ['Cumulative', 0]
    citiesVisited = ['Cities:']

    for cityIdx in path:
        citiesVisited.append( cityNames[cityIdx + cityIndexOffset] )

    for i in range(n-1):
        distance.append( D[path[i]][path[(i+1)]] )
        totalDistance.append( totalDistance[-1] + distance[-1] )
    
    if cityIndexOffset > 0:
        path = [p + cityIndexOffset for p in path]
        
    table.append(['City Index'] + path)
    table.append(distance)
    table.append(totalDistance)
    
    return table, citiesVisited


# prints the route to take as a table including some stats
def printPath(table, citiesVisited):
    # create a dataframe for easy printing. set city names as headings of columns
    dfDisplay = pd.DataFrame(table, columns=citiesVisited) 
    print(dfDisplay.to_string(index=False))
    print('\n')

def run(distMatrixFile):
    distMat = exampleDistanceMatrix(distMatrixFile)

    print('Distance Matrix size:', len(distMat), 'x', len(distMat[0]), '\n')
    
    # cities and their coordinates
    cities = getCities()
    # get city names as a list
    cityNames = [c['name'] for c in cities]

    print("Original City Names:", cityNames, '\n')

    # cityNames conains country names too. remove those for sake simplicity
    cityNames = [name.split(',')[0] for name in cityNames]

    print('City Names:', cityNames, '\n')

    # convert distance matrix 2d list to pandas dataframe 
    # for easy manipulation of data
    df = pd.DataFrame(distMat)

    print('Distance Matrix:')
    print(df, '\n')

    # assign the headers of our dataframe the name of corrosponding cities
    df.columns = cityNames
    df.index = cityNames

    print('Distance Matrix with headings:')
    print(df, '\n')

    # the distances are in meters (as returned by Google Maps APIs)
    # convert distances in meters to kilometers
    df[df > 0 ] = round(df / 1000)

    print('Distance Matrix (km):')
    print(df, '\n')

    # our distance matrix has some entries as -1, 
    # these are entries for which gmaps didn't return a distance, so we don't know the distance 
    # to tackle this issue, we are going to divide our distance matrix in 2 parts
    # matrix A for first part of cities among which all distances are known
    # matrix B for second part of cities among which all distances are not known
    # we will solve both of these matrices separately and 
    # will connect the path end of matrix A to path start city of matrix B

    # matrix A will have first 6 cities
    dfA = df.iloc[:6, :6]

    # distance matrix A as 2d list
    DA = dfA.values.tolist()

    print('Distance Matrix A:')
    pprint(DA)
    print('\n')

    # let's find shortest route
    # model_p: find an open tour that visits all nodes in shortest way possible
    rc, Value, pathA = solve_model_p(DA)
    
    # let's print the route taken in detail
    print('Shortest Path for Part A of tour:')
    table, citiesVisitedA = calcPathStats(DA, pathA, cityNames)
    printPath(table, citiesVisitedA)

    # from the above path provided by our algorithm, we can observe that
    # the path is indeed a shortest one, 
    # but when we put it on a map, it is traveling from west to east
    # we want to travel from east to west. so let's just simply reverse the path
    # it might increase our distance a little bit, but that would be minimal bcz: same cities, reverse order
    newPathA = pathA.copy()
    newPathA.reverse()

    # let's look at the path and verify
    print('[East -> West] Shortest Path for Part A of tour:')
    table, citiesVisitedA = calcPathStats(DA, newPathA, cityNames)
    printPath(table, citiesVisitedA)

    
    # now, let's solve for 2nd part of the tour:
    # matrix B will have remaining 14 cities
    dfB = df.iloc[6:, 6:]

    # distance matrix A as 2d list
    DB = dfB.values.tolist()

    print('Distance Matrix B:')
    pprint(DB)
    print('\n')

    # let's find shortest route
    # model_p: find an open tour that visits all nodes in shortest way possible
    rc, Value, pathB = solve_model_p(DB)

    # pathB contains values like 0, 1, 3 as city indexes. 
    # but in the whole path, it's 0 value must be 0+6, 1 must be 1+6
    # that's because for distance matrix DB, values were take from 6 index forward
    # to compensate for that, use cityIndexOffset = 6
    # let's print the route taken in detail
    print('Shortest Path for Part B of tour:')
    table, citiesVisitedB = calcPathStats(DB, pathB, cityNames, cityIndexOffset=6)
    printPath(table, citiesVisitedB)

    # path for tour B is also shortest, but it is again from West -> East. We want East -> West
    newPathB = pathB.copy()
    newPathB.reverse()

    # let's look at the path and verify
    print('[East -> West] Shortest Path for Part B of tour:')
    table, citiesVisitedB = calcPathStats(DB, newPathB, cityNames, cityIndexOffset=6)
    printPath(table, citiesVisitedB)

    # now we have shortest paths in 2 parts. let's combine them
    wholePath = newPathA + [ p+6 for p in newPathB ]

    D = df.values.tolist()

    print('Shortest Path for our Cycling Tour:')
    # instead of D we can use distMat variable too, but that is in meters
    table, citiesVisited = calcPathStats(D, wholePath, cityNames) # distMat was the original distance matrix
    printPath(table, citiesVisited)

    return wholePath

if __name__ == "__main__":
    distMatrixFile = './data/matrix-2020-10-0816:22:43.952927.json'
    run(distMatrixFile)
