# -*- coding: utf-8 -*-

import os, sys
import msvcrt
import random
from copy import deepcopy
from collections import defaultdict


DIRECT_4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIRECT_8 = ((-1, -1), (-1, 0), (-1, 1), (0, 1), 
            (1, 1),   (1, 0),  (1, -1), (0, -1))

# OBJMAP = {0: ' ', 1: '@', 9: 'p', 2: '$', 'split': ' '}
OBJMAP = {0: '  ', 1: u'█', 9: u'え', 2: '$', 'split': ''}
CONTROL = {'\xe0H': (-1, 0), '\xe0P': (1, 0), 
           '\xe0K': (0, -1), '\xe0M': (0, 1)}


class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.mz = None
        self.mz_obj = None

    def generate(self):
        w, h = self.width, self.height
        def get_neighbor(p, directions):
            constraint = lambda p: 0 < p[0] < h-1 and 0 < p[1] < w-1
            plist = [(p[0]+i, p[1]+j) for i,j in directions]
            return set(filter(constraint, plist))

        maze = [[1] * w for _ in range(h)]
        to_search = [(random.randint(1, h-1), random.randint(1, w-1))]
        while to_search:
            cur_p = to_search[-1]
            maze[cur_p[0]][cur_p[1]] = 0
            neighbors = [(i,j) for i,j in get_neighbor(cur_p, DIRECT_4) if maze[i][j]]
            
            available = []
            for p in neighbors:
                new_neighs = get_neighbor(p, DIRECT_8).difference(get_neighbor(cur_p, DIRECT_4))
                if sum([maze[i][j] == 0 for i,j in new_neighs]) <= 1:
                    available.append(p)
            
            if available:
                to_search.append(random.choice(available))
            else:
                to_search.pop()
        self.mz = maze
        return maze

    def generate_objects(self, n = 5):
        xlim, ylim = len(self.mz), len(self.mz)
        maze = deepcopy(self.mz)
        pi, pj = (random.randrange(1, xlim), random.randrange(1, ylim))
        while maze[pi][pj]:
            pi, pj = (random.randrange(1, xlim), random.randrange(1, ylim))
        maze[pi][pj] = 9
        self.mz_obj = maze
        return maze

    def move(self, command):
        if command not in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            return

        pi, pj = self.objs[9].pop()
        qi = pi + command[0]
        qj = pj + command[1]
        if 1 <= qi < self.height - 1 and 1 <= qj < self.width - 1 and self.mz_obj[qi][qj] == 0:
            self.mz_obj[pi][pj] = 0
            self.mz_obj[qi][qj] = 9

    def strformat(self, mztype='o'):
        if mztype == 'r':
            show = [map(OBJMAP.get, r) for r in self.mz]
            return '\n'.join(OBJMAP['split'].join(line) for line in show)
        elif mztype == 'o':
            show = [map(OBJMAP.get, r) for r in self.mz_obj]
            return '\n'.join(OBJMAP['split'].join(line) for line in show)

    def show(self, mztype='o'):
        if mztype == 'r':
            show = [map(OBJMAP.get, r) for r in self.mz]
            for line in show:
                print OBJMAP['split'].join(line)
        elif mztype == 'o':
            show = [map(OBJMAP.get, r) for r in self.mz_obj]
            for line in show:
                print OBJMAP['split'].join(line)

    @property
    def objs(self):
        output = defaultdict(set)
        for i,r in enumerate(self.mz_obj):
            for j,n in enumerate(r):
                if n > 1:
                    output[n].add((i, j))
        return output

    
def move(maze, command):
    xlim, ylim = maze.height, maze.width
    mz, objs = maze.mz_obj, maze.objs

    if command not in CONTROL:
        return maze
    
    pi, pj = objs[9].pop()
    qi = pi + CONTROL[command][0]
    qj = pj + CONTROL[command][1]
    if 1 <= qi < xlim - 1 and 1 <= qj < ylim - 1 and mz[qi][qj] == 0:
        mz[pi][pj] = 0
        mz[qi][qj] = 9
    

def main():
    mz = Maze(30, 20)
    mz.generate()
    mz.generate_objects()

    command = ''
    while True:
        os.system("cls")
        move(mz, command)
        mz.show()
        
        ch = msvcrt.getch()
        # print [ch]
        if ch in 'q|Q|\x1b':
            print "MazeRunner Exit."
            break
        else:
            command = command[-1] + ch if len(command) else ch

        if command not in CONTROL:
            continue
        else:
            print CONTROL[command]

if __name__=='__main__':
    main()