
'''
A maze generator and solver

The maze is generated using a tree graph that expands until it fills the given
area, allowing for guaranteed solves

The maze is solved using dijkstras
'''


import sys
import random
import time

class INFINITY:
	pass

'''
A single cell in the maze. They function as both a node in a tree as well
as a cell in the maze with an cordinate.
'''
class MazeCell:	
	def __init__(self,myd):
		#neighbors, used for navigation
		self.left = None
		self.right = None
		self.up = None
		self.down = None

		self.explored = False
		self.my_id = myd

		#for dijkstra
		self.distance = INFINITY
		self.is_path = False

	#allows for easy iteration and concationation of neighbors
	@property
	def neighbors(self):
		return [self.left, self.right, self.up, self.down]

	def __str__(self):
		return str(self.my_id)

	def __repr__(self):
		return str(self.my_id)

	#get a list of explored and unexplored neighbors
	def _get_explored_unexplored_neighbors(self, get_explored=True):
		cells = []
		for way in self.neighbors:
			if way:
				neighbor = way.get_neighbor(self)
				if not neighbor.explored and get_explored is False:
					cells.append(potential_path(neighbor,way))
				elif neighbor.explored and get_explored is True:
					cells.append(neighbor)
		return cells

	def get_explored_neighbors(self):
		return self._get_explored_unexplored_neighbors(get_explored=True)

	def get_unexplored_neighbors(self):
		return self._get_explored_unexplored_neighbors(get_explored=False)

#A connection between maze cells. allows for walls between neighbors
class connection:
	def __init__(self, a, b):
		self.is_wall = True
		self.nodes = [a,b]

	def get_neighbor(self, node):
		if node not in self.nodes:
			return None
		if self.nodes[0] == node:
			return self.nodes[-1]
		else:
			return self.nodes[0]

#A wrapper around a path and a direction, so a newly explored
#  node knows where it came from
class potential_path:
	def __init__(self, cell, connection):
		self.cell = cell
		self.connection = connection

	def __repr__(self):
		return ""+str(self.cell.my_id)
		

