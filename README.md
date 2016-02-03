Invent With Python ported to PySDL2
===================================

This is a project aiming to port all the code/games from the book
["Making Games with Python & Pygame"](http://inventwithpython.com/pygame/chapters/) by Al Sweigart
from pygame to PySDL2.

## Why?

Well, I'm mostly a C/C++ programmer and I use SDL2 for my games/demos and
I wanted to be able to prototype in python with a library that'd make
it very easy to go from that to C.  PySDL2, while it does have some
great convenience classes/API's in the sdl2.ext, it's not hard to look
into the source and see what they're actually doing.  In addition it has
the sdl2 module, which is a straight 1:1 wrapper of SDL2, as well as
1:1 wrappers of SDL2 libraries like SDL2_mixer, SDL2_gfx and SDL2_ttf.
This design also makes using PySDL2 a great way to learn the SDL2
API and related libraries in general.

Another advantage of PySDL2 is that it's public domain/CC0/zlib instead of LGPL.

Look [here](https://pysdl2.readthedocs.org/en/latest/tutorial/pygamers.html)
for more details on the differences between Pygame and PySDL2


## Status
I've ported the first 8 projects, though the first 3 hardly count being so simple.
They all (should) work with python 2.7 and python 3.x though I think I may drop
python 2 in the future.  They're mostly straight ports not redesigns/reimplementations,
so it's easy to compare/learn (I've left all the pygame versions in the repo).  I have
about 7 more games to go and various improvements in the first half and general maintenance.

## License
All original content/code is copyrighted by Al Sweigart and as you can see
at the top of his py files, is BSD licensed.  All my code is public domain,
fallback to MIT/BSD.  I may change/expand/formalize the fallback later but
take it, do whatever you want with it, is the gist if public domain doesn't
work obviously.

### References/Sources
http://inventwithpython.com/pygame/chapters/

https://bitbucket.org/marcusva/py-sdl2/overview

https://pysdl2.readthedocs.org/en/latest/#
