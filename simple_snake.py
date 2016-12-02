
import random, pygame, sys, ctypes
from pygame.locals import *


FPS = 30
CELL_SIZE = 20
CELLS_WIDE = 32
CELLS_HIGH = 24

GRID = []
for x in range(CELLS_WIDE):
	GRID.append([None] * CELLS_HIGH)

# Constants for some colors.
#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK             # color to use for the background of the grid
GRID_LINES_COLOR = DARKGRAY # color to use for the lines of the grid

# Calculate total pixels wide and high that the full window is
WINDOWWIDTH = CELL_SIZE * CELLS_WIDE
WINDOWHEIGHT = CELL_SIZE * CELLS_HIGH

TARGET = [-1,-1]
TARGET_COLOR = WHITE

snake = None
SNAKE_LEN = 4

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0
BUTT = -1


class Worm():
	def __init__(self, name='Worm', color=None, speed=None):
		self.name = name
		self.maxsize = SNAKE_LEN

		if color is None:
			self.color = WHITE
		else:
			self.color = color

		if speed is None:
			self.speed = random.randint(20, 500)
		else:
			self.speed = speed

		startx, starty = getRandPos()
		self.body = [{'x': startx, 'y': starty}]
		GRID[startx][starty] = self.color

		self.direction = random.choice((UP, DOWN, LEFT, RIGHT))

		for x in range(SNAKE_LEN-1):
			nextx, nexty = self.getNextPosition(True)
			while nextx in (-1, CELLS_WIDE) or nexty in (-1, CELLS_HIGH) or GRID[nextx][nexty] is not None:
				self.direction = random.choice((UP, DOWN, LEFT, RIGHT))
				nextx, nexty = self.getNextPosition(True)
			self.body.append({'x':nextx, 'y':nexty})
			GRID[nextx][nexty] = self.color

		self.body.reverse()

	def autoRun(self):
		if random.randint(0, 100) < 20:
		    self.direction = random.choice((UP, DOWN, LEFT, RIGHT))
		nextx, nexty = self.getNextPosition()
		if nextx in (-1, CELLS_WIDE) or nexty in (-1, CELLS_HIGH) or GRID[nextx][nexty] is not None:
			self.direction = self.getNewDirection()
			if self.direction is not None:
				nextx, nexty = self.getNextPosition()
		if self.direction is not None:
			self.moveTo(nextx, nexty)
		else:
			self.direction = random.choice((UP, DOWN, LEFT, RIGHT))
		pygame.time.wait(self.speed)

	def moveTo(self, x, y):
		GRID[x][y] = self.color
		self.body.insert(0, {'x': x, 'y': y})
		if len(self.body) > self.maxsize:
			GRID[self.body[BUTT]['x']][self.body[BUTT]['y']] = None
			del self.body[BUTT]

	def simpleRun(self):
		nextx, nexty = self.getNextPosition()

		# eat the Target
		if nextx == TARGET[0] and nexty == TARGET[1]:
			GRID[nextx][nexty] = self.color
			self.body.insert(0, {'x': nextx, 'y': nexty})
			randTarget()
			return True

		if nextx in (-1, CELLS_WIDE) or nexty in (-1, CELLS_HIGH) or GRID[nextx][nexty] is not None:
			gameOver()
			return False

		self.moveTo(nextx, nexty)

		pygame.time.wait(self.speed)
		return True

	def autoFind(self):
		pass

	def getSimplePath(self):
		pass

	def getNextPosition(self, init=False):
		pos = init and len(self.body)-1 or HEAD
		if self.direction == UP:
			nextx = self.body[pos]['x']
			nexty = self.body[pos]['y'] - 1
		elif self.direction == DOWN:
			nextx = self.body[pos]['x']
			nexty = self.body[pos]['y'] + 1
		elif self.direction == LEFT:
			nextx = self.body[pos]['x'] - 1
			nexty = self.body[pos]['y']
		elif self.direction == RIGHT:
			nextx = self.body[pos]['x'] + 1
			nexty = self.body[pos]['y']
		else:
			assert False, 'Bad value for self.direction: %s' % self.direction

		return nextx, nexty

	def getNewDirection(self):
		x = self.body[HEAD]['x']
		y = self.body[HEAD]['y']

		newDirection = []
		if y - 1 not in (-1, CELLS_HIGH) and GRID[x][y - 1] is None:
			newDirection.append(UP)
		if y + 1 not in (-1, CELLS_HIGH) and GRID[x][y + 1] is None:
			newDirection.append(DOWN)
		if x - 1 not in (-1, CELLS_WIDE) and GRID[x - 1][y] is None:
			newDirection.append(LEFT)
		if x + 1 not in (-1, CELLS_WIDE) and GRID[x + 1][y] is None:
			newDirection.append(RIGHT)

		if newDirection == []:
			return None

		return random.choice(newDirection)


def main():
	global FPSCLOCK, DISPLAYSURF
	global snake

	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption('SnakeAI')
	
	randTarget()

	snake = Worm(name='Snake', speed=100)

	while True:
		# snake.autoRun()
		
		if not snake.simpleRun():
			break

		handleEvents()
		drawGrid()

		pygame.display.update()
		FPSCLOCK.tick(FPS)

def getRandPos():
	while True:
		x = random.randint(0, CELLS_WIDE - 1)
		y = random.randint(0, CELLS_HIGH - 1)
		if GRID[x][y] is None:
			return x, y

def randTarget():
	x, y = getRandPos()
	TARGET[0], TARGET[1] = x, y
	TARGET_COLOR = (random.randint(60, 255), random.randint(60, 255), random.randint(60, 255))
	GRID[x][y] = TARGET_COLOR

def gameOver():
	ctypes.windll.user32.MessageBoxA(0, "Don't lose heart, try it again", 'Game Over', 0)

def handleEvents():
	for event in pygame.event.get(): # event handling loop
		if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
			pygame.quit()
			sys.exit()
		elif event.type == KEYDOWN:
			handleControl(event)

def handleControl(event):
	if event.key == K_UP:
		snake.direction = UP
	elif event.key == K_DOWN:
		snake.direction = DOWN
	elif event.key == K_LEFT:
		snake.direction = LEFT
	elif event.key == K_RIGHT:
		snake.direction = RIGHT

def drawGrid():
	DISPLAYSURF.fill(BGCOLOR)
	for x in range(0, WINDOWWIDTH, CELL_SIZE):
		pygame.draw.line(DISPLAYSURF, GRID_LINES_COLOR, (x, 0), (x, WINDOWHEIGHT))
	for y in range(0, WINDOWHEIGHT, CELL_SIZE):
		pygame.draw.line(DISPLAYSURF, GRID_LINES_COLOR, (0, y), (WINDOWWIDTH, y))

	for x in range(0, CELLS_WIDE):
		for y in range(0, CELLS_HIGH):
			if GRID[x][y] is None:
				continue

			color = GRID[x][y]

			darkerColor = (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 50, 0))
			pygame.draw.rect(DISPLAYSURF, darkerColor, (x * CELL_SIZE,     y * CELL_SIZE,     CELL_SIZE,     CELL_SIZE    ))
			pygame.draw.rect(DISPLAYSURF, color,       (x * CELL_SIZE + 4, y * CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8))



if __name__ == '__main__':
	main()
