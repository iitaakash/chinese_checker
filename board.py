import random
import math


# Class for hole on the Board
# Hole Neighbors defined in direction order :
#     2  1
#    3     0
#     4  5

class Hole:
    def __init__(self, x = 0, y = 0, radius = 0, filled = False):
        self.idx = -1
        self.x = x
        self.y = y
        self.radius = radius
        self.filled = filled
        self.neigh = [None, None, None, None, None, None]
    
    def shape(self):
        out = []
        for i in range(6):
            count = 1
            hole = self
            while hole.neigh[i] is not None:
                hole = hole.neigh[i]
                count = count + 1
            out.append(count)
        return tuple(out)


    def find_possible_positions(self, postions = [], include_adj = False):
        
        hole = self

        size = hole.shape()

        if hole not in postions:
            postions.append(hole)
        
        if hole.idx == postions[0].idx:
            hole.filled = False

        for i in range(0, 6):
            first_found = False
            for j in range(1,size[i]):
                if hole[i,j].filled == True and (2*j) < size[i]:
                    gaps = True
                    for k in range(j+1, 2*j):
                        if hole[i,k].filled == True:
                            gaps = False
                            break
                    if gaps and hole[i,2*j].filled == False and hole[i,2*j] not in postions:
                        postions.append(hole[i,2*j])
                        hole[i,2*j].find_possible_positions(postions)
                    first_found = True
                    break
        
        
        if hole.idx == postions[0].idx:
            hole.filled = True
        
        # first node
        if include_adj:
            if hole.idx == postions[0].idx:
                for nbr in hole.neigh:
                    if nbr is not None:
                        if not nbr.filled:
                            if nbr not in postions:
                                postions.append(nbr)
                postions.pop(0)




    def __getitem__(self, pos):
        x, y = pos

        hole = self
        for i in range(0, y): 
            hole = hole.neigh[x]
            if hole is None:
                raise Exception("Out of Bounds")
        return hole

    
    def create_neighbors(self, filled = False, common_neighbors = []):
        out = []
        create = False
        for n in self.neigh:
            if n is None:
                create = True
                break
        
        if not create:
            print("I am out")
            return  out
        
        radius = self.radius + 1
        edge = 1
        delta = 60.0
        for i in range(0, 6):
            if self.neigh[i] is not None: 
                continue

            deg = delta * i
            angle = math.radians(deg)
            x_pos = self.x + edge * math.cos(angle)
            y_pos = self.y + edge * math.sin(angle)
            hole = Hole(x = x_pos, y = y_pos, radius = radius, filled = filled)

            if len(common_neighbors):
                common = 0
                for cnbr in common_neighbors:
                    if math.isclose(hole.distance(cnbr) , 1.0) and ( not math.isclose(hole.distance(cnbr) , 0.0) ):
                        common = common + 1
                if common < 2:
                    continue

            for nbr in self.neigh:
                if nbr is None:
                    continue
                if math.isclose(hole.distance(nbr) , 1.0):
                    angle = hole.angle(nbr)
                    if angle == -1:
                        print("angle error")
                        continue
                    if hole.neigh[angle] is None:
                        hole.neigh[angle] = nbr
                    new_angle = (angle + 3) % 6
                    if nbr.neigh[new_angle] is None:
                        nbr.neigh[new_angle] = hole
               
            self.neigh[i] = hole
            out.append(hole)
            new_i = (i + 3) % 6   
            hole.neigh[new_i] = self
        
        for i in range(len(out)):
            for j in range(len(out)):
                if math.isclose(out[i].distance(out[j]) , 1.0):
                    angle = out[i].angle(out[j])
                    if angle == -1:
                        print("angle error")
                        continue
                    if out[i].neigh[angle] is None:
                        out[i].neigh[angle] = out[j]
                    new_angle = (angle + 3) % 6
                    if out[j].neigh[new_angle] is None:
                        out[j].neigh[new_angle] = out[i]
        
        return out

    def distance(self, hole):
        return math.sqrt((self.x - hole.x)**2 + (self.y - hole.y)**2)


    def angle(self, hole):
        num = hole.y - self.y
        den = hole.x - self.x
        tol = 10e-2

        if math.isclose(num, 0.0, abs_tol=tol):
            if math.isclose(den, 1.0, abs_tol=tol):
                return 0
            elif math.isclose(den, -1.0, abs_tol=tol):
                return 3

        if math.isclose(num, 0.87, abs_tol=tol):
            if math.isclose(den, 0.5, abs_tol=tol):
                return 1
            elif math.isclose(den, -0.5, abs_tol=tol):
                return 2
        
        if math.isclose(num, -0.87, abs_tol=tol):
            if math.isclose(den, 0.5, abs_tol=tol):
                return 5
            elif math.isclose(den, -0.5, abs_tol=tol):
                return 4
        
        return -1

    def num_neighbors(self):
        count = 0
        for nbr in self.neigh:
            if nbr is not None:
               count = count + 1
        return count 

    def __str__(self) -> str:
        return f"({self.radius},{self.x:.2f},{self.y:.2f},{self.filled})"
    
    def __repr__(self):
        return self.__str__()



