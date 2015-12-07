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
	global window, ren, sprite_factory, sprite_renderer

	sdl2.ext.init()

	window = sdl2.ext.Window("Wormy", size=(WINDOWWIDTH, WINDOWHEIGHT))
	ren = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_SOFTWARE)
	window.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = sdl2.ext.FontManager(font_file, size=18)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE, renderer=ren, fontmanager=font_manager, free=True)
	sprite_renderer = sprite_factory.create_sprite_render_system(window)
	
	showStartScreen()
	while True:
		runGame()
		showGameOverScreen()



def runGame():
	# Set a random start point.
	startx = random.randint(5, CELLWIDTH - 6)
	starty = random.randint(5, CELLHEIGHT - 6)
	wormCoords = [{'x': startx,     'y': starty},
				  {'x': startx - 1, 'y': starty},
				  {'x': startx - 2, 'y': starty}]
	direction = RIGHT
	latestdir = direction
	turns = []

	# Start the apple in a random place.
	apple = getRandomLocation()

	while True: # main game loop
		for event in sdl2.ext.get_events():
			if turns:
				latestdir = turns[0]
			else:
				latestdir = direction

			if event.type == sdl2.SDL_QUIT:
				shutdown()
			elif event.type == sdl2.SDL_KEYDOWN:
				sc = event.key.keysym.scancode
				#only get the first valid turn otherwise you can kill yourself by turning
				#180 degrees in the same frame
				if (sc == sdl2.SDL_SCANCODE_LEFT or sc == sdl2.SDL_SCANCODE_A) and latestdir != RIGHT:
					turns.append(LEFT)
				elif (sc == sdl2.SDL_SCANCODE_RIGHT or sc == sdl2.SDL_SCANCODE_D) and latestdir != LEFT:
					turns.append(RIGHT)
				elif (sc == sdl2.SDL_SCANCODE_UP or sc == sdl2.SDL_SCANCODE_W) and latestdir != DOWN:
					turns.append(UP)
				elif (sc == sdl2.SDL_SCANCODE_DOWN or sc == sdl2.SDL_SCANCODE_S) and latestdir != UP:
					turns.append(DOWN)
				if sc == sdl2.SDL_SCANCODE_ESCAPE:
					shutdown()

		# check if the worm has hit itself or the edge
		if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
			print("hit edge")
			return # game over
		for wormBody in wormCoords[1:]:
			if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
				print("hit itself")
				return # game over

		# check if worm has eaten an apple
		if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
			# don't remove worm's tail segment
			apple = getRandomLocation() # set a new apple somewhere
		else:
			del wormCoords[-1] # remove worm's tail segment
			#wormCoords.pop()

		#get first actual turn
		while turns:
			if turns[0] != direction:
				direction = turns.pop(0)
				break
			turns.pop(0)

		# move the worm by adding a segment in the direction it is moving
		if direction == UP:
			newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
		elif direction == DOWN:
			newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
		elif direction == LEFT:
			newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
		elif direction == RIGHT:
			newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

		wormCoords.insert(0, newHead)

		ren.clear(BGCOLOR)

		drawGrid()
		drawWorm(wormCoords)
		drawApple(apple)
		drawScore(len(wormCoords) - 3)
		ren.present()
		sdl2.SDL_Delay(1000//FPS)





def showStartScreen():
	title1 = sprite_factory.from_text("Wormy!", size=100, bg_color=DARKGREEN)
	title2 = sprite_factory.from_text("Wormy!", size=100, color=GREEN)
	#titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
	#titleSurf2 = titleFont.render('Wormy!', True, GREEN)

	pressKey = sprite_factory.from_text("Press a key to play.", color=DARKGRAY)
	pressKey.position = WINDOWWIDTH - 200, WINDOWHEIGHT - 30

	degrees1 = 0
	degrees2 = 0
	win_surf = window.get_surface()
	while True:
		ren.clear(BGCOLOR) #fill?
		rot_title1p = sdlgfx.rotozoomSurface(title1.surface, degrees1, 1, sdlgfx.SMOOTHING_ON)
		rot_title2p = sdlgfx.rotozoomSurface(title2.surface, degrees2, 1, sdlgfx.SMOOTHING_ON)

		rot1 = rot_title1p.contents
		rot2 = rot_title2p.contents
		rect1 = sdl2.rect.SDL_Rect(WINDOWWIDTH//2 - rot1.w//2, WINDOWHEIGHT//2 - rot1.h//2, 0, 0)
		rect2 = sdl2.rect.SDL_Rect(WINDOWWIDTH//2 - rot2.w//2, WINDOWHEIGHT//2 - rot2.h//2, 0, 0)
		sdl2.SDL_BlitSurface(rot1, None, win_surf, rect1)
		sdl2.SDL_BlitSurface(rot2, None, win_surf, rect2)

		if check_for_key_press():
			return

		#TODO test order etc
		window.refresh()
		sprite_renderer.render(pressKey)
		#ren.present()

		sdl2.SDL_Delay(1000//FPS)
		degrees1 += 3 # rotate by 3 degrees each frame
		degrees2 += 7 # rotate by 7 degrees each frame


def showGameOverScreen():
	gamesprite = sprite_factory.from_text("Game", size=150)
	oversprite = sprite_factory.from_text("Over", size=150)
	pressKey = sprite_factory.from_text("Press a key to play.", color=DARKGRAY)

	gamesprite.position = WINDOWWIDTH//2 - gamesprite.size[0]//2, 10
	oversprite.position = WINDOWWIDTH//2 - oversprite.size[0]//2, gamesprite.size[1] + 35
	pressKey.position = WINDOWWIDTH - 200, WINDOWHEIGHT - 30

	sprite_renderer.render((gamesprite, oversprite, pressKey))

	ren.present()
	sdl2.SDL_Delay(500)
	check_for_key_press() # clear out any key presses in the event queue

	while True:
		if check_for_key_press():
			return

#return true if there's been a keypress
def check_for_key_press():
	ret = False
	for event in sdl2.ext.get_events():
		if event.type == sdl2.SDL_QUIT:
			shutdown()
		elif event.type == sdl2.SDL_MOUSEBUTTONUP:
			mousex, mousey = event.button.x, event.button.y
		elif event.type == sdl2.SDL_KEYDOWN:
			sym = event.key.keysym.sym
			ret = True
			if sym == sdl2.SDLK_ESCAPE:
				shutdown()
	return ret


def getRandomLocation():
	return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def drawScore(score):
	scoresprite = sprite_factory.from_text("Score: %s" % (score)) 
	scoresprite.position = WINDOWWIDTH - 120, 10
    #scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
	sprite_renderer.render(scoresprite)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        ren.fill((x, y, CELLSIZE, CELLSIZE), DARKGREEN)
        ren.fill((x+4, y+4, CELLSIZE-8, CELLSIZE-8), GREEN)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    ren.fill((x, y, CELLSIZE, CELLSIZE), RED)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
    	ren.draw_line((x, 0, x, WINDOWHEIGHT), DARKGRAY)
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
    	ren.draw_line((0, y, WINDOWWIDTH, y), DARKGRAY)


def shutdown():
	sdl2.ext.quit()
	sys.exit()

if __name__ == '__main__':
	main()
