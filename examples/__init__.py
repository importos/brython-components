from . import helloworld
from . import timer
from . import filtered_list


examples_modules = [helloworld, timer, filtered_list]



examples_list = [(getattr(x, 'TITLE'), getattr(x, 'CODE')) for x in examples_modules]
