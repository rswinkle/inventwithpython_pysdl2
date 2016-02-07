# Flippy (an Othello or Reversi clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# Based on the "reversi.py" code that originally appeared in "Invent
# Your Own Computer Games with Python", chapter 15:
#   http://inventwithpython.com/chapter15.html

#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com
# Released into Public Domain, fallback MIT/BSD

from __future__ import division

import sdl2.ext, sdl2.sdlgfx
from sdl2 import *

import random, sys, time, copy
from utils import sysfont



FPS = 30 # frames per second to update the screen
WINDOWWIDTH = 640 # width of the program's window, in pixels
WINDOWHEIGHT = 480 # height in pixels
SPACESIZE = 50 # width & height of each space on the board, in pixels
BOARDWIDTH = 8 # how many columns of spaces on the game board
BOARDHEIGHT = 8 # how many rows of spaces on the game board
WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value
HINT_TILE = 'HINT_TILE' # an arbitrary but unique value
ANIMATIONSPEED = 25 # integer from 1 to 100, higher is faster animation

# Amount of space on the left & right side (XMARGIN) or above and below
# (YMARGIN) the game board, in pixels.
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

#                       R    G    B
WHITE      = ext.Color(255, 255, 255)
BLACK      = ext.Color(  0,   0,   0)
GREEN      = ext.Color(  0, 155,   0)
BRIGHTBLUE = ext.Color(  0,  50, 255)
BROWN      = ext.Color(174,  94,   0)

TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN



def main():
	global WINDOW, REN, SPRITE_FACTORY, SPRITE_RENDERER, BG_SPR

	sdl2.ext.init()

	WINDOW = sdl2.ext.Window("Flippy", size=(WINDOWWIDTH, WINDOWHEIGHT))
	REN = sdl2.ext.Renderer(WINDOW, flags=sdl2.SDL_RENDERER_SOFTWARE)
	WINDOW.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = sdl2.ext.FontManager(font_file, size=16)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	SPRITE_FACTORY = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE, renderer=REN, fontmanager=font_manager, free=True)
	SPRITE_RENDERER = SPRITE_FACTORY.create_sprite_render_system(WINDOW)


	bg_image = load_n_scale_img('flippybackground.png', WINDOWWIDTH, WINDOWHEIGHT)
	board_surf = load_n_scale_img('flippyboard.png', BOARDWIDTH*SPACESIZE, BOARDWIDTH*SPACESIZE)

	SDL_BlitSurface(board_surf, None, bg_image, SDL_Rect(XMARGIN, YMARGIN, 0, 0))

	print(bg_image.w, bg_image.h)
	BG_SPR = SPRITE_FACTORY.from_surface(bg_image)
	print(BG_SPR.position, BG_SPR.size)
	

	
	while True:
		if runGame() == False:
			break



def load_n_scale_img(image_file, w, h):
	tmp = sdl2.ext.load_image(image_file)
	tmp2 = sdlgfx.zoomSurface(tmp, w/tmp.w, h/tmp.h, sdlgfx.SMOOTHING_ON)
	tmp2 = tmp2.contents
	print(image_file, tmp.w, tmp.h, tmp2.w, tmp2.h)
	return tmp2
	


# should make these methods ... not sure I want to modify pysdl2
# too much yet
def get_spr_rect(spr):
	return SDL_Rect(spr.x, spr.y, spr.size[0], spr.size[1])

def center_sprite(spr, x, y):
	spr.position = x - spr.size[0]//2, y - spr.size[1]//2

def center_rect(rect, x, y):
	rect.x, rect.y = x - rect.w//2, y - rect.h//2



