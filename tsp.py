# based on https://github.com/sgkruk/Apress-AI
# Apress-AI/tsp.py

from random import randint,uniform
from math import sqrt

from tsp_helpers import ObjVal, SolVal, newSolver

# Euclidean Distance between given points (but multiplied by 10 to get a bigger value)
def dist(p1,p2):
  return int(round( 10 * sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) ))

def gen_data(n):

  # generate random pair of points like [(2, 31), (75, 83), ... n times]
  points = [(randint(1,100), randint(1,100)) for i in range(n)]

  # 2D array of n*n with None values
  R = [[None for i in range(n)] for j in range(n)]

  for i in range(n):
    for j in range(n):
      perturb = uniform(0.8,1.2)

      if i != j and perturb > 0:
        # slightly update the Euclidean Distance betwen thse points by multiply then with a uniform(0.8,1.2)
        R[i][j] = int( dist(points[i],points[j]) * perturb)

  return R,points


# if provided, also eliminiates mentioned (unwanted) subtours from solution
def solve_model_eliminate(D,Subtours=[]):
  # solver
  s = newSolver('TSP', True)
  # number of cities
  n = len(D) # number of rows which is actually equal to number of cities

  # x[i][j] will be allowed to have a value between 0 & 0 if D[i][j] is None
  # else x[i][j] will be allowed to have an integer value between 0 & 1
  x = [[s.IntVar(0, 0 if D[i][j] is None else 1, '') \
        for j in range(n)] for i in range(n)] 
  
  # add constraints
  for i in range(n):  
    # in i-th row, only one element can be used in the tour
    s.Add(1 == sum(x[i][j] for j in range(n))) 
    # in j-th column, only one element can be used in the tour
    s.Add(1 == sum(x[j][i] for j in range(n))) 
    # a city must not be assigned a path to itself in the tour
    s.Add(0 == x[i][i])

  for sub in Subtours:
    K = [x[sub[i]][sub[j]]+x[sub[j]][sub[i]]\
         for i in range(len(sub)-1) for j in range(i+1,len(sub))]
    
    s.Add(len(sub)-1 >= sum(K))

  # minimize the total distance of the tour
  s.Minimize(s.Sum(x[i][j]*(0 if D[i][j] is None else D[i][j]) \
                   for i in range(n) for j in range(n))) 
  rc = s.Solve()
  tours = extract_tours(SolVal(x),n) 
  return rc,ObjVal(s),tours


def extract_tours(R,n):
#   print('Inside: extract_tours')
#   print('n:', n)
#   pprint(R)
  # starting node
  node = 0

  # list of lists. each inner list is a tour
  tours = [[0]]

  # [0, 1, 1, 1. ...], len(allnodes) = n
  # 0 value represents node has been visited, 
  # 1 represents that i-th node is yet to be visited
  allnodes = [0]+[1]*(n-1)

  # while there is still unvisited nodes:
  while sum(allnodes) > 0:
    
    # add i-th node from Route to next nodes to be visited
    # if current node and i-th node are CONNECTED?
    # assign first value of these next to be visted nodes to "next"
    # next = [i for i in range(n) if R[node][i]==1][0]

    # OR
    # from all the next nodes for current node, pick first one
    nextNodes = [i for i in range(n) if R[node][i]==1]
    # print('nextNodes: ')
    # pprint(nextNodes)
    next = nextNodes[0]

    # if next node to be visited is not part of our latest tour
    if next not in tours[-1]:
      # add next node to our latest/current tour
      tours[-1].append(next)
      # make next, the current node
      node = next

    else:
      # else, pick the next node to as a starting node
      node = allnodes.index(1)
      # add a tour, with this node as starting point
      tours.append([node])

    # now, mark this node as visited
    allnodes[node] = 0


  return tours

# returns a closed tour/path
def solve_model(D):
  subtours,tours = [],[]

  while len(tours) != 1:
    rc, Value, tours = solve_model_eliminate(D,subtours)
  
    # status
    if rc == 0:
      subtours.extend(tours)

  return rc,Value,tours[0]


# instead of a closed tour, return a simple path covering all vertices
def solve_model_p(D):
  n = len(D)
  n1 = len(D)+1 # add another point to points list

  # add another point to points distance matrix D which is 0 distance away from other points
  # new distance matrix will be E
  # this new point is added at the end of every row & column
  E = [[0 if n in (i,j) else D[i][j] \
    for j in range(n1)] for i in range(n1)]

  rc,Value,tour = solve_model(E)
  i = tour.index(n)
  path = [tour[j] for j in range(i+1,n1)]+\
         [tour[j] for j in range(i)]
  return rc,Value,path


# allow repeated visits. can visit a node multiple times
def solve_model_star(D):
  import shortest_path
  n = len(D)
  Paths, Costs = shortest_path.solve_all_pairs(D)
  rc,Value,tour = solve_model(Costs)
  Tour=[]
  for i in range(len(tour)):
    Tour.extend(Paths[tour[i]][tour[(i+1) % len(tour)]][0:-1])
  return rc,Value,Tour
