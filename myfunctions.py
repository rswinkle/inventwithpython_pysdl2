import sdl2.ext
import sdl2
from sdl2 import sdlgfx

from random import randint


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
	#test seems to indicate that I don't



WIDTH = 640
HEIGHT = 480

BLACK = sdl2.ext.Color(  0,   0,   0)
WHITE = sdl2.ext.Color(255, 255, 255)
RED   = sdl2.ext.Color(255,   0,   0)
GREEN = sdl2.ext.Color(  0, 255,   0)
BLUE  = sdl2.ext.Color(  0,   0, 255)

colors = [BLACK, WHITE, RED, GREEN, BLUE]


def main():
    sdl2.ext.init()

    window = sdl2.ext.Window("testing", size=(WIDTH, HEIGHT))
    window.show()

    ren = sdl2.ext.Renderer(window)


    for i in range(100000):
        points = [(randint(0, WIDTH), randint(0, HEIGHT)) for i in range(randint(3, 10))]
        draw_polygon(ren.renderer, points, colors[randint(0, 4)])
        ren.present()


if __name__ == '__main__':
	main()
