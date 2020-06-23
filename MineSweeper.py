import random as rand
import sys
from PIL import Image, ImageTk
from tkinter import Tk, Frame, Canvas, ALL, Button, Label, Toplevel

class Cons:

    BOARD_HEIGHT = 500
    BOARD_WIDTH  = 500
    NUM_MINES    = 25
    GRID_RES     = 1
    GRID_SIZE    = 12
    OFFSET       = 50
    COL          = ['black', 'blue', 'green', 'red', 'purple', 'pink', 'brown', 'cyan']

    

class Board(Frame):

    def __init__(self, root):

        super().__init__(width=Cons.BOARD_WIDTH, height=Cons.BOARD_HEIGHT,
                         background="white", highlightthickness=0)

        self.root = root
        self.init_Game()


    def init_Game(self):
        
        self.score = 0

        # Initialise the grid. Include a ghost shell of zeros to facilitate 
        # calculation of # of mines next to a square
        self.grid = [0]*(Cons.GRID_SIZE + 2)**2
    
        # Actual index of first grid value
        init_Ind = Cons.GRID_SIZE + 3
        x = 0
        self.mine_Inds = []

        # Put mines in self.grid. mine represented by -1. 
        while x < Cons.NUM_MINES:

            mine_PosX = rand.randint(0, Cons.GRID_SIZE - 1)
            mine_PosY = rand.randint(0, Cons.GRID_SIZE - 1)
            self.grid[init_Ind + mine_PosX*(Cons.GRID_SIZE + 2) + mine_PosY] = -1
            
            # Check to see if mine has already been added in this position
            if [mine_PosX, mine_PosY] not in self.mine_Inds:
                self.mine_Inds.append([mine_PosX, mine_PosY])
                x += 1

        for ii in range(Cons.GRID_SIZE):

            for jj in range(Cons.GRID_SIZE):
                
                # To get actual ind, we have to navigate past the
                # ghost shell of zeroes surrounding the grid.
                ind = init_Ind + ii*(Cons.GRID_SIZE+2) + jj

                if self.grid[ind] != -1:

                    self.grid[ind] = self.Get_Num(ind)

        self.Trunc_Grid()
        self.Create_Objects()


    def Get_Num(self, ind):
        # Check the 3x3 grid around the index value for mines. Store the number of mines in count
        # return number of mines
        count = 0

        for ii in range(3):
            for jj in range(3):

                if self.grid[(ii-1)*(Cons.GRID_SIZE + 2) + (jj-1) + ind] == -1:
                    count += 1

        return count


    def Trunc_Grid(self):
        # Remove ghost layer of zeros from self.grid

        # Remove top and bottom rows of zeros
        del self.grid[0:Cons.GRID_SIZE + 2]
        del self.grid[-(Cons.GRID_SIZE + 2):]
        
        # Remove the right and left columns of zeros
        for ii in range(Cons.GRID_SIZE):

            del self.grid[-1 - ii*Cons.GRID_SIZE]
            del self.grid[-1 - (ii + 1)*Cons.GRID_SIZE]


    def Load_Images(self):

        try:
            self.ibomb = Image.open("head.png")
            self.ibomb.resize((50,50), Image.ANTIALIAS)
            self.bomb  = ImageTk.PhotoImage(self.ibomb)
                
        except IOError as e:

            print(e)
            sys.exit(1)

            
    def Print_Grid(self):   
        print('\n')
        for ii in range(Cons.GRID_SIZE):
            print('\n')
            for jj in range(Cons.GRID_SIZE):
                print('[%d]' % self.grid[ii*Cons.GRID_SIZE + jj], end ="")

        print('\n')
        

    def Create_Objects(self):

        self.tiles = []

        for ii in range(Cons.GRID_SIZE**2):
            
            self.tiles.append(Tile(self.root, self.grid[ii], ii))

    
            
            
class Tile():

    def __init__(self, root, val, ind):

        self.root = root
        self.val  = val 
        self.ind  = ind 
        self.button = Button(self.root, text = '', command = self.button_Press, 
                             width = Cons.GRID_RES*2, height = Cons.GRID_RES)
        self.button.grid( row = self.ind // Cons.GRID_SIZE, column = self.ind % Cons.GRID_SIZE )
            
    def button_Press(self):

        if self.val == 0:
            self.button.config(relief = 'sunken')

        elif self.val == -1:
            self.button.config(image = Cons.BOMB, relief = 'sunken', width = 18, height = 18)

            self.Gameover()

        else:
            self.button.config(text = str(self.val), relief = 'sunken', fg = Cons.COL[self.val + 1])

    def Gameover(self):

        GameOver = Toplevel()
        GameOver.geometry('200x200')

        can     = Canvas(GameOver, height = 200, width = 200)
        can.place(x=0,y=0)
        can.create_text(100, 50, text ='Game Over')

        res_but         = Button(GameOver, text = 'Restart', command = Restart )
        res_but_window  = can.create_window(100, 100, anchor='center', window = res_but)
        
        quit_but        = Button(GameOver, text = 'Quit', command = self.Quit )
        quit_but_window = can.create_window(100, 150, anchor='center', window = quit_but)
        
        GameOver.grab_set()
        

    def Quit(self):
        self.root.destroy()



def main():

    def Restart():
        root.destroy()
        root = Tk()
        Board(root)

    root = Tk()
    Board(root)
    Cons.ROOT.mainloop()


if __name__ == '__main__':
    main()