def runGame():
	# Plays a single game of reversi each time this function is called.

	# Reset the board and game.
	mainBoard = getNewBoard()
	resetBoard(mainBoard)
	showHints = False
	turn = random.choice(['computer', 'player'])

	# Draw the starting board and ask the player what color they want.
	drawBoard(mainBoard)
	playerTile, computerTile = enterPlayerTile()

	# Make the sprite and Rect objects for the "New Game" and "Hints" buttons
	newGame = SPRITE_FACTORY.from_text("New Game", color=TEXTCOLOR, bg_color=TEXTBGCOLOR2)
	newGame.position = (WINDOWWIDTH - 8 - newGame.size[0], 10)
	newGameRect = get_spr_rect(newGame)
	
	hints = SPRITE_FACTORY.from_text("Hints", color= TEXTCOLOR, bg_color=TEXTBGCOLOR2)
	hints.position = (WINDOWWIDTH - 8 - hints.size[0], 40)
	hintsRect = get_spr_rect(hints)

	while True: # main game loop
		# Keep looping for player and computer's turns.
		if turn == 'player':
			# Player's turn:
			if getValidMoves(mainBoard, playerTile) == []:
				# If it's the player's turn but they
				# can't move, then end the game.
				break
			movexy = None
			while movexy == None:
				# Keep looping until the player clicks on a valid space.

				# Determine which board data structure to use for display.
				if showHints:
					boardToDraw = getBoardWithValidMoves(mainBoard, playerTile)
				else:
					boardToDraw = mainBoard

				for event in ext.get_events():
					if event.type == SDL_QUIT:
						shutdown()
					elif event.type == SDL_KEYUP:
						sc = event.key.keysym.scancode
						if sc == SDL_SCANCODE_ESCAPE:
							shutdown()
					elif event.type == SDL_MOUSEBUTTONUP:
						# Handle mouse click events
						mousex, mousey = event.button.x, event.button.y
						if rect.SDL_PointInRect(SDL_Point(mousex, mousey), newGameRect):
							# Start a new game
							return True
						elif rect.SDL_PointInRect(SDL_Point(mousex, mousey), hintsRect):
							# Toggle hints mode
							showHints = not showHints
						# movexy is set to a two-item tuple XY coordinate, or None value
						movexy = getSpaceClicked(mousex, mousey)
						if movexy != None and not isValidMove(mainBoard, playerTile, movexy[0], movexy[1]):
							movexy = None

				# Draw the game board.
				drawBoard(boardToDraw)
				drawInfo(boardToDraw, playerTile, computerTile, turn)

				# Draw the "New Game" and "Hints" buttons.
				SPRITE_RENDERER.render([newGame, hints])

				SDL_Delay(1000//FPS) #TODO
				REN.present()

			# Make the move and end the turn.
			makeMove(mainBoard, playerTile, movexy[0], movexy[1], True)
			if getValidMoves(mainBoard, computerTile) != []:
				# Only set for the computer's turn if it can make a move.
				turn = 'computer'

		else:
			# Computer's turn:
			if getValidMoves(mainBoard, computerTile) == []:
				# If it was set to be the computer's turn but
				# they can't move, then end the game.
				break

			# Draw the board.
			drawBoard(mainBoard)
			drawInfo(mainBoard, playerTile, computerTile, turn)

			# Draw the "New Game" and "Hints" buttons.
			SPRITE_RENDERER.render([newGame, hints])

			# Make it look like the computer is thinking by pausing a bit.
			pauseUntil = SDL_GetTicks() + random.randint(5, 15) * 100
			while SDL_GetTicks() < pauseUntil:
				REN.present()

			# Make the move and end the turn.
			x, y = getComputerMove(mainBoard, computerTile)
			makeMove(mainBoard, computerTile, x, y, True)
			if getValidMoves(mainBoard, playerTile) != []:
				# Only set for the player's turn if they can make a move.
				turn = 'player'

	# Display the final score.
	drawBoard(mainBoard)
	scores = getScoreOfBoard(mainBoard)

	# Determine the text of the message to display.
	if scores[playerTile] > scores[computerTile]:
		text = 'You beat the computer by %s points! Congratulations!' % \
			   (scores[playerTile] - scores[computerTile])
	elif scores[playerTile] < scores[computerTile]:
		text = 'You lost. The computer beat you by %s points.' % \
			   (scores[computerTile] - scores[playerTile])
	else:
		text = 'The game was a tie!'

	result_spr = SPRITE_FACTORY.from_text(text, color=TEXTCOLOR, bg_color=TEXTBGCOLOR1)
	center_sprite(result_spr, WINDOWWIDTH//2, WINDOWHEIGHT//2)

	# Display the "Play again?" text with Yes and No buttons.
	play_again_spr = SPRITE_FACTORY.from_text('Play again?', color=TEXTCOLOR, bg_color=TEXTBGCOLOR1)
	center_sprite(play_again_spr, WINDOWWIDTH//2, WINDOWHEIGHT//2 + 50)

	# Make "Yes" button.
	yes_spr = SPRITE_FACTORY.from_text('Yes', color=TEXTCOLOR, bg_color=TEXTBGCOLOR1)
	center_sprite(yespr, WINDOWWIDTH//2 - 60, WINDOWHEIGHT//2 + 90)
	yes_rect = get_spr_rect(yes_spr)

	# Make "No" button.
	no_spr = SPRITE_FACTORY.from_text('No', color=TEXTCOLOR, bg_color=TEXTBGCOLOR1)
	center_sprite(no_spr, WINDOWWIDTH//2 + 60, WINDOWHEIGHT//2 + 90)
	no_rect = get_spr_rect(no_spr)

	while True:
		# Process events until the user clicks on Yes or No.
		for event in ext.get_events(): # event handling loop
			if event.type == SDL_QUIT:
				shutdown()
			elif event.type == SDL_KEYUP:
				sc = event.key.keysym.scancode
				if sc == SDL_SCANCODE_ESCAPE:
					shutdown()
			elif event.type == MOUSEBUTTONUP:
				pt = SDL_Point(event.button.x, event.button.y)
				if rect.SDL_PointInRect(pt, yes_rect):
					return True
				elif rect.SDL_PointInRect(pt, no_rect):
					return False
		SPRITE_RENDERER.render([result_spr, play_again_spr, yes_spr, nospr])
		REN.present()
		SDL_Delay(1000//FPS)



def translateBoardToPixelCoord(x, y):
	return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)


def animateTileChange(tilesToFlip, tileColor, additionalTile):
	# Draw the additional tile that was just laid down. (Otherwise we'd
	# have to completely redraw the board & the board info.)
	if tileColor == WHITE_TILE:
		additionalTileColor = WHITE
	else:
		additionalTileColor = BLACK
	additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
	sdlgfx.filledCircleRGBA(REN.renderer, additionalTileX, additionalTileY, SPACESIZE//2 - 4, *additionalTileColor)
	REN.present()

	for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2.55)):
		for event in ext.get_events():
			if event.type == SDL_QUIT:
				shutdown()
			elif event.type == SDL_KEYUP:
				sc = event.key.keysym.scancode
				if sc == SDL_SCANCODE_ESCAPE:
					shutdown()

		if rgbValues > 255:
			rgbValues = 255
		elif rgbValues < 0:
			rgbValues = 0

		if tileColor == WHITE_TILE:
			color = (rgbValues, rgbValues, rgbValues, 255) # rgbValues goes from 0 to 255
		elif tileColor == BLACK_TILE:
			color = (255 - rgbValues, 255 - rgbValues, 255 - rgbValues, 255) # rgbValues goes from 255 to 0

		for x, y in tilesToFlip:
			centerx, centery = translateBoardToPixelCoord(x, y)
			sdlgfx.filledCircleRGBA(REN.renderer, centerx, centery, SPACESIZE//2 - 4, *color)
		REN.present()
		SDL_Delay(1000//FPS)



def drawBoard(board):
	# Draw background of board.
	SPRITE_RENDERER.render(BG_SPR) # sprite position set to 0, 0 in constructor

	# Draw grid lines of the board.
	for x in range(BOARDWIDTH + 1):
		# Draw the horizontal lines.
		startx = (x * SPACESIZE) + XMARGIN
		starty = YMARGIN
		endx = (x * SPACESIZE) + XMARGIN
		endy = YMARGIN + (BOARDHEIGHT * SPACESIZE)
		REN.draw_line((startx, starty, endx, endy), GRIDLINECOLOR)
	for y in range(BOARDHEIGHT + 1):
		# Draw the vertical lines.
		startx = XMARGIN
		starty = (y * SPACESIZE) + YMARGIN
		endx = XMARGIN + (BOARDWIDTH * SPACESIZE)
		endy = (y * SPACESIZE) + YMARGIN
		REN.draw_line((startx, starty, endx, endy), GRIDLINECOLOR)

	# Draw the black & white tiles or hint spots.
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			centerx, centery = translateBoardToPixelCoord(x, y)
			if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
				if board[x][y] == WHITE_TILE:
					tileColor = WHITE
				else:
					tileColor = BLACK
				sdlgfx.filledCircleRGBA(REN.renderer, centerx, centery, SPACESIZE//2 - 4, *tileColor) 
			if board[x][y] == HINT_TILE:
				REN.fill((centerx-4, centery-4, 8, 8), HINTCOLOR)



def getSpaceClicked(mousex, mousey):
	# Return a tuple of two integers of the board space coordinates where
	# the mouse was clicked. (Or returns None not in any space.)
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if mousex > x * SPACESIZE + XMARGIN and \
			   mousex < (x + 1) * SPACESIZE + XMARGIN and \
			   mousey > y * SPACESIZE + YMARGIN and \
			   mousey < (y + 1) * SPACESIZE + YMARGIN:
				return (x, y)
	return None


def drawInfo(board, playerTile, computerTile, turn):
	# Draws scores and whose turn it is at the bottom of the screen.
	scores = getScoreOfBoard(board)
	score_spr = SPRITE_FACTORY.from_text("Player Score: %s    Computer Score: %s    %s's Turn" % (str(scores[playerTile]), str(scores[computerTile]), turn.title()), color=TEXTCOLOR)

	score_spr.position = 10, WINDOWHEIGHT - 5 - score_spr.size[1]
	SPRITE_RENDERER.render(score_spr)


def resetBoard(board):
	# Blanks out the board it is passed, and sets up starting tiles.
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			board[x][y] = EMPTY_SPACE

	# Add starting pieces to the center
	board[3][3] = WHITE_TILE
	board[3][4] = BLACK_TILE
	board[4][3] = BLACK_TILE
	board[4][4] = WHITE_TILE


def getNewBoard():
	# Creates a brand new, empty board data structure.
	board = []
	for i in range(BOARDWIDTH):
		board.append([EMPTY_SPACE] * BOARDHEIGHT)

	return board


def isValidMove(board, tile, xstart, ystart):
	# Returns False if the player's move is invalid. If it is a valid
	# move, returns a list of spaces of the captured pieces.
	if board[xstart][ystart] != EMPTY_SPACE or not isOnBoard(xstart, ystart):
		return False

	board[xstart][ystart] = tile # temporarily set the tile on the board.

	if tile == WHITE_TILE:
		otherTile = BLACK_TILE
	else:
		otherTile = WHITE_TILE

	tilesToFlip = []
	# check each of the eight directions:
	for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
		x, y = xstart, ystart
		x += xdirection
		y += ydirection
		if isOnBoard(x, y) and board[x][y] == otherTile:
			# The piece belongs to the other player next to our piece.
			x += xdirection
			y += ydirection
			if not isOnBoard(x, y):
				continue
			while board[x][y] == otherTile:
				x += xdirection
				y += ydirection
				if not isOnBoard(x, y):
					break # break out of while loop, continue in for loop
			if not isOnBoard(x, y):
				continue
			if board[x][y] == tile:
				# There are pieces to flip over. Go in the reverse
				# direction until we reach the original space, noting all
				# the tiles along the way.
				while True:
					x -= xdirection
					y -= ydirection
					if x == xstart and y == ystart:
						break
					tilesToFlip.append([x, y])

	board[xstart][ystart] = EMPTY_SPACE # make space empty
	if len(tilesToFlip) == 0: # If no tiles flipped, this move is invalid
		return False
	return tilesToFlip


def isOnBoard(x, y):
	# Returns True if the coordinates are located on the board.
	return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT


def getBoardWithValidMoves(board, tile):
	# Returns a new board with hint markings.
	dupeBoard = copy.deepcopy(board)

	for x, y in getValidMoves(dupeBoard, tile):
		dupeBoard[x][y] = HINT_TILE
	return dupeBoard


def getValidMoves(board, tile):
	# Returns a list of (x,y) tuples of all valid moves.
	validMoves = []

	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if isValidMove(board, tile, x, y) != False:
				validMoves.append((x, y))
	return validMoves


def getScoreOfBoard(board):
	# Determine the score by counting the tiles.
	xscore = 0
	oscore = 0
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if board[x][y] == WHITE_TILE:
				xscore += 1
			if board[x][y] == BLACK_TILE:
				oscore += 1
	return {WHITE_TILE:xscore, BLACK_TILE:oscore}


def enterPlayerTile():
	# Draws the text and handles the mouse click events for letting
	# the player choose which color they want to be.  Returns
	# [WHITE_TILE, BLACK_TILE] if the player chooses to be White,
	# [BLACK_TILE, WHITE_TILE] if Black.

	# Create the text.
	text_spr = SPRITE_FACTORY.from_text('Do you want to be white or black?', color=TEXTCOLOR, bg_color=TEXTBGCOLOR1)
	center_sprite(text_spr, WINDOWWIDTH//2, WINDOWHEIGHT//2)

	white_spr = SPRITE_FACTORY.from_text('White', color=TEXTCOLOR, bg_color=TEXTBGCOLOR1)
	center_sprite(white_spr, WINDOWWIDTH//2 - 60, WINDOWHEIGHT//2 + 40)

	black_spr = SPRITE_FACTORY.from_text('Black', color=TEXTCOLOR, bg_color=TEXTBGCOLOR1)
	center_sprite(black_spr, WINDOWWIDTH//2 + 60, WINDOWHEIGHT//2 + 40)

	while True:
		# Keep looping until the player has clicked on a color.
		for event in ext.get_events(): # event handling loop
			if event.type == SDL_QUIT:
				shutdown()
			elif event.type == SDL_KEYUP:
				sc = event.key.keysym.scancode
				if sc == SDL_SCANCODE_ESCAPE:
					shutdown()
			elif event.type == SDL_MOUSEBUTTONUP:
				pt = SDL_Point(event.button.x, event.button.y)
				print(pt)
				if rect.SDL_PointInRect(pt, get_spr_rect(white_spr)):
					return [WHITE_TILE, BLACK_TILE]
				elif rect.SDL_PointInRect(pt, get_spr_rect(black_spr)):
					return [BLACK_TILE, WHITE_TILE]

		# Draw the screen.
		SPRITE_RENDERER.render([text_spr, white_spr, black_spr])
		REN.present()
		SDL_Delay(1000//FPS)



def makeMove(board, tile, xstart, ystart, realMove=False):
	# Place the tile on the board at xstart, ystart, and flip tiles
	# Returns False if this is an invalid move, True if it is valid.
	tilesToFlip = isValidMove(board, tile, xstart, ystart)

	if tilesToFlip == False:
		return False

	board[xstart][ystart] = tile

	if realMove:
		animateTileChange(tilesToFlip, tile, (xstart, ystart))

	for x, y in tilesToFlip:
		board[x][y] = tile
	return True


def isOnCorner(x, y):
	# Returns True if the position is in one of the four corners.
	return (x == 0 and y == 0) or \
		   (x == BOARDWIDTH and y == 0) or \
		   (x == 0 and y == BOARDHEIGHT) or \
		   (x == BOARDWIDTH and y == BOARDHEIGHT)


def getComputerMove(board, computerTile):
	# Given a board and the computer's tile, determine where to
	# move and return that move as a [x, y] list.
	possibleMoves = getValidMoves(board, computerTile)

	# randomize the order of the possible moves
	random.shuffle(possibleMoves)

	# always go for a corner if available.
	for x, y in possibleMoves:
		if isOnCorner(x, y):
			return [x, y]

	# Go through all possible moves and remember the best scoring move
	bestScore = -1
	for x, y in possibleMoves:
		dupeBoard = copy.deepcopy(board)
		makeMove(dupeBoard, computerTile, x, y)
		score = getScoreOfBoard(dupeBoard)[computerTile]
		if score > bestScore:
			bestMove = [x, y]
			bestScore = score
	return bestMove



def shutdown():
	sdl2.ext.quit()
	sys.exit()




if __name__ == '__main__':
	main()
