'''
The maze object is a rectangular container of maze cells. The maze is in
charge of creating the cells, and the connections between them. It also
allows for the creation of a solvable maze and has a function to solve the maze
It can render itself as well
'''
class Maze:
	data = []
	width = 0
	height = 0

	def render(self, dist=False):
		output = ''
		output += ' '
		for x in range(0,self.width):
			output += '_ '
		output += '\n'

		for y in range(0,self.height):
			output += '|'
			for x in range(0,self.width):
				output += self._render_cell(x,y,dist)
		return output

	#you cant have cells render themselves because they dont know
	# where walls or boundaries are
	def _render_cell(self,x,y,dist=False):
		cell = self.data[x][y]
		output = ''

		if dist:
			output += str(cell.distance)
		elif cell.is_path:
			output += '@'
		elif not cell.explored:
			output += '#'
		elif self.height-1 == y:
			output += '_'
		elif not cell.down.is_wall:
			output += ' '
		else:
			output += '_'

		if self.width-1 == x:
			output += '|'
			output += '\n'
		elif not cell.right.is_wall:
			output += ' '
		else:
			output += '|'

		return output

	'''
	  Builds up the maze base.
		This creates all the cells, endpoints, and sets the 
		neighbors and connections for all the cells
	'''
	def __init__(self, width, height):

		#first define the maze
		maze = []
		self.width = width
		self.height = height
		count = 1
		for x in range(0,width):
			column = []
			for y in range(0,height):
				column.append(MazeCell(count))
				count += 1

			maze.append(column)

		#set start and endpoints of the maze
		self.data = maze
		self.start = MazeCell(-1)
		#self.start.right = connection(self.start,self.data[0][int(height/2)])
		self.start.right = connection(self.start,self.data[0][0])
		self.start.right.is_wall = False
		self.start.explored = True

		self.end = MazeCell(0)
		#self.end.left = connection(self.end,self.data[-1][int(height/2)])
		self.end.left = connection(self.end,self.data[-1][-1])
		self.end.left.is_wall = False

		#generate connections between nodes
		for x, column in enumerate(self.data):
			for y, cell in enumerate(column):
				if x+1 < self.width:
					cell.right = connection(cell,self.data[x+1][y])
					self.data[x+1][y].left = cell.right
				if x > 0 :
					cell.left = connection(cell,self.data[x-1][y])
					self.data[x-1][y].right = cell.left
				if y+1 < self.height:
					cell.down = connection(cell,self.data[x][y+1])
					self.data[x][y+1].up = cell.down
				if y < 0:
					cell.up = connection(cell,self.data[x][y-1])
					self.data[x][y-1].down = cell.up

	'''
	  A graph search that expands outward from the start to find all the
		unexplored leafs
	'''
	def _find_frontier(self):
		explored_cells_list = [self.start]
		explored_cells_hash = {self.start:1}
		undiscovered = []
		for cell in explored_cells_list:

			new_explored = cell.get_explored_neighbors()
			new_unexplored = cell.get_unexplored_neighbors()

			undiscovered += new_unexplored
			for seen in new_explored:
				if seen not in explored_cells_hash:
					explored_cells_list += new_explored
					explored_cells_hash[seen] = 1

		return undiscovered, explored_cells_list

	'''
	  After each expansion of the maze, we are left with a list of previous
		cells that the maze could have expanded to and the a newly explored
		location. By expanding the list of unexplored places (frontier) with
		the last explored place, we dont have to re traverse the graph to find
		the next list of choices, allowing for a nice preformance boost

	'''
	def _expand_frontier(self, undiscovered, last_explored):
		updated_unexplored = []
		for direction in undiscovered:
			if direction.cell is not last_explored:
				updated_unexplored.append(direction)

		new_unexplored = last_explored.get_unexplored_neighbors()

		updated_unexplored += new_unexplored

		return updated_unexplored

	#solves a maze. This assumes it is properly built.
	def solve_maze(self):
		self.dijkstra()
		self.crawler()

    #Markes cell of a maze using dijkstras
	def dijkstra(self):

		#the hash will allow for a huge (~2000x) speed reduction
		# but it relies on the ids. Safer to use something less
		# dev alterable (time stamp or pythons internal object id?)
		explored_cells_list = [self.start]
		explored_cells_hash = {}
		explored_cells_hash[self.start.my_id] = 1
		self.start.distance = 1

		for cell in explored_cells_list:
			for way in cell.neighbors:
				if way and not way.is_wall:
					neighbor = way.get_neighbor(cell)

					if neighbor.distance is INFINITY:
						neighbor.distance = cell.distance + 1
						if neighbor.my_id not in explored_cells_hash:
							explored_cells_list.append(neighbor)
							explored_cells_hash[neighbor.my_id] = 1

					elif neighbor.distance < cell.distance + 1:
						cell.distance = neighbor.distance + 1

	#Crawls through the maze marked with dijkstra, and finds the shortest path
	#  it just gives if it cant find anything to avoid errors
	def crawler(self):
		current = self.end

		while current:
			best_way = None
			best_value = current.distance
			current.is_path = True
			for way in current.neighbors:
				if way and not way.is_wall:
					neighbor = way.get_neighbor(current)
					if neighbor.distance < best_value:
						best_value = neighbor.distance
						best_way = neighbor
			current = best_way

	'''
	The maze starts off as a bunch of unexplored cells. To connect the cells
      The list of unexplored cells surrounding explored cells is found 
      ie the 'frontier', and a random cell is choosen to be explored.
	'''
	def build_course(self, show_progress=True):
		start = self.start #the pre explored start
		undiscovered, explored_cells = self._find_frontier()

		count = 0
		while undiscovered:
			discovery = random.choice(undiscovered)
			discovery.connection.is_wall = False
			discovery.cell.explored = True

			undiscovered = self._expand_frontier(undiscovered, discovery.cell)
			
			#just for rendering
			count += 1
			if count % 30 == 0 and show_progress:
				print self.render()
		
	def __repr__(self):
		return self.render()



try:
	print 'Hi! This program will build and solve a maze!'
	height = int(raw_input('How tall should the maze be? (#)  '))
	width = int(raw_input('How wide should the maze be? (#)  '))

except ValueError:
	print "Sorry, I couln't read those numbers, using defaults"
	height = 40
	width = 55

render_mazes = False
show = raw_input('Should I render the process? (y/n) ')
if show == 'y':
	render_mazes = True
elif show == 'n':
	render_mazes = False
else:
	print "I couldnt understand you, using default"
	render_mazes = True


amazing = Maze(width,height)

t1 = time.time()
amazing.build_course(show_progress = render_mazes)
t2 = time.time()
build_time = t2-t1

print '\n\nFinished maze:'
print amazing
t1 = time.time()
amazing.solve_maze()
t2 = time.time()
solver_time = t2-t1
print '\n\nSolved maze:'
print '(The start is at the top left and the end at the bottom right)'
print amazing

print "Time to build maze: ", build_time 
print "Time to solve maze: ", solver_time 
print 'Bye!'








	