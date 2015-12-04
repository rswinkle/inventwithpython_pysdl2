# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license


#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com

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
	sdl2.ext.init()

	window = sdl2.ext.Window("Slide Puzzle", size=(WINDOWWIDTH, WINDOWHEIGHT))
	ren = sdl2.ext.Renderer(window)
	window.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = sdl2.ext.FontManager(font_file, size=BASICFONTSIZE)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	sprite_factory = sdl2.ext.SpriteFactory(renderer=ren, fontmanager=font_manager)
	spriterenderer = sprite_factory.create_sprite_render_system(window)

	ui_factory = sdl2.ext.UIFactory(sprite_factory)

	reset_button = ui_factory.from_text("Reset")
	reset_button.position = WINDOWWIDTH - 120, WINDOWHEIGHT - 90
	reset_button.click = reset_clicked

	new_button = ui_factory.from_text("New Game")
	new_button.position = WINDOWWIDTH - 120, WINDOWHEIGHT - 60
	new_button.click = new_clicked

	solve_button = ui_factory.from_text("Solve")
	solve_button.position = WINDOWWIDTH - 120, WINDOWHEIGHT - 30
	solve_button.click = solve_clicked


	
	# Create a new UIProcessor, which will handle the user input events
	# and pass them on to the relevant user interface elements.
	ui_processor = sdl2.ext.UIProcessor()


	hello_sprite = sprite_factory.from_text("Hello World!")
	goodbye_sprite = sprite_factory.from_text("Goodbye!")
	goodbye_sprite.position = 200, 0

	print(type(hello_sprite), type(spriterenderer))
	
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
			elif event.type == sdl2.SDL_MOUSEBUTTONUP:
				mousex, mousey = event.button.x, event.button.y
				mouse_clicked = True

			spriterenderer.render(hello_sprite)
			spriterenderer.render(goodbye_sprite)
			ren.present()


def reset_clicked():
	resetAnimation(mainBoard, allMoves)
	allMoves = []

def new_clicked():
	mainBoard, solutionSeq = generateNewPuzzle(80)
	allMoves = []

def solve_clicked():
	resetAnimation(mainBoard, solutionSeq + allMoves)
	allMoves = []


def make_buttons(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)










if __name__ == '__main__':
	main()