# Board Class, which hosts all the holes !
class Board:
    def __init__(self, hex_radius, init = "game"):
        self.hex_radius = hex_radius
        self.radius = 0
        self.holes = {}
        self.create_board(hex_radius, init)
    
    def create_board(self, hex_radius, init = "game"):

        # create the first hole
        self.holes[0] = [Hole(x = 0, y = 0, radius = 0)]
        
        # create the inner hex radius holes
        for i in range(1, hex_radius):
            self.radius = i
            self.holes[i] = []
            for hole in self.holes[i-1]:
                created = hole.create_neighbors()
                self.holes[i].extend(created)
        
        # create the outer star holes
        for i in range(hex_radius, (2 * hex_radius) - 1):
            self.radius = i
            self.holes[i] = []
            truncated_holes = []
            
            # edge case for last hole
            if self.radius == (2 * hex_radius) - 2:
                for hole in self.holes[i-1]:
                    created = hole.create_neighbors(filled = False, common_neighbors = self.holes[i-1])
                    self.holes[i].extend(created)
                continue
            
            for hole in self.holes[i-1]:
                if hole.num_neighbors() != 3:
                    truncated_holes.append(hole)
            for hole in truncated_holes:
                created = hole.create_neighbors(filled = False)
                self.holes[i].extend(created)

        # init holes
        if init == "game":
            self.game_initialize()
        elif init == "random":
            self.random_initialize(thresh= 0.9)
        else:
            self.game_initialize()

        # assign index for holes
        all_holes = self.get_holes()
        for i, holes in enumerate(all_holes):
            holes.idx = i


    def game_initialize(self):
        all_holes = self.get_holes()
        for hole in all_holes:
            if hole.radius < self.hex_radius:
                hole.filled = False
            else:
                hole.filled = True

    def random_initialize(self, thresh = 0.5):
        all_holes = self.get_holes()
        for hole in all_holes:
            hole.filled = random.uniform(0, 1) > thresh

    # get holes on the board, upto radius, default - all holes       
    def get_holes(self, radius = -1):
        if radius == -1:
            radius = self.radius
        out = []
        for key, holes in self.holes.items():
            if key <= radius:
                out.extend(holes)
        return out
    
    # check connections on board upto hex_radius 
    def check_connections(self):
        final_layer = self.hex_radius - 1
        check = True
        all_holes = self.get_holes(final_layer)
        for hole in all_holes:
            if hole.radius == final_layer:
                continue
            if hole.num_neighbors() != 6:
                check = False
        return check


if __name__ == "__main__":
    board = Board(5)
    holes = board.holes
    for key, val in holes.items():
        print(f"{key}  {len(val)}")
        pass
    print(board.check_connections())
    holes = board.get_holes()
    print(len(holes))
