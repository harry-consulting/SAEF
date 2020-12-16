import os
import random
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

class ColorGenerator:
    def generate(self, number_of_colors):
        if number_of_colors == 0:
            return 0
        n = number_of_colors
        ret = []
        r = int(random.random() * 256)
        g = int(random.random() * 256)
        b = int(random.random() * 256)
        step = 256 / n
        for i in range(n):
            r += step
            g += step
            b += step
            r = int(r) % 256
            g = int(g) % 256
            b = int(b) % 256
            ret.append("rgb(" + str(r) + "," + str(g) + "," + str(b) + ")")

        return ret

def index_exist(index, lst):
    return 0 <= index < len(lst)

def is_null(value):
    return True if value == 'YES' else False
