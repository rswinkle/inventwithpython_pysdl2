# Memory Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com

import random, sys

import sdl2.ext
import sdl2


FPS = 30 # frames per second, the general speed of the program
WINDOWWIDTH = 640 # size of window's width in pixels
WINDOWHEIGHT = 480 # size of windows' height in pixels
REVEALSPEED = 8 # speed boxes' sliding reveals and covers
BOXSIZE = 40 # size of box height & width in pixels
GAPSIZE = 10 # size of gap between boxes in pixels
BOARDWIDTH = 10 # number of columns of icons
BOARDHEIGHT = 7 # number of rows of icons
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)


#                          R    G    B
GRAY     = sdl2.ext.Color(100, 100, 100)
NAVYBLUE = sdl2.ext.Color( 60,  60, 100)
WHITE    = sdl2.ext.Color(255, 255, 255)
RED      = sdl2.ext.Color(255,   0,   0)
GREEN    = sdl2.ext.Color(  0, 255,   0)
BLUE     = sdl2.ext.Color(  0,   0, 255)
YELLOW   = sdl2.ext.Color(255, 255,   0)
ORANGE   = sdl2.ext.Color(255, 128,   0)
PURPLE   = sdl2.ext.Color(255,   0, 255)
CYAN     = sdl2.ext.Color(  0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of shapes/colors defined."


def main():
	global FPSCLOCK, DISPLAYSURF

	sdl2.ext.init()


	window = sdl2.ext.Window("Memory Game", size=(WINDOWWIDTH, WINDOWHEIGHT))
	window.show()
	renderer = sdl2.ext.Renderer(window)

	mainBoard = getRandomizedBoard()
	revealdBoxes = generateRevealedBoxesData(False)

	firstSelection = None # stores (x, y) of first box picked

	running = True
	while running:
		for event in sdl2.ext.get_events():
			if event.type == sdl2.SDL_QUIT:
				running = False
				break
			elif event.type == sdl2.SDL_KEYDOWN:
				if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
					running = False
					break

		renderer.clear(BGCOLOR)
		drawBoard(mainBoard, revealedBoxes)

	sdl2.ext.quit()


def generateRevealedBoxesData(val):
	revealedBoxes = []
	for i in range(BOARDWIDTH):
		revealedBoxes.append([val] * BOARDHEIGHT)
	return revealedBoxes

def getRandomizedBoard():
	# Get a list of every possible shape in every possible color.
	icons = []
	for color in ALLCOLORS:
		for shape in ALLSHAPES:
			icons.append( (shape, color) )

	random.shuffle(icons) # randomize the order of the icons list
	numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2) # calculate how many icons are needed
	icons = icons[:numIconsUsed] * 2 # make two of each
	random.shuffle(icons)

	# Create the board data structure, with randomly placed icons.
	board = []
	for x in range(BOARDWIDTH):
		column = []
		for y in range(BOARDHEIGHT):
			column.append(icons[0])
			del icons[0] # remove the icons as we assign them
		board.append(column)
	return board


def splitIntoGroupsOf(groupSize, theList):
	# splits a list into a list of lists, where the inner lists have at
	# most groupSize number of items.
	result = []
	for i in range(0, len(theList), groupSize):
		result.append(theList[i:i + groupSize])
	return result


def leftTopCoordsOfBox(boxx, boxy):
	# Convert board coordinates to pixel coordinates
	left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
	top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
	return (left, top)


def getBoxAtPixel(x, y):
	for boxx in range(BOARDWIDTH):
		for boxy in range(BOARDHEIGHT):
			left, top = leftTopCoordsOfBox(boxx, boxy)
			boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
			if x >= left and x <= left+BOXSIZE and y >= top and y <= top+BOXSIZE:
				return (boxx, boxy)
	return (None, None)















if __name__ == '__main__':
	main()
