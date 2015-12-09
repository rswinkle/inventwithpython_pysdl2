# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com

import random, sys, ctypes
from utils import sysfont

import sdl2.ext, sdl2.sdlmixer
from sdl2 import *



FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 150
MOVEDOWNFREQ = 100

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

BIGFONTSIZE = 100


TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
					 '.....',
					 '..OO.',
					 '.OO..',
					 '.....'],
					['.....',
					 '..O..',
					 '..OO.',
					 '...O.',
					 '.....']]

Z_SHAPE_TEMPLATE = [['.....',
					 '.....',
					 '.OO..',
					 '..OO.',
					 '.....'],
					['.....',
					 '..O..',
					 '.OO..',
					 '.O...',
					 '.....']]

I_SHAPE_TEMPLATE = [['..O..',
					 '..O..',
					 '..O..',
					 '..O..',
					 '.....'],
					['.....',
					 '.....',
					 'OOOO.',
					 '.....',
					 '.....']]

O_SHAPE_TEMPLATE = [['.....',
					 '.....',
					 '.OO..',
					 '.OO..',
					 '.....']]

J_SHAPE_TEMPLATE = [['.....',
					 '.O...',
					 '.OOO.',
					 '.....',
					 '.....'],
					['.....',
					 '..OO.',
					 '..O..',
					 '..O..',
					 '.....'],
					['.....',
					 '.....',
					 '.OOO.',
					 '...O.',
					 '.....'],
					['.....',
					 '..O..',
					 '..O..',
					 '.OO..',
					 '.....']]

L_SHAPE_TEMPLATE = [['.....',
					 '...O.',
					 '.OOO.',
					 '.....',
					 '.....'],
					['.....',
					 '..O..',
					 '..O..',
					 '..OO.',
					 '.....'],
					['.....',
					 '.....',
					 '.OOO.',
					 '.O...',
					 '.....'],
					['.....',
					 '.OO..',
					 '..O..',
					 '..O..',
					 '.....']]

