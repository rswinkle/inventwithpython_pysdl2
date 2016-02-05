# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com
# Released into Public Domain, fallback MIT/BSD

import sdl2.ext
import sdl2
from sdl2 import sdlgfx

import random, sys
from utils import sysfont

# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 4  # number of columns in the board
BOARDHEIGHT = 4 # number of rows in the board
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None
NUMSLIDES = 20


#                              R    G    B
BLACK =         sdl2.ext.Color(  0,   0,   0)
WHITE =         sdl2.ext.Color(255, 255, 255)
BRIGHTBLUE =    sdl2.ext.Color(  0,  50, 255)
DARKTURQUOISE = sdl2.ext.Color(  3,  54,  73)
GREEN =         sdl2.ext.Color(  0, 204,   0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
	#cause I don't want to pass these around
	global REN, SPRITE_FACTORY, SPRITE_RENDERER
	global RESET_BUTTON, NEW_BUTTON, SOLVE_BUTTON


	sdl2.ext.init()

	window = sdl2.ext.Window("Slide Puzzle", size=(WINDOWWIDTH, WINDOWHEIGHT))
	REN = sdl2.ext.Renderer(window)
	window.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = sdl2.ext.FontManager(font_file, size=BASICFONTSIZE)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	SPRITE_FACTORY = sdl2.ext.SpriteFactory(renderer=REN, fontmanager=font_manager, free=True)
	SPRITE_RENDERER = SPRITE_FACTORY.create_sprite_render_system(window)


	RESET_BUTTON, reset_rect = make_text(SPRITE_FACTORY, "Reset", WINDOWWIDTH - 120, WINDOWHEIGHT - 90, bg_color=TILECOLOR)
	NEW_BUTTON, new_rect = make_text(SPRITE_FACTORY, "New Game", WINDOWWIDTH - 120, WINDOWHEIGHT - 60, bg_color=TILECOLOR)
	SOLVE_BUTTON, solve_rect = make_text(SPRITE_FACTORY, "Solve", WINDOWWIDTH - 120, WINDOWHEIGHT - 30, bg_color=TILECOLOR)


	mainBoard, solutionSeq = generateNewPuzzle(NUMSLIDES)
	SOLVEDBOARD = getStartingBoard() # a solved board is the same as the board in a start state.
	allMoves = [] # list of moves made from the solved configuration


	print(NEW_BUTTON.area)
	
	running = True
	while running:
		slideTo = None # the direction, if any, a tile should slide
		msg = 'Click tile or press arrow keys to slide.' # contains the message to show in the upper left corner.
		if mainBoard == SOLVEDBOARD:
			msg = 'Solved!'

		drawBoard(mainBoard, msg)

		for event in sdl2.ext.get_events():
			if event.type == sdl2.SDL_QUIT:
				running = False
				break
			elif event.type == sdl2.SDL_WINDOWEVENT:
				if event.window.event == sdl2.SDL_WINDOWEVENT_EXPOSED:
					print("window exposed")
					drawBoard(mainBoard, msg)
			elif event.type == sdl2.SDL_MOUSEBUTTONUP:
				pos = event.button.x, event.button.y
				spotx, spoty = getSpotClicked(mainBoard, pos[0], pos[1])
				pt = sdl2.SDL_Point(pos[0], pos[1])
				if (spotx, spoty) == (None, None):
					if sdl2.SDL_PointInRect(pt, reset_rect):
						resetAnimation(mainBoard, allMoves)
						allMoves = []
					elif sdl2.SDL_PointInRect(pt, new_rect):
						mainBoard, solutionSeq = generateNewPuzzle(NUMSLIDES)
						allMoves = []
					elif sdl2.SDL_PointInRect(pt, solve_rect):
						resetAnimation(mainBoard, solutionSeq + allMoves)
						allMoves = []

				else:
					#check if clicked tile was next to blank
					blankx, blanky = getBlankPosition(mainBoard)
					if spotx == blankx + 1 and spoty == blanky:
						slideTo = LEFT
					elif spotx == blankx - 1 and spoty == blanky:
						slideTo = RIGHT
					elif spotx == blankx and spoty == blanky + 1:
						slideTo = UP
					elif spotx == blankx and spoty == blanky - 1:
						slideTo = DOWN

			elif event.type == sdl2.SDL_KEYUP:
				# check if the user pressed a key to slide a tile
				sym = event.key.keysym.sym
				if sym in (sdl2.SDLK_LEFT, sdl2.SDLK_a) and isValidMove(mainBoard, LEFT):
					slideTo = LEFT
				elif sym in (sdl2.SDLK_RIGHT, sdl2.SDLK_d) and isValidMove(mainBoard, RIGHT):
					slideTo = RIGHT
				elif sym in (sdl2.SDLK_UP, sdl2.SDLK_w) and isValidMove(mainBoard, UP):
					slideTo = UP
				elif sym in (sdl2.SDLK_DOWN, sdl2.SDLK_s) and isValidMove(mainBoard, DOWN):
					slideTo = DOWN

				elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
					running = False
					break

		if slideTo:
			slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide.', 8) # show slide on screen
			allMoves.append(slideTo) # record the slide

		REN.present()
		sdl2.SDL_Delay(1000//FPS)

	
	sdl2.ext.quit()




def make_text(SPRITE_FACTORY, text, top, left, **kwargs):
	button = SPRITE_FACTORY.from_text(text, **kwargs)
	button.position = top, left
	return (button, sdl2.SDL_Rect(top, left, *button.size))


def generateNewPuzzle(numSlides):
	# From a starting configuration, make numSlides number of moves (and
	# animate these moves).
	sequence = []
	board = getStartingBoard()
	drawBoard(board, 'Generating new puzzle...')
	sdl2.SDL_Delay(500) # pause 500 milliseconds for effect
	lastMove = None
	for i in range(numSlides):
		move = getRandomMove(board, lastMove)
		slideAnimation(board, move, 'Generating new puzzle...', animationSpeed=TILESIZE//3)
		sequence.append(move)
		lastMove = move
	return (board, sequence)


def drawBoard(board, message):
	REN.clear(BGCOLOR)
	if message:
		text, rect = make_text(SPRITE_FACTORY, message, 5, 5)
		SPRITE_RENDERER.render(text)

	for tilex in range(len(board)):
		for tiley in range(len(board[0])):
			if board[tilex][tiley]:
				drawTile(tilex, tiley, board[tilex][tiley])

	left, top = getLeftTopOfTile(0, 0)
	width = BOARDWIDTH * TILESIZE
	height = BOARDHEIGHT * TILESIZE
	
	#One way to draw thick rectangle
	#another (maybe) is draw 4 sdlgfx.thickLineRGBA's
	#though that seems more iffy because would you specify left-3 or 4 since
	#the center of the line is between them with an even width ...
	REN.draw_rect((left-5, top-5, width+11, height+11), BORDERCOLOR)
	REN.draw_rect((left-4, top-4, width+10, height+10), BORDERCOLOR)
	REN.draw_rect((left-3, top-3, width+9, height+9), BORDERCOLOR)
	REN.draw_rect((left-2, top-2, width+8, height+8), BORDERCOLOR)

	
	SPRITE_RENDERER.render([RESET_BUTTON, NEW_BUTTON, SOLVE_BUTTON])


def getStartingBoard():
	# Return a board data structure with tiles in the solved state.
	# For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
	# returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
	counter = 1
	board = []
	for x in range(BOARDWIDTH):
		column = []
		for y in range(BOARDHEIGHT):
			column.append(counter)
			counter += BOARDWIDTH
		board.append(column)
		counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

	board[BOARDWIDTH-1][BOARDHEIGHT-1] = BLANK
	return board


def getBlankPosition(board):
	# Return the x and y of board coordinates of the blank space.
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if board[x][y] == BLANK:
				return (x, y)


def makeMove(board, move):
	# This function does not check if the move is valid.
	blankx, blanky = getBlankPosition(board)

	if move == UP:
		board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
	elif move == DOWN:
		board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
	elif move == LEFT:
		board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
	elif move == RIGHT:
		board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
	blankx, blanky = getBlankPosition(board)
	return (move == UP and blanky != len(board[0]) - 1) or \
		   (move == DOWN and blanky != 0) or \
		   (move == LEFT and blankx != len(board) - 1) or \
		   (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
	# start with a full list of all four moves
	validMoves = [UP, DOWN, LEFT, RIGHT]

	# remove moves from the list as they are disqualified
	if lastMove == UP or not isValidMove(board, DOWN):
		validMoves.remove(DOWN)
	if lastMove == DOWN or not isValidMove(board, UP):
		validMoves.remove(UP)
	if lastMove == LEFT or not isValidMove(board, RIGHT):
		validMoves.remove(RIGHT)
	if lastMove == RIGHT or not isValidMove(board, LEFT):
		validMoves.remove(LEFT)

	# return a random move from the list of remaining moves
	return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
	left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
	top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
	return (left, top)


def getSpotClicked(board, x, y):
	# from the x & y pixel coordinates, get the x & y board coordinates
	pt = sdl2.SDL_Point(x, y)
	for tileX in range(len(board)):
		for tileY in range(len(board[0])):
			left, top = getLeftTopOfTile(tileX, tileY)
			if sdl2.SDL_PointInRect(pt, sdl2.SDL_Rect(left, top, TILESIZE, TILESIZE)):
				return (tileX, tileY)
	return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
	# draw a tile at board coordinates tilex and tiley, optionally a few
	# pixels over (determined by adjx and adjy)
	left, top = getLeftTopOfTile(tilex, tiley)

	REN.fill((left+adjx, top+adjy, TILESIZE, TILESIZE), TILECOLOR)
	num_text = SPRITE_FACTORY.from_text(str(number))
	num_text.position = left + TILESIZE//2 + adjx, top + TILESIZE//2 + adjy
	num_text.x -= num_text.size[0]//2
	num_text.y -= num_text.size[1]//2

	#textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)

	SPRITE_RENDERER.render(num_text)





def slideAnimation(board, direction, message, animationSpeed):
	# Note: This function does not check if the move is valid.

	blankx, blanky = getBlankPosition(board)
	if direction == UP:
		movex = blankx
		movey = blanky + 1
	elif direction == DOWN:
		movex = blankx
		movey = blanky - 1
	elif direction == LEFT:
		movex = blankx + 1
		movey = blanky
	elif direction == RIGHT:
		movex = blankx - 1
		movey = blanky

	print("mx, my", movex, movey)

	left, top = getLeftTopOfTile(movex, movey)
	adjx, adjy = 0, 0

	for i in range(0, TILESIZE, animationSpeed):
		# animate the tile sliding over
		#checkForQuit()
		REN.fill((left+adjx, top+adjy, TILESIZE, TILESIZE), BGCOLOR)
		if direction == UP:
			adjx, adjy = 0, -i
		if direction == DOWN:
			adjx, adjy = 0, i
		if direction == LEFT:
			adjx, adjy = -i, 0
		if direction == RIGHT:
			adjx, adjy = i, 0
		
		drawTile(movex, movey, board[movex][movey], adjx, adjy)
		REN.present()
		sdl2.SDL_Delay(1000//FPS)
	
	REN.fill((left+adjx, top+adjy, TILESIZE, TILESIZE), BGCOLOR)
	makeMove(board, direction)
	drawTile(blankx, blanky, board[blankx][blanky])


def resetAnimation(board, allMoves):
	# make all of the moves in allMoves in reverse.
	revAllMoves = allMoves[:] # gets a copy of the list
	revAllMoves.reverse()

	for move in revAllMoves:
		if move == UP:
			oppositeMove = DOWN
		elif move == DOWN:
			oppositeMove = UP
		elif move == RIGHT:
			oppositeMove = LEFT
		elif move == LEFT:
			oppositeMove = RIGHT
		slideAnimation(board, oppositeMove, '', animationSpeed=TILESIZE//4)



if __name__ == '__main__':
	main()

