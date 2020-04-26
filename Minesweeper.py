#MineSweeper
from tkinter import *
from random import randrange, randint

class Tile:
    def __init__(self, value = 0, hide = True, flag = 0):
        self.value = value
        self.hide = hide
        self.flag = flag

class Minesweeper:
    def __init__(self):
        window = Tk()
        window.title("Minesweeper")

        self.size = 20
        self.column = 24
        self.row = 20
        
        self.textColor = {1:"#0E25F9", 2:"#157C17", 3:"#FB101D", 4:"#050D72", 5:"#7E1F22",
                          6:"#1A807F", 7:"#020202", 8:"#7C7C7C"}
        
        self.width = self.column * self.size
        self.height = self.row * self.size

        #Create Flag counter and Restart button
        frame = Frame(window)
        frame.pack()

        Label(frame, text = "Flags:").pack(side = LEFT)      
        self.flagVar = StringVar()
        Label(frame, textvariable = self.flagVar).pack(side = LEFT)

        Button(frame, text = "Restart", command = self.initialize).pack(side = LEFT)

        #Create canvas for minefield        
        self.canvas = Canvas(window, width = self.width,
                             height = self.height)
        self.canvas.pack()

        #Bind mouse clicks
        self.canvas.bind("<Button-1>", self.processMouseEvent)
        self.canvas.bind("<Button-2>", self.processMouseEvent)                

        #Draw blank tiles
        for i in range(self.row):
            for j in range(self.column):
                x = j * self.size
                y = i * self.size
                self.canvas.create_rectangle(x, y, x + self.size, y + self.size)
                
        self.initialize()

        window.mainloop()

    def initialize(self):
        #Reset parameter
        self.grid = []
        self.mineSet = set()
        self.flagSet = set()

        self.isOver = False
        self.numberOfFlags = 99
        self.flagVar.set(self.numberOfFlags)
        
        #Generate mines
        while len(self.mineSet) < self.numberOfFlags:
            i = randrange(self.row)
            j = randrange(self.column)
            self.mineSet.add((i, j))
            
        for i in range(self.row):
            self.grid.append([])
            for j in range(self.column):
                if (i, j) not in self.mineSet:
                    count = self.getHint(i, j)
                    self.grid[i].append(Tile(count))   #0 means hidden, 1 means revealed
                else:
                    self.grid[i].append(Tile(-1))

        for i in range(self.row):
            for j in range(self.column):
                index = i * self.column + j + 1
                self.canvas.itemconfigure(index, fill = "#629AC2", outline = "#477FAC")

        self.canvas.delete("flag", "mine", "text")
   
    def getHint(self, row, col):
        count = 0
        for i in range(-1, 2):
            if (row + i, col - 1) in self.mineSet:
                count += 1
            if (row + i, col + 1) in self.mineSet:
                count += 1

        if (row - 1, col) in self.mineSet:
            count += 1
        if (row + 1, col) in self.mineSet:
            count += 1        

        return count

    def processMouseEvent(self, event):
        row = event.y // self.size
        col = event.x // self.size

        if self.isOver == False:
            if self.grid[row][col].hide == True:
                if event.num == 1:
                    if self.grid[row][col].flag == 0:
                        self.showTile(row, col)
                elif event.num == 2:
                    if self.grid[row][col].flag == 0:
                        self.numberOfFlags -= 1
                        self.flagSet.add((row, col))
                        self.grid[row][col].flag = self.createFlag(col * self.size, row * self.size, self.size)
                    else:
                        self.canvas.delete(self.grid[row][col].flag)
                        self.grid[row][col].flag = 0
                        self.numberOfFlags += 1
                        self.flagSet.remove((row, col))
        self.flagVar.set(self.numberOfFlags)

    def showTile(self, row, col):
        value = self.grid[row][col].value
        
        #Clear flag
        if self.grid[row][col].flag != 0:
            self.deleteFlag(row, col)
            
        if self.grid[row][col].hide == True:
            #Reveal tile
            self.grid[row][col].hide = False
            index = row * self.column + col + 1
            self.canvas.itemconfigure(index, fill = "#E7E7E7", outline = "#D9D9D9")
            
            if value == 0: #Empty tile
                if row > 0:
                    self.showTile(row - 1, col)
                if row < self.row - 1:
                    self.showTile(row + 1, col)
                if col > 0:
                    self.showTile(row, col - 1)
                if col < self.column - 1:
                    self.showTile(row, col + 1)
            elif value == -1: #Mine
                self.createMine(col * self.size, row * self.size, self.size)
                self.isOver = True
                self.showMines()
                del self.grid
                del self.mineSet
                del self.flagSet
            else: #Hint
                self.canvas.create_text(col * self.size + self.size / 2,
                                        row * self.size  + self.size / 2,
                                        text = str(value), fill = self.textColor[value], tags = "text")                

    def showMines(self):
        mines = self.mineSet - self.flagSet #Unflagged mines
        for m in mines:
            self.canvas.after(20)
            self.canvas.update()
            self.createMine(m[1] * self.size, m[0] * self.size, self.size)

        flags = self.flagSet - (self.flagSet & self.mineSet) #False flags
        for f in flags:
            self.canvas.after(20)
            self.canvas.update()
            self.canvas.delete(self.grid[f[0]][f[1]].flag)
            self.createX(f[1] * self.size, f[0] * self.size, self.size)
                
    def createFlag(self, x, y, size):
        s = size // 6
        return self.canvas.create_polygon(x + 2 * s, y + s,
                                          x + 5 * s, y + 2 * s,
                                          x + 2 * s, y + 3 * s,
                                          x + 2 * s, y + 5 * s,
                                          fill = "red", outline = "red", tags = "flag")

    def deleteFlag(self, row, col):          
        self.canvas.delete(self.grid[row][col].flag)
        self.grid[row][col].flag = 0
        self.numberOfFlags += 1
        self.flagSet.remove((row, col))
        
    def createMine(self, x, y, size):
        s = size // 6
        self.canvas.create_oval(x + s, y + s,
                                       x + 5 * s, y + 5 * s,
                                       fill = "black", tags = "mine")
    def createX(self, x, y, size):
        s = size // 6
        self.canvas.create_line(x + s, y + s, x + 5 * s, y + 5 * s, fill = "red", tags = "flag")
        self.canvas.create_line(x + 5 * s, y + s, x + s, y + 5 * s, fill = "red", tags = "flag")

    
Minesweeper()
    
