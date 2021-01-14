
from array import *
import sys, pygame
import button

class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent, x, y):
        self.parent = parent
        self.x = x
        self.y = y

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Grid(object):
    EMPTY = 0
    BLOCK = 1
    BEGIN = 2
    END   = 3
    PATH_NODE = 4

    EMPTY_COLOR = 150, 150, 150
    BLOCK_COLOR = 20, 20, 20
    BEGIN_COLOR = 20, 200, 20
    END_COLOR = 20, 20, 200
    PATH_COLOR = 100, 100, 10


    def __init__(self, x, y, size, margin, offsetx, offsetybottom, offsetytop):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.path = []
        self.startx = -1
        self.starty = -1
        self.endx = -1
        self.endy = -1

        self.calculated = False

        self.buttons = {}

        self.buttons["reset"] = button.Button(500, 50, 200, 35, "Reset Board", 25, (150, 150, 150), True, (0, 0, 0), (200, 200, 200))
        self.buttons["emptyNode"] = button.Button(150, 10, size, size, "", 25, self.EMPTY_COLOR, False)
        self.buttons["blockNode"] = button.Button(150 + 10 + size, 10, size, size, "", 25, self.BLOCK_COLOR, False)
        self.buttons["startNode"] = button.Button(150 + 2*10 + 2*size, 10, size, size, "", 25, self.BEGIN_COLOR, False)
        self.buttons["endNode"] = button.Button(150 + 3*10 + 3*size, 10, size, size, "", 25, self.END_COLOR, False)
        self.buttons["selected"] = button.Button(150, 20 + size, size, size, "", 25, self.EMPTY_COLOR, False)
        self.buttons["calcPath"] = button.Button(500, 10, 200, 35, "Calculate Path", 25, (150, 150, 150), True, (0, 0, 0), (200, 200, 200))

        self.selected = 0
        self.running = True
        self.nodesX = x
        self.nodesY = y
        self.nodeSize = size
        self.nodeMargin = margin
        self.offsetX = offsetx
        self.offsetY = offsetybottom
        self.offsetYTop = offsetytop

        self.winSize = ((size + margin) * x + margin + 2 * offsetx), ((size + margin) * y + margin + offsetybottom + offsetytop)
        
        self.screen = pygame.display.set_mode(self.winSize)


        ## font below
        self.font = pygame.font.SysFont(None, 24)
        self.selectNodeText = self.font.render('Select Node:', True, (10, 10, 10))
        self.selectedText = self.font.render('Selected:', True, (10, 10, 10))
        
        
        self.grid = []
        for row in range(y):
            # For each row, create a list that will
            # represent an entire row
            self.grid.append([])
            # Loop for each column
            for column in range(x):
                # Add a the number zero to the current row
                self.grid[row].append(0)
    
    def loop(self):
        while self.running:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:
                    self.running = False
            
            if pygame.mouse.get_pressed()[0]:
                    self.getMouseClick(pygame.mouse.get_pos())

            self.screen.fill((200, 200, 255))
            
            pygame.draw.rect(self.screen, (0, 0, 0), [self.offsetX, self.offsetYTop,
                                                  (self.nodeSize + self.nodeMargin) * self.nodesX + self.nodeMargin,
                                                  (self.nodeSize + self.nodeMargin) * self.nodesY + self.nodeMargin])

            self.screen.blit(self.selectNodeText, (20, 20))
            self.screen.blit(self.selectedText, (20, 60))

            self.drawGrid()

            for key in self.buttons:
                self.buttons[key].draw(self.screen, pygame.mouse.get_pos())

            self.clock.tick(60)
            pygame.display.flip()

    def drawGrid(self):
        for row in range(self.nodesY):
            for column in range(self.nodesX):
                color = 0, 0, 0
                nodeType = self.grid[row][column] 
                if (nodeType == self.EMPTY):
                    color = self.EMPTY_COLOR
                elif nodeType == self.BLOCK:
                    color = self.BLOCK_COLOR
                elif nodeType == self.BEGIN:
                    color = self.BEGIN_COLOR
                elif nodeType == self.END:
                    color = self.END_COLOR
                elif nodeType == self.PATH_NODE:
                    color = self.PATH_COLOR

                pygame.draw.rect(self.screen,
                                 color,
                                 [self.offsetX + (self.nodeSize + self.nodeMargin) * column + self.nodeMargin,
                                  (self.offsetYTop) + (self.nodeSize + self.nodeMargin) * row + self.nodeMargin,
                                  self.nodeSize,
                                  self.nodeSize])

    def getMouseClick(self, p):

        x, y = p

        # Calculate Path
        if(self.buttons["calcPath"].isOver(p)):
            self.calcRoute()
        
        # Reset Button
        if(self.buttons["reset"].isOver(p)):
            self.reset_board()

        # Empty Node
        if (self.buttons["emptyNode"].isOver(p)):
            self.selected = self.EMPTY
            self.buttons["selected"].bg = self.EMPTY_COLOR
        
        # Block Node
        if (self.buttons["blockNode"].isOver(p) == True):
            self.selected = self.BLOCK
            self.buttons["selected"].bg = self.BLOCK_COLOR
        
        # Start Node
        if (self.buttons["startNode"].isOver(p)):
            self.selected = self.BEGIN
            self.buttons["selected"].bg = self.BEGIN_COLOR
        # End Node
        if (self.buttons["endNode"].isOver(p)):
            self.selected = self.END
            self.buttons["selected"].bg = self.END_COLOR
            
        
        col = int((x - self.offsetX - self.nodeMargin) / (self.nodeSize + self.nodeMargin))
        row = int((y - self.offsetYTop - self.nodeMargin) / (self.nodeSize + self.nodeMargin))

        if (col < 0 or col > self.nodesX - 1 or row < 0 or row > self.nodesY - 1):
            return

        if (row == self.startx and col == self.starty):
            if (self.selected == self.EMPTY):
                self.startx = -1
                self.starty = -1
                self.clearPath()
            else:
                return

        if (row == self.endx and col == self.endy):
            if (self.selected == self.EMPTY):
                self.endx = -1
                self.endy = -1
                self.clearPath()
            else:
                return

        if(self.selected == self.BEGIN):
            if(self.startx != -1 and self.starty != -1):
                self.grid[self.starty][self.startx] = self.EMPTY
            self.startx = col
            self.starty = row
            self.calculated = False
            self.clearPath()

        if(self.selected == self.END):
            if(self.endx != -1 and self.endy != -1):
                self.grid[self.endy][self.endx] = self.EMPTY
            self.endx = col
            self.endy = row
            self.calculated = False
            self.clearPath()

        if(self.selected == self.BLOCK or self.selected == self.EMPTY):
            if self.isOnPath(col, row):
                self.clearPath()
        self.grid[row][col] = self.selected

    def reset_board(self):
        self.startx = -1
        self.starty = -1
        self.endx = -1
        self.endy = -1
        self.selected = self.EMPTY
        self.path = []
        self.calculated = False
        self.buttons["selected"].bg = self.EMPTY_COLOR
        for row in range(self.nodesY):
            for column in range(self.nodesX):
                self.grid[row][column] = self.EMPTY

    def calcRoute(self):
        print("start x: " + str(self.startx))
        print("start y: " + str(self.starty))
        print("end x: " + str(self.endx))
        print("end y: " + str(self.endy))
        print("nodes x: " + str(self.nodesX))
        print("nodes y: " + str(self.nodesY))

        if(self.startx >= 0 and self.startx < self.nodesX
            and self.starty >= 0 and self.starty < self.nodesY
            and self.endx >= 0 and self.endx < self.nodesX
            and self.endy >= 0 and self.endy < self.nodesY):       
            self.path = self.astar()
            self.calculated = True
            #print(path)
            if(self.path):
                for p in self.path:
                    self.grid[p[1]][p[0]] = self.PATH_NODE
                    self.grid[self.starty][self.startx] = self.BEGIN
                    self.grid[self.endy][self.endx] = self.END
        else:
            print("bounds")

    def isOnPath(self, x, y):
        if self.path:
            for p in self.path:
                if(x == p[0] and y == p[1]):
                    return True
        else:
            return False

    def clearPath(self):
        for p in self.path:
            self.grid[p[1]][p[0]] = self.EMPTY
            self.path = []
        if(self.startx >= 0 and self.starty >= 0):
            self.grid[self.starty][self.startx] = self.BEGIN

        if(self.endx >= 0 and self.endy >= 0):
            self.grid[self.endy][self.endx] = self.END

    def astar(self): ## A* algorithm
        openSet = list()
        closedSet = list()

        nullNode = (None, -1, -1)
        start_node = Node(nullNode, self.startx, self.starty)
        end_x = self.endx
        end_y = self.endy

        openSet.append(start_node)
        
        while len(openSet) > 0:

            q = openSet[0]
            toPop = 0
            for i in range(len(openSet)):
                if openSet[i].f < q.f:
                    q = openSet[i]
                    toPop = i

            openSet.pop(toPop)

            offsets = [[0, 1], [1, 0], [0, -1], [-1, 0]]

            for i in range(len(offsets)):

                x = q.x + offsets[i][0] 
                y = q.y + offsets[i][1]
                if(x < 0 or x >= self.nodesX or y < 0 or y >= self.nodesY):
                    continue
                if(self.grid[y][x] == self.BLOCK):
                    continue
                #print("Loc: [ " + str(x) + " , " + str(y) + " ]")

                if x == end_x and y == end_y:
                    print("path found")
                    trace = q # Node
                    ret = list()
                    while not (trace.x == self.startx and trace.y == self.starty):
                        ret.append((trace.x, trace.y))
                        trace = trace.parent
                    return ret

                temp = Node(q, x, y)
                temp.g = 1
                temp.h = abs(temp.x - end_x) + abs(temp.y - end_y)
                temp.f = temp.g + temp.h

                skip = False
                for n in openSet:
                    if(n.x == temp.x and n.y == temp.y):
                        if(n.f <= temp.f):
                            skip = True
                for n in closedSet:
                    if(n.x == temp.x and n.y == temp.y):
                        if(n.f <= temp.f):
                            skip = True
                    
                if skip == False:
                    #print("Inserted")
                    openSet.append(temp)
                #else:
                #    print("skipped")

            closedSet.append(q);
        print("Destination blocked")