T_SHAPE_TEMPLATE = [['.....',
					 '..O..',
					 '.OOO.',
					 '.....',
					 '.....'],
					['.....',
					 '..O..',
					 '..OO.',
					 '..O..',
					 '.....'],
					['.....',
					 '.....',
					 '.OOO.',
					 '..O..',
					 '.....'],
					['.....',
					 '..O..',
					 '.OO..',
					 '..O..',
					 '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
		  'Z': Z_SHAPE_TEMPLATE,
		  'J': J_SHAPE_TEMPLATE,
		  'L': L_SHAPE_TEMPLATE,
		  'I': I_SHAPE_TEMPLATE,
		  'O': O_SHAPE_TEMPLATE,
		  'T': T_SHAPE_TEMPLATE}




def main():
	#cause I don't want to pass these around
	global window, ren, sprite_factory, sprite_renderer, music

	SDL_Init(SDL_INIT_VIDEO|SDL_INIT_AUDIO)

	window = ext.Window("Tetromino", size=(WINDOWWIDTH, WINDOWHEIGHT))
	ren = ext.Renderer(window, flags=SDL_RENDERER_SOFTWARE)
	window.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = ext.FontManager(font_file, size=18)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	sprite_factory = ext.SpriteFactory(ext.SOFTWARE, renderer=ren, fontmanager=font_manager, free=True)
	sprite_renderer = sprite_factory.create_sprite_render_system(window)

	sdlmixer.Mix_Init(sdlmixer.MIX_INIT_OGG)
	sdlmixer.Mix_OpenAudio(22050, sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
	#BEEP1 = sdlmixer.Mix_LoadWAV(b"beep1.ogg")


	showTextScreen("Tetromino")
	while True:
		if random.randint(0, 1) == 0:
			music = sdlmixer.Mix_LoadMUS(b"tetrisb.mid")
		else:
			music = sdlmixer.Mix_LoadMUS(b"tetrisc.mid")
		sdlmixer.Mix_PlayMusic(music, -1)
		runGame()
		sdlmixer.Mix_HaltMusic()
		showTextScreen("Game Over")


def runGame():
	#setup variables for start of game
	board = getBlankBoard()
	lastMoveDownTime = SDL_GetTicks()
	lastMoveSidewaysTime = lastMoveDownTime
	lastFallTime = lastMoveDownTime
	score = 0
	level, fallFreq = calculateLevelAndFallFreq(score)

	fallingPiece = None
	nextPiece = getNewPiece()

	keylen = ctypes.c_int()
	kybd_st = SDL_GetKeyboardState(ctypes.byref(keylen))

	while True:
		starttime = SDL_GetTicks()
		if fallingPiece == None:
			fallingPiece = nextPiece
			nextPiece = getNewPiece()
			lastFallTime = SDL_GetTicks()

			if not isValidPos(board, fallingPiece):
				return

		for event in ext.get_events():
			if event.type == SDL_QUIT:
				shutdown()
			elif event.type == SDL_KEYUP:
				sc = event.key.keysym.scancode
				if sc == SDL_SCANCODE_ESCAPE:
					shutdown()
				elif sc == SDL_SCANCODE_P:
					#Pausing the game
					ren.clear(BGCOLOR)
					sdlmixer.Mix_PauseMusic()
					showTextScreen("Paused") # pause till keypress
					sdlmixer.Mix_ResumeMusic()
					lastMoveDownTime = SDL_GetTicks()
					lastMoveSidewaysTime = SDL_GetTicks()

				#rotate
				elif sc == SDL_SCANCODE_UP or sc == SDL_SCANCODE_W:
					fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
					if not isValidPos(board, fallingPiece):
						fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
				#rotate other way
				elif sc == SDL_SCANCODE_Q:
					fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
					if not isValidPos(board, fallingPiece):
						fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])

				# move piece all the way down
				elif sc == SDL_SCANCODE_SPACE:
					for i in range(1, BOARDHEIGHT):
						if not isValidPos(board, fallingPiece, adj_y=i):
							break
					fallingPiece['y'] += i-1

			
		if is_moving_left(kybd_st) or is_moving_right(kybd_st) and SDL_GetTicks() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
			if is_moving_left(kybd_st) and isValidPos(board, fallingPiece, adj_x=-1):
				fallingPiece['x'] -= 1
			elif is_moving_right(kybd_st) and isValidPos(board, fallingPiece, adj_x=1):
				fallingPiece['x'] += 1
			lastMoveSidewaysTime = SDL_GetTicks()

		if is_moving_down(kybd_st) and SDL_GetTicks() - lastMoveDownTime > MOVEDOWNFREQ and isValidPos(board, fallingPiece, adj_y=1):
			fallingPiece['y'] += 1
			lastMoveDownTime = SDL_GetTicks()


		# let piece fall if it's time to fall
		if SDL_GetTicks() - lastFallTime > fallFreq:
			# see if piece has landed
			if not isValidPos(board, fallingPiece, adj_y=1):
				print(fallingPiece)
				addToBoard(board, fallingPiece)
				score += removeCompleteLines(board)
				level, fallFreq = calculateLevelAndFallFreq(score)
				fallingPiece = None
			else:
				fallingPiece['y'] += 1
				lastFallTime = SDL_GetTicks() #replace all these calls with variable set at top of loop?

		#draw everything
		ren.clear(BGCOLOR)
		#ren.fill((0,0,WINDOWWIDTH,WINDOWHEIGHT), BGCOLOR)
		#ren.fill((XMARGIN - 3, 0, (BOARDWIDTH * BOXSIZE) + 8, WINDOWHEIGHT), BGCOLOR)

		drawBoard(board)
		if fallingPiece:
			drawPiece(fallingPiece)
		drawStatus(score, level, nextPiece) #ren.present called in here in sprite_renderer.render

		SDL_Delay(1000//FPS - ((SDL_GetTicks()-starttime)))
			
def is_moving_left(keyboard):
	return keyboard[SDL_SCANCODE_LEFT] or keyboard[SDL_SCANCODE_A]

def is_moving_right(keyboard):
	return keyboard[SDL_SCANCODE_RIGHT] or keyboard[SDL_SCANCODE_D]

def is_moving_down(keyboard):
	return keyboard[SDL_SCANCODE_DOWN] or keyboard[SDL_SCANCODE_S]


def shutdown():
	sdlmixer.Mix_CloseAudio()
	#ext.quit()
	SDL_Quit()
	sys.exit()
	#do I need to do anything else here?


def showTextScreen(text):
	# This function displays large text in the
	# center of the screen until a key is pressed.

	# Draw the text drop shadow
	shadowtext = sprite_factory.from_text(text, size=BIGFONTSIZE, color=TEXTSHADOWCOLOR)
	shadowtext.position = WINDOWWIDTH//2 - shadowtext.size[0]//2, WINDOWHEIGHT//2 - shadowtext.size[1]//2

	# Draw the text
	textsprite = sprite_factory.from_text(text, size=BIGFONTSIZE, color=TEXTCOLOR)
	textsprite.position = shadowtext.x-3, shadowtext.y-3

	# Draw the additional "Press a key to play." text.
	presskeysprite = sprite_factory.from_text("Press a key to play.", color=TEXTCOLOR)
	presskeysprite.position = WINDOWWIDTH//2-presskeysprite.size[0]//2, shadowtext.y + 100

	sprite_renderer.render([shadowtext, textsprite, presskeysprite])
	while checkForKeyPress() == None:
		pass
		#window.refresh()


def checkForKeyPress():
	for event in ext.get_events():
		if event.type == SDL_QUIT:
			shutdown()
		elif event.type == SDL_KEYUP:
			sc = event.key.keysym.scancode
			if sc == SDL_SCANCODE_ESCAPE:
				shutdown()
			return event.key.keysym.scancode

def calculateLevelAndFallFreq(score):
	# Based on the score, return the level the player is on and
	# how many milliseconds pass until a falling piece falls one space.
	level = score//10 + 1
	fallFreq = 270 - (level * 20)
	return level, fallFreq


def getNewPiece():
	# return a random new piece in a random rotation and color
	shape = random.choice(list(PIECES.keys()))
	newPiece = {'shape': shape,
				'rotation': random.randint(0, len(PIECES[shape]) - 1),
				'x': BOARDWIDTH // 2 - TEMPLATEWIDTH // 2,
				'y': -2, # start it above the board (i.e. less than 0)
				'color': random.randint(0, len(COLORS)-1)}
	return newPiece


def addToBoard(board, piece):
	# fill in the board based on piece's location, shape, and rotation
	for x in range(TEMPLATEWIDTH):
		for y in range(TEMPLATEHEIGHT):
			if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
				board[x + piece['x']][y + piece['y']] = piece['color']


def getBlankBoard():
	# create and return a new blank board data structure
	board = []
	for i in range(BOARDWIDTH):
		board.append([BLANK] * BOARDHEIGHT)
	return board


def isOnBoard(x, y):
	return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPos(board, piece, adj_x=0, adj_y=0):
	# Return True if the piece is within the board and not colliding
	for x in range(TEMPLATEWIDTH):
		for y in range(TEMPLATEHEIGHT):
			isAboveBoard = y + piece['y'] + adj_y < 0
			if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
				continue
			if not isOnBoard(x + piece['x'] + adj_x, y + piece['y'] + adj_y):
				return False
			if board[x + piece['x'] + adj_x][y + piece['y'] + adj_y] != BLANK:
				return False
	return True

def isCompleteLine(board, y):
	# Return True if the line filled with boxes with no gaps.
	for x in range(BOARDWIDTH):
		if board[x][y] == BLANK:
			return False
	return True


def removeCompleteLines(board):
	# Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
	numLinesRemoved = 0
	y = BOARDHEIGHT - 1 # start y at the bottom of the board
	while y >= 0:
		if isCompleteLine(board, y):
			# Remove the line and pull boxes down by one line.
			for pullDownY in range(y, 0, -1):
				for x in range(BOARDWIDTH):
					board[x][pullDownY] = board[x][pullDownY-1]
			# Set very top line to blank.
			for x in range(BOARDWIDTH):
				board[x][0] = BLANK
			numLinesRemoved += 1
			# Note on the next iteration of the loop, y is the same.
			# This is so that if the line that was pulled down is also
			# complete, it will be removed.
		else:
			y -= 1 # move on to check next row up
	return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
	# Convert the given xy coordinates of the board to xy
	# coordinates of the location on the screen.
	return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
	# draw a single box (each tetromino piece has four boxes)
	# at xy coordinates on the board. Or, if pixelx & pixely
	# are specified, draw to the pixel coordinates stored in
	# pixelx & pixely (this is used for the "Next" piece).
	if color == BLANK:
		return
	if pixelx == None and pixely == None:
		pixelx, pixely = convertToPixelCoords(boxx, boxy)
	ren.fill((pixelx+1, pixely+1, BOXSIZE-1, BOXSIZE-1), COLORS[color])
	ren.fill((pixelx+1, pixely+1, BOXSIZE-4, BOXSIZE-4), LIGHTCOLORS[color])


def drawBoard(board):
	# draw the border around the board (a box 10 pixels wider than playing area)
	ren.fill((XMARGIN - 5, TOPMARGIN - 5, (BOARDWIDTH * BOXSIZE) + 10, (BOARDHEIGHT * BOXSIZE) + 10), BORDERCOLOR) 

	# fill the background of the board
	ren.fill((XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT), BGCOLOR) 
	# draw the individual boxes on the board
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			drawBox(x, y, board[x][y])


def drawStatus(score, level, piece):
	# creote the text sprites
	score_sprite = sprite_factory.from_text("Score: %s" % score, color=TEXTCOLOR)
	score_sprite.position = WINDOWWIDTH - 150, 20

	level_sprite = sprite_factory.from_text("Level: %s" % level, color=TEXTCOLOR)
	level_sprite.position = WINDOWWIDTH-150, 50

	next_text = sprite_factory.from_text("Next:", color=TEXTCOLOR)
	next_text.position = WINDOWWIDTH - 120, 80

	drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)
	sprite_renderer.render((score_sprite, level_sprite, next_text))


def drawPiece(piece, pixelx=None, pixely=None):
	shapeToDraw = PIECES[piece['shape']][piece['rotation']]
	if pixelx == None and pixely == None:
		# if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
		pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

	# draw each of the boxes that make up the piece
	for x in range(TEMPLATEWIDTH):
		for y in range(TEMPLATEHEIGHT):
			if shapeToDraw[y][x] != BLANK:
				drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))






if __name__ == '__main__':
	main()
