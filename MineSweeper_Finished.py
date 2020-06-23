import random as rand
import sys
import time
import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

class Cons:

    BOARD_HEIGHT = 500
    BOARD_WIDTH  = 500
    COL          = ['black', 'blue', 'green', 'red', 'purple', 'cyan', 'brown', 'pink']


class Grid():
    # Class which generates a minesweeper board given by (supplied by the user in Setup)
    # width, height and number of mines

    def __init__(self, width, height, num_Mines):

        self.height    = height 
        self.width     = width
        self.num_Mines = num_Mines
        
        self.Make_Grid()


    def Make_Grid(self):

        # Initialise the grid. Include a ghost shell of -2's to facilitate 
        # calculation of # of mines next to a square
        self.matrix = [-2]*(self.height + 2)*(self.width + 2)

        # Actual index of first grid value
        init_Ind = self.width + 3
        x = 0
        self.mine_Inds = []

        # Put mines in self.grid. mine represented by -1. 
        while x < self.num_Mines:

            mine_PosX = rand.randint(0, self.width - 1)
            mine_PosY = rand.randint(0, self.height - 1)
            self.matrix[init_Ind + mine_PosY*(self.width + 2) + mine_PosX] = -1
            
            # Check to see if mine has already been added in this position
            if [mine_PosX, mine_PosY] not in self.mine_Inds:
                self.mine_Inds.append([mine_PosX, mine_PosY])
                x += 1

        for ii in range(self.height):

            for jj in range(self.width):
                
                # To get actual ind, we have to navigate past the
                # ghost shell of zeroes surrounding the grid.
                ind = init_Ind + ii*(self.width + 2) + jj

                if self.matrix[ind] != -1:

                    self.matrix[ind] = self.Get_Num(ind)

        
        self.clear_areas = [[]]
        self.num_areas   = 0

        for ii in range(self.height):

            for jj in range(self.width):

                # To get actual ind, we have to navigate past the
                # ghost shell of zeroes surrounding the grid.
                ind = init_Ind + ii*(self.width + 2) + jj

                if self.matrix[ind] == 0:
                    
                    found = 0 
                    for kk in range(self.num_areas):
                        if ind in self.clear_areas[kk]:
                            found = 1
                    
                    if found == 0:
                        self.Get_Clear_Areas(ind, self.num_areas)

                    # if we have broken out of the recursive function Get_Clear_Areas, then we have
                    # found the entire conjoined clear area and we need to move onto the next one.
                    if len(self.clear_areas[self.num_areas]) != 0:
                        self.num_areas += 1
                        self.clear_areas.append([])

        self.Trunc_Grid()
        self.Coord_Transform()


    def Get_Num(self,ind):
        # Check the 3x3 grid around the index value for mines. Store the number of mines in count
        # return number of mines
        count = 0

        for ii in range(3):
            for jj in range(3):

                if self.matrix[(ii-1)*(self.width + 2) + (jj-1) + ind] == -1:
                    count += 1

        return count

    
    def Trunc_Grid(self):
        # Remove ghost layer of zeros from self.grid

        # Remove top and bottom rows of zeros
        del self.matrix[0:self.width + 2]
        del self.matrix[-(self.width + 2):]
        
        # Remove the right and left columns of zeros
        for ii in range(self.height):

            del self.matrix[-1 - ii*self.width]
            del self.matrix[-1 - (ii + 1)*self.width]

    
    def Print_Grid(self):   
        print('\n')
        for ii in range(self.height):
            print('\n')
            for jj in range(self.width):
                print('[%d]' % self.matrix[ii*self.width + jj], end ="")

        print('\n')


    def Get_Clear_Areas(self, ind, cl_ind):

        # Check the 3x3 grid around the index value for whitespace. Store the indicies in 
        # self.clear_areas[cl_ind]

        for ii in range(3):
            for jj in range(3):
                new_ind = (ii-1)*(self.width + 2) + (jj-1) + ind

                # add index of new whitespace to self.clear_areas if it is not already in it
                if self.matrix[new_ind] == 0 and new_ind not in self.clear_areas[cl_ind]:

                    self.clear_areas[cl_ind].append(new_ind)
                    # recursively call on the new whitespace value to find the whole clear area
                    self.Get_Clear_Areas(new_ind, cl_ind)
                    

    def Coord_Transform(self):
        # get clear areas in the correct coordinates (i.e after the ghost layer has been removed)

        for ii in range(len(self.clear_areas)):

            for jj in range(len(self.clear_areas[ii])):

                self.clear_areas[ii][jj] -= self.width + 3
                row_num = self.clear_areas[ii][jj] // (self.width + 2)
                self.clear_areas[ii][jj] -= row_num*2 


