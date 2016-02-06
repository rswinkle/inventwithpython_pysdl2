# Four-In-A-Row (a Connect Four clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license


#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com
# Released into Public Domain, fallback MIT/BSD

from __future__ import division

import sdl2.ext, sdl2.sdlgfx
from sdl2 import *

import random, copy, sys


BOARDWIDTH = 7  # how many spaces wide the board is
BOARDHEIGHT = 6 # how many spaces tall the board is
assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'

DIFFICULTY = 2 # how many moves to look ahead. (>2 is usually too much)

SPACESIZE = 50 # size of the tokens and individual board spaces in pixels

FPS = 30 # frames per second to update the screen
WINDOWWIDTH = 640 # width of the program's window, in pixels
WINDOWHEIGHT = 480 # height in pixels

XMARGIN = (WINDOWWIDTH - BOARDWIDTH * SPACESIZE) // 2
YMARGIN = (WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) // 2

BRIGHTBLUE = (0, 50, 255)
WHITE = (255, 255, 255)

BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

RED = 'red'
BLACK = 'black'
EMPTY = None
HUMAN = 'human'
COMPUTER = 'computer'


def main():
	global WINDOW, REN, SPRITE_FACTORY, SPRITE_RENDERER

	global REDPILERECT, BLACKPILERECT, REDTOKENSPR
	global BLACKTOKENSPR, BOARDSPR, ARROWSPR, ARROWPOS, HUMANWINNERSPR
	global COMPUTERWINNERSPR, WINNERRECT, TIEWINNERSPR

	sdl2.ext.init()

	WINDOW = sdl2.ext.Window("Four in a Row", size=(WINDOWWIDTH, WINDOWHEIGHT))
	REN = sdl2.ext.Renderer(WINDOW, flags=sdl2.SDL_RENDERER_SOFTWARE)
	WINDOW.show()

	SPRITE_FACTORY = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE, renderer=REN, free=True)
	SPRITE_RENDERER = SPRITE_FACTORY.create_sprite_render_system(WINDOW)

	REDPILERECT = SDL_Rect(SPACESIZE//2, WINDOWHEIGHT - 3*SPACESIZE//2, SPACESIZE, SPACESIZE)
	BLACKPILERECT = SDL_Rect(WINDOWWIDTH - 3*SPACESIZE//2, WINDOWHEIGHT - 3*SPACESIZE//2, SPACESIZE, SPACESIZE)

	red_surf = load_n_scale_img('4row_red.png', SPACESIZE, SPACESIZE)
	black_surf = load_n_scale_img('4row_black.png', SPACESIZE, SPACESIZE)
	board_surf = load_n_scale_img('4row_board.png', SPACESIZE, SPACESIZE)

	REDTOKENSPR = SPRITE_FACTORY.from_surface(red_surf.contents)
	BLACKTOKENSPR = SPRITE_FACTORY.from_surface(black_surf.contents)
	BOARDSPR = SPRITE_FACTORY.from_surface(board_surf.contents)

	HUMANWINNERSPR = SPRITE_FACTORY.from_image('4row_humanwinner.png')
	COMPUTERWINNERSPR = SPRITE_FACTORY.from_image('4row_computerwinner.png')
	TIEWINNERSPR = SPRITE_FACTORY.from_image('4row_tie.png')
	WINNERRECT = get_spr_rect(HUMANWINNERSPR)
	center_rect(WINNERRECT, WINDOWWIDTH//2, WINDOWHEIGHT//2)


	ARROWSPR = SPRITE_FACTORY.from_image('4row_arrow.png')
	ARROWPOS = SDL_Point()
	ARROWPOS.x = REDPILERECT.x + REDPILERECT.w + 10
	ARROWPOS.y = REDPILERECT.y + REDPILERECT.h//2 - ARROWSPR.size[1]//2
	
	isFirstGame = True

	while True:
		runGame(isFirstGame)
		isFirstGame = False

def load_n_scale_img(image_file, w, h):
	tmp = sdl2.ext.load_image(image_file)
	return sdlgfx.zoomSurface(tmp, w/tmp.w, h/tmp.h, sdlgfx.SMOOTHING_ON)
	


# should make these methods ... not sure I want to modify pysdl2
# too much yet
def get_spr_rect(spr):
	return SDL_Rect(spr.x, spr.y, spr.size[0], spr.size[1])

def center_sprite(spr, x, y):
	spr.position = x - spr.size[0]//2, y - spr.size[1]//2

def center_rect(rect, x, y):
	rect.x, rect.y = x - rect.w//2, y - rect.h//2



def runGame(isFirstGame):
	if isFirstGame:
		# Let the computer go first on the first game, so the player
		# can see how the tokens are dragged from the token piles.
		turn = COMPUTER
		showHelp = True
	else:
		# Randomly choose who goes first.
		if random.randint(0, 1) == 0:
			turn = COMPUTER
		else:
			turn = HUMAN
		showHelp = False

	# Set up a blank board data structure.
	mainBoard = getNewBoard()

	while True: # main game loop
		if turn == HUMAN:
			# Human player's turn.
			getHumanMove(mainBoard, showHelp)
			if showHelp:
				# turn off help arrow after the first move
				showHelp = False
			if isWinner(mainBoard, RED):
				winnerImg = HUMANWINNERSPR
				break
			turn = COMPUTER # switch to other player's turn
		else:
			# Computer player's turn.
			column = getComputerMove(mainBoard)
			animateComputerMoving(mainBoard, column)
			makeMove(mainBoard, BLACK, column)
			if isWinner(mainBoard, BLACK):
				winnerImg = COMPUTERWINNERSPR
				break
			turn = HUMAN # switch to other player's turn

		if isBoardFull(mainBoard):
			# A completely filled board means it's a tie.
			winnerImg = TIEWINNERSPR
			break

	while True:
		# Keep looping until player clicks the mouse or quits.
		starttime = SDL_GetTicks()
		for event in sdl2.ext.get_events():
			if event.type == SDL_QUIT:
				shutdown()
			elif event.type == SDL_KEYUP:
				sc = event.key.keysym.scancode
				if sc == SDL_SCANCODE_ESCAPE:
					shutdown()
			elif event.type == SDL_MOUSEBUTTONUP:
				return

		drawBoard(mainBoard)
		SPRITE_RENDERER.render(winnerImg, WINNERRECT.x, WINNERRECT.y)
		REN.present()
		SDL_Delay(1000//FPS - ((SDL_GetTicks()-starttime)))
		


def makeMove(board, player, column):
	lowest = getLowestEmptySpace(board, column)
	if lowest != -1:
		board[column][lowest] = player


def drawBoard(board, extraToken=None):
	REN.clear(BGCOLOR)

	# draw tokens
	tok_x, tok_y = 0, 0
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			tok_x, tok_y = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
			if board[x][y] == RED:
				SPRITE_RENDERER.render(REDTOKENSPR, tok_x, tok_y)
			elif board[x][y] == BLACK:
				SPRITE_RENDERER.render(BLACKTOKENSPR, tok_x, tok_y)

	# draw the extra token
	if extraToken != None:
		if extraToken['color'] == RED:
			SPRITE_RENDERER.render(REDTOKENSPR, extraToken['x'], extraToken['y'])
		elif extraToken['color'] == BLACK:
			SPRITE_RENDERER.render(BLACKTOKENSPR, extraToken['x'], extraToken['y'])

	# draw board over the tokens
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			tok_x, tok_y = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
			SPRITE_RENDERER.render(BOARDSPR, tok_x, tok_y)

	# draw the red and black tokens off to the side
	SPRITE_RENDERER.render(REDTOKENSPR, REDPILERECT.x, REDPILERECT.y) # red on the left
	SPRITE_RENDERER.render(BLACKTOKENSPR, BLACKPILERECT.x, BLACKPILERECT.y) # black on the right



def getNewBoard():
	board = []
	for x in range(BOARDWIDTH):
		board.append([EMPTY] * BOARDHEIGHT)
	return board


def getHumanMove(board, isFirstMove):
	draggingToken = False
	tokenx, tokeny = None, None
	while True:
		starttime = SDL_GetTicks()
		for event in sdl2.ext.get_events():
			if event.type == SDL_QUIT:
				shutdown()
			elif event.type == SDL_KEYUP:
				sc = event.key.keysym.scancode
				if sc == SDL_SCANCODE_ESCAPE:
					shutdown()
			elif event.type == SDL_MOUSEBUTTONDOWN and not draggingToken and sdl2.rect.SDL_PointInRect(SDL_Point(event.button.x, event.button.y), REDPILERECT):
				# start of dragging on red token pile.
				draggingToken = True
				tokenx, tokeny = event.button.x, event.button.y
			elif event.type == SDL_MOUSEMOTION and draggingToken:
				# update the position of the red token being dragged
				tokenx, tokeny, = event.motion.x, event.motion.y
			elif event.type == SDL_MOUSEBUTTONUP and draggingToken:
				# let go of the token being dragged
				if tokeny < YMARGIN and tokenx > XMARGIN and tokenx < WINDOWWIDTH - XMARGIN:
					# let go at the top of the screen.
					column = (tokenx - XMARGIN) // SPACESIZE
					if isValidMove(board, column):
						animateDroppingToken(board, column, RED)
						board[column][getLowestEmptySpace(board, column)] = RED
						drawBoard(board)
						REN.present()
						return
				tokenx, tokeny = None, None
				draggingToken = False
		if tokenx != None and tokeny != None:
			drawBoard(board, {'x':tokenx - SPACESIZE // 2, 'y':tokeny - SPACESIZE // 2, 'color':RED})
		else:
			drawBoard(board)

		if isFirstMove:
			# Show the help arrow for the player's first move.
			SPRITE_RENDERER.render(ARROWSPR, ARROWPOS.x, ARROWPOS.y)

		REN.present()
		SDL_Delay(1000//FPS - (SDL_GetTicks()-starttime))



def animateDroppingToken(board, column, color):
	x = XMARGIN + column * SPACESIZE
	y = YMARGIN - SPACESIZE
	dropSpeed = 1.0

	lowestEmptySpace = getLowestEmptySpace(board, column)

	while True:
		starttime = SDL_GetTicks()
		y += int(dropSpeed)
		dropSpeed += 10
		if int((y - YMARGIN) // SPACESIZE) >= lowestEmptySpace:
			return
		drawBoard(board, {'x':x, 'y':y, 'color':color})
		REN.present()
		SDL_Delay(1000//FPS - (SDL_GetTicks()-starttime))


def animateComputerMoving(board, column):
	x = BLACKPILERECT.x
	y = BLACKPILERECT.y
	speed = 10.0
	# moving the black tile up
	while y > (YMARGIN - SPACESIZE):
		starttime = SDL_GetTicks()
		y -= int(speed)
		speed += 0.5
		drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
		REN.present()
		SDL_Delay(1000//FPS - ((SDL_GetTicks()-starttime)))
	# moving the black tile over
	y = YMARGIN - SPACESIZE
	speed = 10.0
	while x > (XMARGIN + column * SPACESIZE):
		starttime = SDL_GetTicks()
		x -= int(speed)
		speed += 0.5
		drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
		REN.present()
		SDL_Delay(1000//FPS - (SDL_GetTicks()-starttime))
	# dropping the black tile
	animateDroppingToken(board, column, BLACK)


def getComputerMove(board):
	potentialMoves = getPotentialMoves(board, BLACK, DIFFICULTY)
	# get the best fitness from the potential moves
	bestMoveFitness = -1
	for i in range(BOARDWIDTH):
		if potentialMoves[i] > bestMoveFitness and isValidMove(board, i):
			bestMoveFitness = potentialMoves[i]
	# find all potential moves that have this best fitness
	bestMoves = []
	for i in range(len(potentialMoves)):
		if potentialMoves[i] == bestMoveFitness and isValidMove(board, i):
			bestMoves.append(i)
	return random.choice(bestMoves)


def getPotentialMoves(board, tile, lookAhead):
	if lookAhead == 0 or isBoardFull(board):
		return [0] * BOARDWIDTH

	if tile == RED:
		enemyTile = BLACK
	else:
		enemyTile = RED

	# Figure out the best move to make.
	potentialMoves = [0] * BOARDWIDTH
	for firstMove in range(BOARDWIDTH):
		dupeBoard = copy.deepcopy(board)
		if not isValidMove(dupeBoard, firstMove):
			continue
		makeMove(dupeBoard, tile, firstMove)
		if isWinner(dupeBoard, tile):
			# a winning move automatically gets a perfect fitness
			potentialMoves[firstMove] = 1
			break # don't bother calculating other moves
		else:
			# do other player's counter moves and determine best one
			if isBoardFull(dupeBoard):
				potentialMoves[firstMove] = 0
			else:
				for counterMove in range(BOARDWIDTH):
					dupeBoard2 = copy.deepcopy(dupeBoard)
					if not isValidMove(dupeBoard2, counterMove):
						continue
					makeMove(dupeBoard2, enemyTile, counterMove)
					if isWinner(dupeBoard2, enemyTile):
						# a losing move automatically gets the worst fitness
						potentialMoves[firstMove] = -1
						break
					else:
						# do the recursive call to getPotentialMoves()
						results = getPotentialMoves(dupeBoard2, tile, lookAhead - 1)
						potentialMoves[firstMove] += (sum(results) / BOARDWIDTH) / BOARDWIDTH
	return potentialMoves



def getLowestEmptySpace(board, column):
	# Return the row number of the lowest empty row in the given column.
	for y in range(BOARDHEIGHT-1, -1, -1):
		if board[column][y] == EMPTY:
			return y
	return -1


def isValidMove(board, column):
	# Returns True if there is an empty space in the given column.
	# Otherwise returns False.
	if column < 0 or column >= (BOARDWIDTH) or board[column][0] != EMPTY:
		return False
	return True


def isBoardFull(board):
	# Returns True if there are no empty spaces anywhere on the board.
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if board[x][y] == EMPTY:
				return False
	return True


def isWinner(board, tile):
	# check horizontal spaces
	for x in range(BOARDWIDTH - 3):
		for y in range(BOARDHEIGHT):
			if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
				return True
	# check vertical spaces
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT - 3):
			if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
				return True
	# check / diagonal spaces
	for x in range(BOARDWIDTH - 3):
		for y in range(3, BOARDHEIGHT):
			if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
				return True
	# check \ diagonal spaces
	for x in range(BOARDWIDTH - 3):
		for y in range(BOARDHEIGHT - 3):
			if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
				return True
	return False

def shutdown():
	sdl2.ext.quit()
	sys.exit()


if __name__ == '__main__':
	main()





























