from board import Board
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import matplotlib




class ChiApp:

    def __init__(self, radius = 5):
        self.board = Board(5)
        self.holes = self.board.get_holes()

    def exec(self):

        matplotlib.rcParams['toolbar'] = 'None' 
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.manager.set_window_title('Chinese Checker')
        self.fig.patch.set_facecolor('silver')

        x = []
        y = []
        colors = []
        for hole in self.holes :
            x.append(hole.x)
            y.append(hole.y)
            if hole.filled:
                colors.append('red')
            else:
                colors.append('gray')
        
        self.scatter = self.ax.scatter(x, y, picker = 3, s= 100, color = colors)
        self.ax.axis('equal')
        self.ax.set_box_aspect(1)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.hover)
        plt.axis("off")
        plt.show()

    def on_pick(self,event):
        i = int(event.ind)
        hole = self.holes[i]
        if event.mouseevent.button == 1:
            self.scatter._facecolors[event.ind,:] = mcolors.to_rgba_array('red')
            self.scatter._edgecolors[event.ind,:] = mcolors.to_rgba_array('red')
            hole.filled = True
        elif event.mouseevent.button == 3:
            self.scatter._facecolors[event.ind,:] = mcolors.to_rgba_array('gray')
            self.scatter._edgecolors[event.ind,:] = mcolors.to_rgba_array('gray')
            hole.filled = False
        self.fig.canvas.draw()
    
    def hover(self, event):
        if event.inaxes == self.ax:
            cont, ind = self.scatter.contains(event)
            if cont:
                ind = int(ind['ind'])
                hole = self.holes[ind]
                if hole.filled:
                    positions = []
                    hole.find_possible_positions(positions)
                    for suggestion in positions:
                        idx = suggestion.idx
                        self.scatter._facecolors[idx,:] = mcolors.to_rgba_array('yellow')
                        self.scatter._edgecolors[idx,:] = mcolors.to_rgba_array('yellow')
                    self.fig.canvas.draw_idle()
            else:
                for i, hole in enumerate(self.holes):
                    if hole.filled: 
                        self.scatter._facecolors[i,:] = mcolors.to_rgba_array('red')
                        self.scatter._edgecolors[i,:] = mcolors.to_rgba_array('red')
                    else:
                        self.scatter._facecolors[i,:] = mcolors.to_rgba_array('gray')
                        self.scatter._edgecolors[i,:] = mcolors.to_rgba_array('gray')
                
                self.fig.canvas.draw_idle()


if __name__ == "__main__":
    app = ChiApp()
    app.exec()
