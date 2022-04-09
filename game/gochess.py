import pygame
from pygame.locals import *

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((540,540))
        self.stop = False
        self.white = pygame.image.load('whitepiece.png')
        self.black = pygame.image.load('blackpiece.png')
        self.board = pygame.image.load('board.png')
        self.screen.blit(self.board,(0,0))
        self.empty = pygame.image.load('empty.png')
        self.turn = 0
        self.locdict = {}
        for i in range(121):
            if i in range(11) or i in range(101,121) or i%11 == 0 or i%11 == 10:
                self.locdict[i] == 'wall'
            else:
                self.locdict[i] = None
        self.event = pygame.event.wait()
        self.result = None
    
    def run(self):
        while not self.stop:
            for event in self.event:
                if event.type == 'MOUSEBUTTONDOWN':
                    pos = event.pos()
                    loc = [int(pos[0]/60), int(pos[1]/60)]
                    if self.locdict[loc[0]+1+(loc[1]+1)*11] == None: 
                        if self.turn%2 == 0:
                            self.locdict[loc[0]+1+(loc[1]+1)*11] = 'black'
                            self.screen.blit(self.black,(loc[0]*60,loc[1]*60))
                        else:
                            self.locdict[loc[0]+1+(loc[1]+1)*11] = 'white' 
                            self.screen.blit(self.white,(loc[0]*60,loc[1]*60))
                        self.eaten(loc)
                        self.toeat(loc)
                        self.turn+=1

    def eaten(self,loc):
        loc = [loc[0]+1, loc[1]+1]
        loclist = [loc]
        color = self.locdict[loc[0]+loc[1]*11]
        nei_loc = [[loc[0]-1,loc[1]],
                   [loc[0]+1,loc[1]],
                   [loc[0],loc[1]-1],
                   [loc[0],loc[1]+1]]
        nei_color = [self.locdict[l[0]+l[1]*11] for l in nei_loc]
                     
        while color in nei_color:
            for i in range(len(nei_color)):
                if nei_color[i] == color:
                    old_loc = loc
                    loc = nei_loc.pop(i)
                    loclist.append(loc)
                    nei_loc.append([[loc[0]-1,loc[1]],
                                     [loc[0]+1,loc[1]],
                                     [loc[0],loc[1]-1],
                                     [loc[0],loc[1]+1]])
                    nei_loc.pop(nei_loc.index(old_loc))
                    nei_loc = list(set(nei_loc))
                    nei_color = [self.locdict[l[0]+l[1]*11] for l in nei_loc]
        
        if None not in nei_color:
            for l in loclist:
                self.locdict[l[0]+l[1]*11] = None
                self.screen.blit(self.empty,((l[0]-1)*60,(l[1]-1)*60))
    
    def toeat(self,loc):
        loc = [loc[0]+1, loc[1]+1]
        color = self.locdict[loc[0]+loc[1]*11]
        if color == 'black':
            anti_color = 'white'
        else:
            anti_color = 'black'
        nei_loc = [[loc[0]-1,loc[1]],
                   [loc[0]+1,loc[1]],
                   [loc[0],loc[1]-1],
                   [loc[0],loc[1]+1]]
        nei_color = [self.locdict[l[0]+l[1]*11] for l in nei_loc]
        for i in range(4):
            if nei_color[i] == anti_color:
                self.eaten(nei_loc[i])
    
    def endcheck(self):
        self.stop = True
        bcnt, wcnt = 0,0
        for c in self.locdict:
            if c == 'black':
                bcnt+=1
            elif c == 'white':
                wcnt+=1
        if bcnt>wcnt:
            self.result = 'Black Won.'
        elif wcnt>bcnt:
            self.result = 'White Won.'
        else:
            self.result = 'Draw.'

    def showturn(self):
        if self.turn%2 == 0:
            return 'Next Is Black Turn.'
        else:
            return 'Next Is White Turn.' 
    
    def restart(self):
        self.__init__()
        self.run()

