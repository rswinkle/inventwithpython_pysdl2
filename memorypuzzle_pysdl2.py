# Memory Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com
# Released into Public Domain, fallback MIT/BSD

import random, sys

import sdl2.ext
import sdl2
from sdl2 import sdlgfx


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
	sdl2.ext.init()

	window = sdl2.ext.Window("Memory Game", size=(WINDOWWIDTH, WINDOWHEIGHT))
	window.show()
	ren = sdl2.ext.Renderer(window)

	mainBoard = getRandomizedBoard()
	revealedBoxes = generateRevealedBoxesData(False)

	firstSelection = None # stores (x, y) of first box picked
	mouse_clicked = False
	mousex = 0
	mousey = 0

	ren.clear(BGCOLOR)
	startGameAnimation(ren, mainBoard)

	running = True
	while running:
		mouse_clicked = False
		ren.clear(BGCOLOR)
		drawBoard(ren, mainBoard, revealedBoxes)

		for event in sdl2.ext.get_events():
			if event.type == sdl2.SDL_QUIT:
				running = False
				break
			elif event.type == sdl2.SDL_KEYDOWN:
				if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
					running = False
					break
			elif event.type == sdl2.SDL_MOUSEMOTION:
				mousex, mousey = event.motion.x, event.motion.y
			elif event.type == sdl2.SDL_MOUSEBUTTONUP:
				mousex, mousey = event.button.x, event.button.y
				mouse_clicked = True

		boxx, boxy = getBoxAtPixel(mousex, mousey)
		if boxx != None and boxy != None:
			# The mouse is currently over a box.
			if not revealedBoxes[boxx][boxy]:
				drawHighlightBox(ren, boxx, boxy)
			if not revealedBoxes[boxx][boxy] and mouse_clicked:
				revealBoxesAnimation(ren, mainBoard, [(boxx, boxy)])
				revealedBoxes[boxx][boxy] = True # set the box as "revealed"
				if firstSelection == None: # the current box was the first box clicked
					firstSelection = (boxx, boxy)
				else: # the current box was the second box clicked
					# Check if there is a match between the two icons.
					icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
					icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

					if icon1shape != icon2shape or icon1color != icon2color:
						# Icons don't match. Re-cover up both selections.
						sdl2.SDL_Delay(1000) # 1000 milliseconds = 1 sec
						coverBoxesAnimation(ren, mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
						revealedBoxes[firstSelection[0]][firstSelection[1]] = False
						revealedBoxes[boxx][boxy] = False
					elif hasWon(revealedBoxes): # check if all pairs found
						gameWonAnimation(ren, mainBoard)
						sdl2.SDL_Delay(2000)

						# Reset the board
						mainBoard = getRandomizedBoard()
						revealedBoxes = generateRevealedBoxesData(False)

						# Show the fully unrevealed board for a second.
						ren.clear(BGCOLOR)
						drawBoard(ren, mainBoard, revealedBoxes)
						ren.present()
						sdl2.SDL_Delay(1000)

						# Replay the start game animation.
						startGameAnimation(ren, mainBoard)
					firstSelection = None # reset firstSelection variable


		ren.present()
		sdl2.SDL_Delay(FPS)
	
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
			if x >= left and x <= left+BOXSIZE and y >= top and y <= top+BOXSIZE:
				return (boxx, boxy)
	return (None, None)



def draw_polygon(renderer, points, color):
	n_pts = len(points)
	xarray = (sdl2.Sint16 * n_pts)()
	yarray = (sdl2.Sint16 * n_pts)()

	for i in range(n_pts):
		xarray[i] = points[i][0]
		yarray[i] = points[i][1]
	#unecessary
	#xptr = ctypes.cast(xarray, ctypes.POINTER(sdl2.Sint16))
	#yptr = ctypes.cast(yarray, ctypes.POINTER(sdl2.Sint16))

	sdlgfx.filledPolygonRGBA(renderer, xarray, yarray, n_pts, *color)
	#do I need to del or somehow free the arrays here?


def drawIcon(ren, shape, color, boxx, boxy):
	quarter = int(BOXSIZE * 0.25) # syntactic sugar
	half =    int(BOXSIZE * 0.5)  # syntactic sugar

	left, top = leftTopCoordsOfBox(boxx, boxy) # get pixel coords from board coords
	# Draw the shapes
	if shape == DONUT:
		sdlgfx.filledCircleRGBA(ren.renderer, left+half, top+half, half-5, *color) 
		sdlgfx.filledCircleRGBA(ren.renderer, left+half, top+half, quarter-5, *BGCOLOR) 
	elif shape == SQUARE:
		lqrtr = left+quarter
		tqrtr = top+quarter
		sdlgfx.boxRGBA(ren.renderer, lqrtr, tqrtr, lqrtr+BOXSIZE-half, tqrtr+BOXSIZE-half, *color)
	elif shape == DIAMOND:
		pts = ((left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1), (left, top + half))
		draw_polygon(ren.renderer, pts, color)

	elif shape == LINES:
		for i in range(0, BOXSIZE, 4):
			ren.draw_line((left, top+i, left+i, top), color)
			ren.draw_line((left+i, top+BOXSIZE-1, left+BOXSIZE-1, top+i), color)
	elif shape == OVAL:
		sdlgfx.ellipseRGBA(ren.renderer, left+BOXSIZE//2, top+quarter+half//2, BOXSIZE//2, half//2, *color)


def getShapeAndColor(board, boxx, boxy):
	# shape value for x, y spot is stored in board[x][y][0]
	# color value for x, y spot is stored in board[x][y][1]
	return board[boxx][boxy][0], board[boxx][boxy][1]


def drawBoxCovers(ren, board, boxes, coverage):
	# Draws boxes being covered/revealed. "boxes" is a list
	# of two-item lists, which have the x & y spot of the box.
	for box in boxes:
		left, top = leftTopCoordsOfBox(box[0], box[1])
		ren.fill((left, top, BOXSIZE, BOXSIZE), BGCOLOR)
		shape, color = getShapeAndColor(board, box[0], box[1])
		drawIcon(ren, shape, color, box[0], box[1])
		if coverage > 0: # only draw the cover if there is an coverage
			ren.fill((left, top, coverage, BOXSIZE), BOXCOLOR)
	ren.present()
	sdl2.SDL_Delay(FPS)


def revealBoxesAnimation(ren, board, boxesToReveal):
	# Do the "box reveal" animation.
	for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
		drawBoxCovers(ren, board, boxesToReveal, coverage)


def coverBoxesAnimation(ren, board, boxesToCover):
	# Do the "box cover" animation.
	for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
		drawBoxCovers(ren, board, boxesToCover, coverage)


def drawBoard(ren, board, revealed):
	# Draws all of the boxes in their covered or revealed state.
	for boxx in range(BOARDWIDTH):
		for boxy in range(BOARDHEIGHT):
			left, top = leftTopCoordsOfBox(boxx, boxy)
			if not revealed[boxx][boxy]:
				# Draw a covered box.
				ren.fill((left, top, BOXSIZE, BOXSIZE), BOXCOLOR)
			else:
				# Draw the (revealed) icon.
				shape, color = getShapeAndColor(board, boxx, boxy)
				drawIcon(ren, shape, color, boxx, boxy)


def drawHighlightBox(ren, boxx, boxy):
	left, top = leftTopCoordsOfBox(boxx, boxy)
	ren.draw_rect((left-5, top-5, BOXSIZE+10, BOXSIZE+10), HIGHLIGHTCOLOR)


def startGameAnimation(ren, board):
	# Randomly reveal the boxes 8 at a time.
	coveredBoxes = generateRevealedBoxesData(False)
	boxes = []
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			boxes.append( (x, y) )
	random.shuffle(boxes)
	boxGroups = splitIntoGroupsOf(8, boxes)

	drawBoard(ren, board, coveredBoxes)
	for boxGroup in boxGroups:
		revealBoxesAnimation(ren, board, boxGroup)
		coverBoxesAnimation(ren, board, boxGroup)


def gameWonAnimation(ren, board):
	# flash the background color when the player has won
	coveredBoxes = generateRevealedBoxesData(True)
	color1 = LIGHTBGCOLOR
	color2 = BGCOLOR

	for i in range(13):
		color1, color2 = color2, color1 # swap colors
		ren.clear(color1)
		drawBoard(ren, board, coveredBoxes)
		ren.present()
		sdl2.SDL_Delay(300)


def hasWon(revealedBoxes):
	# Returns True if all the boxes have been revealed, otherwise False
	for i in revealedBoxes:
		if False in i:
			return False # return False if any boxes are covered.
	return True















if __name__ == '__main__':
	main()