class Board(tk.Frame):
    # Class to turn the Grid into the main game GUI

    def __init__(self, chart, root):
        super().__init__(width=Cons.BOARD_WIDTH, height=Cons.BOARD_HEIGHT,
                         background="white", highlightthickness=0)

        self.root             = root
        self.chart            = chart
        self.num_opened_tiles = 0
        self.grid(row = self.chart.height, column = self.chart.width)

        self.Load_Images()
        self.Draw_Board()
        

    def Draw_Board(self):
        
        # Storage for button widgets
        self.tiles = []

        for ii in range(self.chart.height):

            for jj in range(self.chart.width):
                
                # Make buttons
                tile = tk.Button(self, text = '', 
                                command = lambda ind = ii*self.chart.width + jj: self.Tile_Press(ind), 
                                width = 2, height = 1)
                # Bind right click to each tile 
                tile.bind('<Button-3>', lambda event, ind = ii*self.chart.width + jj: self.Flag(ind))
                tile.grid(row = jj, column = ii)
                self.tiles.append(tile)

    
    def Tile_Press(self, ind):

        self.num_opened_tiles += 1
        
        # Clicked on an empty tile
        if self.chart.matrix[ind] == 0:
           
            for ii in range(len(self.chart.clear_areas)):
                
                # Find which clear area the tile belongs to 
                try:
                    self.chart.clear_areas[ii].index(ind)
                    self.num_opened_tiles -= 1

                    # "Press" the whole clear area
                    for jj in self.chart.clear_areas[ii]:
                        self.num_opened_tiles += 1
                        self.tiles[jj].config(relief = 'sunken', state = 'disabled')
                        time.sleep(0.01)
                        self.update_idletasks()
                    break
                
                except ValueError:
                    pass
                    
        # Clicked on bomb
        elif self.chart.matrix[ind] == -1:
            self.tiles[ind].config(text = '', image = self.bomb, relief = 'sunken', 
                                   compound = 'center',
                                   height = 18, width = 18 )
            self.update_idletasks()
            time.sleep(0.3)
            self.Gameover()

        # Clicked on number tile
        else:
            self.tiles[ind].config(text = str(self.chart.matrix[ind]), relief = 'sunken', 
                                   disabledforeground = Cons.COL[self.chart.matrix[ind] - 1],
                                   state = 'disabled')
        

        if self.num_opened_tiles == self.chart.width*self.chart.height - self.chart.num_Mines:
            self.Congratulations()


    def Gameover(self):
        # Make a new window with a restart and quit button when a bomb is clicked on 
        
        self.gameover_window = tk.Toplevel()
        self.gameover_window.title('GameOver')
        self.gameover_window.geometry('200x200')

        frame = tk.Frame(self.gameover_window, height = 100, width = 100)
        frame.grid(row = 7, column = 3)

        gameover_label = tk.Label(frame, text = 'Game Over', font = ('arial', 14))
        gameover_label.grid(row = 2, column = 2, padx = 50, pady = 20)

        restart_button = tk.Button(frame, command = self.Restart, text = 'Restart')
        restart_button.grid(row = 4, column = 2, pady = 20)

        quit_button    = tk.Button(frame, command = self.Quit, text = 'Quit')
        quit_button.grid(row = 6, column = 2, pady = 20)

        self.gameover_window.grab_set()


    def Restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)


    def Quit(self):
        self.root.destroy()


    def Flag(self, ind):
        # Event set to trigger on the right click on a tile. will change the background 
        # between a flag and no flag

        if self.tiles[ind].cget('state') != 'disabled':
            im = self.tiles[ind].cget('image')
            if im == '':
                self.tiles[ind].config(image = self.flag, width = 18, height = 18)
            else:
                self.tiles[ind].config(text = '', image = '', width = 2, height = 1)


    def Congratulations(self):
        messagebox.showinfo('Winner', 'Winner')
        self.root.destroy()

    
    def Load_Images(self):

        self.ibomb = Image.open('bomb.png')
        self.bomb  = ImageTk.PhotoImage(self.ibomb)
        self.iflag = Image.open('flag.png')
        self.flag  = ImageTk.PhotoImage(self.iflag)


class Setup(tk.Frame):
    # Class to make the initial input Gui usd by the user to setup the game

    def __init__(self, root):

        super().__init__(width = 100, height = 100,
                         background="white", highlightthickness=0)
        self.grid(row = 10, column = 10)
        self.root = root
        self.Init_Setup()


    def Init_Setup(self):
        
        # Validation command to ensure only integers can be put in the entry widgets
        vcmd = (self.register(self.onValidate), '%S')

        # Width entry 
        self.w_lab = tk.Label(self, text = 'Enter Width:')
        self.w_lab.grid(row = 3, column = 4)
        self.width_entry  = tk.Entry(self, validate="key", validatecommand=vcmd)
        self.width_entry.grid(row = 3, column = 6, sticky = 'e')
        self.width_entry.focus_set()
        
        # Height entry 
        self.h_lab = tk.Label(self, text = 'Enter Height:')
        self.h_lab.grid(row = 5, column = 4)
        self.height_entry = tk.Entry(self, validate="key", validatecommand=vcmd)
        self.height_entry.grid(row = 5, column = 6, sticky = 'e')
        
        # Num_Mines entry 
        self.n_lab = tk.Label(self, text = 'Enter Number of Mines:')
        self.n_lab.grid(row = 7, column = 4)
        self.num_mines    = tk.Entry(self, validate="key", validatecommand=vcmd)
        self.num_mines.grid(row = 7, column = 6, sticky = 'e')

        # Generate button
        self.gen_but = tk.Button(self, text = 'Generate')
        self.gen_but.grid(row = 9, column = 5)
        self.gen_but.bind('<Button-1>', self.Make_MS)
        self.root.bind('<Return>', self.Make_MS)


    def onValidate(self,S):
        # Ensure only integers can be typed

        try:
            int(S)
            return True
        
        except ValueError:
            return False

        
    def Make_MS(self,*args):
        # Draw the board and ensure that the values in the entry boxes are sensible

        w = int(self.width_entry.get())
        h = int(self.height_entry.get())
        n = int(self.num_mines.get())

        if w > 20 or w <= 1:
            messagebox.showinfo('Error', 'Width must be between 2 and 20')
            
        elif h > 20 or h <= 1:
            messagebox.showinfo('Error', 'Height must be between 2 and 20')

        elif n > w*h-1 or n < 1:
            messagebox.showinfo('Error', 'Number of mines must be between 1 and (width*height - 1)')

        else:
            G = Grid(w, h ,n)
            Board(G, self.root)
            self.destroy()


def main():
    root = tk.Tk()
    root.title('Minesweeper')
    Setup(root)
    root.mainloop()


if __name__ == '__main__':
    main()
