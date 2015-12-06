# Wormy (a Nibbles clone)
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


FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#                           R    G    B
WHITE     = sdl2.ext.Color(255, 255, 255)
BLACK     = sdl2.ext.Color(  0,   0,   0)
RED       = sdl2.ext.Color(255,   0,   0)
GREEN     = sdl2.ext.Color(  0, 255,   0)
DARKGREEN = sdl2.ext.Color(  0, 155,   0)
DARKGRAY  = sdl2.ext.Color( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head


def main():
	#cause I don't want to pass these around
	global ren, sprite_factory, sprite_renderer

	sdl2.ext.init()

	window = sdl2.ext.Window("Wormy", size=(WINDOWWIDTH, WINDOWHEIGHT))
	ren = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_SOFTWARE)
	window.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = sdl2.ext.FontManager(font_file, size=18)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	sprite_factory = sdl2.ext.SpriteFactory(renderer=ren, fontmanager=font_manager, free=True)
	sprite_renderer = sprite_factory.create_sprite_render_system(window)
	
	showStartScreen()
	while True:
		runGame()
		showGameOverScreen()


def showStartScreen():
	titleFont = pygame.font.Font('freesansbold.ttf', 100)

	title1 = sprite_factory.from_text("Wormy!")
	title2 = sprite_factory.from_text("Wormy!")
	#titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
	#titleSurf2 = titleFont.render('Wormy!', True, GREEN)

	degrees1 = 0
	degrees2 = 0
	win_surf = window.get_surface()
	while True:
		ren.clear(BGCOLOR) #fill?
		rot_title1p = sdlgfx.rotozoomSurface(title1.surface, degrees1, 1, sdlgfx.SMOOTHING_ON)
		rot_title2p = sdlgfx.rotozoomSurface(title2.surface, degrees2, 1, sdlgfx.SMOOTHING_ON)

		rot1 = rot_title1p.contents
		rot2 = rot_title2p.contents
		rect1 = sdl2.rect.SDL2_Rect(WINDOWWIDTH//2 - rot1.w//2, WINDOWHEIGHT//2 - rot1.h//2, 0, 0)
		rect2 = sdl2.rect.SDL2_Rect(WINDOWWIDTH//2 - rot2.w//2, WINDOWHEIGHT//2 - rot2.h//2, 0, 0)
		sdl2.SDL_BlitSurface(rot1, None, win_surf, rect1)
		sdl2.SDL_BlitSurface(rot2, None, win_surf, rect2)

		#drawPressKeyMsg()

		if checkForKeyPress():
			pygame.event.get() # clear event queue
			return
		pygame.display.update()
		FPSCLOCK.tick(FPS)
		degrees1 += 3 # rotate by 3 degrees each frame
		degrees2 += 7 # rotate by 7 degrees each frame


def handle_events():

if __name__ == '__main__':
	main()
