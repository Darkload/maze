
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
		self.path = False

		self.distance = INFINITY


	@property
	def neighbors(self):
		return [self.left, self.right, self.up, self.down]


	def __str__(self):
		return str(self.my_id)

	def __repr__(self):
		#return str(self.my_id)
		return self.render()


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
	def __init__(self, cell, path):
		self.cell = cell
		self.path = path

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
		elif cell.path:
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


		self.data = maze
		self.start = MazeCell(-1)
		self.start.right = connection(self.start,self.data[0][0])
		self.start.right.is_wall = False
		self.start.explored = True

		self.end = MazeCell(0)
		self.end.left = connection(self.end,self.data[-1][-1])
		self.end.left.is_wall = False

		#build all associations
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

		
	def buildMaze(self):
		'''
		#next build associations
		for x, column in enumerate(maze):
			for y, cell in enumerate(column):
				if x+1 < width:
					cell.right = maze[x+1][y]
				if x > 0 :
					cell.left = maze[x-1][y]
				if y+1 < height:
					cell.down = maze[x][y+1]
				if y < 0:
					cell.up = maze[x][y-1]
		'''
		self._build_func(self.start)

	'''
	#recursive? will produce dfs, bad 
	def _build_func(self,cell):
		if cell == Border:
			return

		cell.explored = True

		possibilities = []
		for neerby in cell.borders:
	'''


	def _find_frontier(self):
		# a bfs that finds the undiscovered frontier

		explored_cells = [self.start]
		undiscovered = []
		for cell in explored_cells:
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

		return undiscovered, explored_cells

	def _expand_frontier(self, undiscovered, explored_cells, last_explored):

		updated_unexplored = []
		for direction in undiscovered:
			if direction.cell is not last_explored:
				updated_unexplored.append(direction)

		explored_cells.append(last_explored)
		for way in last_explored.neighbors:
			if way:
				neighbor = way.get_neighbor(last_explored)
				if not neighbor.explored:
					updated_unexplored.append(potential_path(neighbor,way))
				elif neighbor not in explored_cells:
					explored_cells.append(neighbor)

		return updated_unexplored, explored_cells


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
			current.path = True
			for way in current.neighbors:
				if way and not way.is_wall:
					neighbor = way.get_neighbor(current)
					if neighbor.distance < best_value:
						best_value = neighbor.distance
						best_way = neighbor
			current = best_way




	def _build_func(self, start):
		

		undiscovered, explored_cells = self._find_frontier()

		count = 0
		while undiscovered:
			#print undiscovered
			if len(undiscovered) == 1:
				discovery = undiscovered[0]
			else:
				discovery = random.choice(undiscovered)
			discovery.path.is_wall = False
			discovery.cell.explored = True
			#print '!', discovery.
			#raw_input('ok')
			undiscovered, explored_cells = \
			 self._expand_frontier(undiscovered, 
			 	                 explored_cells,
			 	                  discovery.cell)
			count += 1
			if count % 20 == 0:
				self.render()



m = Maze(55,48)
#m = Maze(25,25)
#m[1][1].left = 1


m.render()
m.buildMaze()
m.render()
m.bfs()
m.render(dist=True)
m.crawler()
m.render()










	