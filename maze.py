
import sys
import random

class INFINITY:
	pass

#nodes for a cell
class MazeCell:	
	def __init__(self,myd):
		self.left = None
		self.right = None
		self.up = None
		self.down = None

		self.explored = False
		self.my_id = myd
		self.is_path = False

		self.distance = INFINITY


	@property
	def neighbors(self):
		return [self.left, self.right, self.up, self.down]


	def __str__(self):
		return str(self.my_id)

	def __repr__(self):
		return str(self.my_id)
		#return self.render()

	#get a list of explored and unexplored neighbors
	def get_explored_unexplored_neighbors(self):
		unexplored_cells = []
		explored_cells = []
		for way in self.neighbors:
			if way:
				neighbor = way.get_neighbor(self)
				if not neighbor.explored:
					unexplored_cells.append(potential_path(neighbor,way))
				elif neighbor not in explored_cells:
					explored_cells.append(neighbor)

		return explored_cells, unexplored_cells


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

class potential_path:
	def __init__(self, cell, connection):
		self.cell = cell
		self.connection = connection

	def __repr__(self):
		#return str(self.my_id)
		return ""+str(self.cell.my_id)


		
class Maze:
	data = []
	width = 0
	height = 0

	def render(self, dist=False):

		sys.stdout.write(' ')
		for x in range(0,m.width):
			sys.stdout.write('_ ')
		sys.stdout.write('\n')


		for y in range(0,m.height):
			sys.stdout.write('|')

			for x in range(0,m.width):
				m._render_cell(x,y,dist)


	def _render_cell(self,x,y,dist=False):
		cell = self.data[x][y]

		if dist:
			sys.stdout.write(str(cell.distance))
		elif cell.is_path:
			sys.stdout.write('@')
		elif not cell.explored:
			sys.stdout.write('#')
		elif self.height-1 == y:
			sys.stdout.write('_')
		elif not cell.down.is_wall:
			sys.stdout.write(' ')
		else:
			sys.stdout.write('_')

		if self.width-1 == x:
			sys.stdout.write('|')
			sys.stdout.write('\n')
		elif not cell.right.is_wall:
			sys.stdout.write(' ')
		else:
			sys.stdout.write('|')

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
		self.start.right = connection(self.start,self.data[0][0])
		self.start.right.is_wall = False
		self.start.explored = True

		self.end = MazeCell(0)
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





	def _find_frontier(self):
		# a modified bsf that finds the undiscovered frontier

		explored_cells = [self.start]
		explored_cells_hash = {self.start:1}
		undiscovered = []
		for cell in explored_cells:
			#print explored_cells, undiscovered, cell

			new_explored, new_unexplored = \
			  cell.get_explored_unexplored_neighbors()

			#print new_explored, new_unexplored
			undiscovered += new_unexplored
			for seen in new_explored:
				if seen not in explored_cells_hash:
					explored_cells += new_explored
					explored_cells_hash[seen] = 1
			#print len(explored_cells), len(undiscovered)
			'''
			for way in cell.neighbors:
				if way:
					neighbor = way.get_neighbor(cell)
					#print name, way
					if not neighbor.explored:
						#print '2', neighbor, way
						undiscovered.append(potential_path(neighbor,way))
					elif neighbor not in explored_cells:
						#print '1',neighbor
						explored_cells.append(neighbor)
			'''

		return undiscovered, explored_cells

	#a modification to the find frontier function to greatly improve speed
	# by a factor of N! over time
	def _expand_frontier(self, undiscovered, last_explored):

		updated_unexplored = []
		for direction in undiscovered:
			if direction.cell is not last_explored:
				updated_unexplored.append(direction)

		_, new_unexplored = \
			  last_explored.get_explored_unexplored_neighbors()

		#updated_unexplored = list_union(new_unexplored, updated_unexplored)
		updated_unexplored += new_unexplored

		'''
		print len(updated_unexplored)
		for way in last_explored.neighbors:
			if way:
				neighbor = way.get_neighbor(last_explored)
				if not neighbor.explored:
					updated_unexplored.append(potential_path(neighbor,way))
		'''

		return updated_unexplored


	def bfs(self):

		explored_cells = [self.start]
		self.start.distance = 1

		for cell in explored_cells:
			for way in cell.neighbors:
				if way and not way.is_wall:
					neighbor = way.get_neighbor(cell)

					if neighbor.distance is INFINITY:
						neighbor.distance = cell.distance + 1
						if neighbor not in explored_cells:
							explored_cells.append(neighbor)

					elif neighbor.distance < cell.distance + 1:
						cell.distance = neighbor.distance + 1

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


	def build_course(self):

		self._build_course(self.start)

	def _build_course(self, start, show_progress=True):
		

		undiscovered, explored_cells = self._find_frontier()

		count = 0
		while undiscovered:
			#print undiscovered
			#undiscovered_set = set(undiscovered)
			#discovery = random.choice(tuple(undiscovered_set))
			discovery = random.choice(undiscovered)
			discovery.connection.is_wall = False
			discovery.cell.explored = True
			#print '!', discovery.
			#raw_input('ok')
			#undiscovered, _ = self._find_frontier()
			undiscovered = self._expand_frontier(undiscovered, discovery.cell)
			#raw_input('go?')
			count += 1
			#print count
			if count % 50 == 0 and show_progress:
				self.render()
				#time.sleep(.05)
		


import time
m = Maze(55,48)
#m = Maze(25,25)
#m[1][1].left = 1


m.render()
t1 = time.time()
m.build_course()
t2 = time.time()
m.render()
print t1-t2
'''
m.render()
m.bfs()
m.render(dist=True)
m.crawler()
m.render()
'''









	