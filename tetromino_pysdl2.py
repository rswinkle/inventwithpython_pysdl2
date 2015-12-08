# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com

import random, time, sys
from utils import sysfont

import sdl2.ext
import sdl2
from sdl2 import sdlgfx, sdlmixer



FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

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
	global window, ren, sprite_factory, sprite_renderer

	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO|sdl2.SDL_INIT_AUDIO)

	window = sdl2.ext.Window("Tetromino", size=(WINDOWWIDTH, WINDOWHEIGHT))
	ren = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_SOFTWARE)
	window.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = sdl2.ext.FontManager(font_file, size=18)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE, renderer=ren, fontmanager=font_manager, free=True)
	sprite_renderer = sprite_factory.create_sprite_render_system(window)

	sdlmixer.Mix_Init(sdlmixer.MIX_INIT_OGG)
	sdlmixer.Mix_OpenAudio(44100, sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
	#BEEP1 = sdlmixer.Mix_LoadWAV(b"beep1.ogg")


	showTextScreen("Tetromino")
	while True:
		if random.randint(0, 1) == 0:
			music = sdl2.sdlmixer.Mix_LoadMUS(b"tetrisb.mid")
		else:
			music = sdl2.sdlmixer.Mix_LoadMUS(b"tetrisc.mid")
		sdl2.sdlmixer.Mix_PlayMusic(music, -1)
		runGame()
		sdl2.sdlmixer.Mix_HaltMusic()
		showTextScreen("Game Over")


def runGame():
	#setup variables for start of game
	board = getBlankBoard()
	lastMoveDownTime = sdl2.SDL_GetTicks()
	#TODO
	while True:
		for event in sdl2.ext.get_events():
			if event.type == sdl2.SDL_QUIT:
				shutdown()
			elif event.type == sdl2.SDL_KEYDOWN:
				sc = event.key.keysym.scancode
				if sc == sdl2.SDL_SCANCODE_ESCAPE:
					shutdown()


def shutdown():
	sdlmixer.Mix_CloseAudio()
	#sdl2.ext.quit()
	sdl2.SDL_Quit()
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
	presskeysprite.position = shadowtext.x, shadowtext.y + 100

	sprite_renderer.render([shadowtext, textsprite, presskeysprite])
	while checkForKeyPress() == None:
		pass
		#window.refresh()


def checkForKeyPress():
	for event in sdl2.ext.get_events():
		if event.type == sdl2.SDL_QUIT:
			shutdown()
		elif event.type == sdl2.SDL_KEYUP:
			sc = event.key.keysym.scancode
			if sc == sdl2.SDL_SCANCODE_ESCAPE:
				shutdown()
			return event.key.keysym.scancode



if __name__ == '__main__':
	main()
