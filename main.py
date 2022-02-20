from ast import literal_eval
import pygame, sys, time, random, json, math
from pygame.locals import *

ROWS, COLS = 15, 12
unit_size = 30

score_board_height = 40
spacing_below = 30
box_width, box_height = COLS*unit_size, ROWS*unit_size

pygame.init()
WIDTH, HEIGHT = box_width, box_height+(score_board_height+spacing_below)
surface=pygame.display.set_mode((WIDTH, HEIGHT),0,32)
fps=64
ft=pygame.time.Clock()
pygame.display.set_caption("Tetris")

BLOCKS = []
with open("blocks.json", "r") as fobj:
    Data = json.load(fobj)
    BLOCKS = Data["blocks"][:]

class Block:
    def __init__(self):
        self.data = [[]]
        self.y = -1
        self.x = (COLS//2)-(len(self.data[0])//2)
        self.feed()
    def feed(self):
        random_index = random.randint(0, len(BLOCKS)-1)
        self.data = BLOCKS[random_index][:]
        self.set_initial_position()
    def set_initial_position(self):
        self.y = 0-(len(self.data))
    def move(self, direction):
        self.x += direction
        if self.x<0:
            self.x = 0
        elif self.x>=(COLS-len(self.data[0])):
            self.x = COLS-len(self.data[0])
    def move_down(self):
        self.y += 1
    def rotate(self):
        result = []
        for i in range(len(self.data[0])-1, -1, -1):
            new_row = []
            for j in range(len(self.data)):
                new_row.append(self.data[j][i])
            result.append(new_row[:])
        if 0<=self.x<=(COLS-len(result[0])):
            self.data = result[:]


class App:
    def __init__(self, surface):
        self.surface = surface
        self.play = True
        self.mouse=pygame.mouse.get_pos()
        self.click=pygame.mouse.get_pressed()
        self.color = {
            "background": (77, 50, 39),
            "block": (205, 119, 0),
            "box": (235, 201, 153)
        }
        self.matrix = []
        self.initialize_matrix()
        self.block = Block()
        self.last_moved = time.time()
        self.min_time_gap_between_moving_blocks = 0.4
    def initialize_matrix(self):
        self.matrix = []
        for _ in range(ROWS):
            new_row = [0]*COLS
            self.matrix.append(new_row[:])
        # for i in range(COLS):
        #     self.matrix[7][i] = 1
    def move_blocks(self):
        if (time.time()-self.last_moved)>=self.min_time_gap_between_moving_blocks:
            self.block.move_down()
            self.last_moved = time.time()
    def will_block_touch_other_blocks_by_moving_down(self):
        if self.block.y>=0:
            for i in range(ROWS-1):
                for j in range(COLS):
                    if self.matrix[i+1][j]==1:
                        # check if block covers that point
                        if (self.block.y)<=i<=(self.block.y+(len(self.block.data)-1)):
                            if (self.block.x)<=j<=(self.block.x+(len(self.block.data[0])-1)):
                                x = j-self.block.x
                                y = i-self.block.y
                                if self.block.data[y][x]==1:
                                    return True
        return False
    def will_block_touch_wall(self):
        if (self.block.y+1+(len(self.block.data)-1))>=ROWS:
            return True
        return False
    def draw_block(self):
        for i in range(len(self.block.data)):
            literal_y = self.block.y+i
            if literal_y>=0:
                for j in range(len(self.block.data[i])):
                    y = score_board_height+((literal_y)*unit_size)
                    x = ((self.block.x+j)*unit_size)
                    if self.block.data[i][j]==1:
                        pygame.draw.rect(self.surface, self.color["block"], (x, y, unit_size, unit_size))
    def draw_layout(self):
        pygame.draw.rect(self.surface, self.color["box"], (0, score_board_height, WIDTH, box_height), 1)
        for i in range(COLS):
            for j in range(ROWS):
                x = (i*unit_size)
                y = score_board_height+(j*unit_size)
                if self.matrix[j][i]==1:
                    pygame.draw.rect(self.surface, self.color["block"], (x, y, unit_size, unit_size))
                pygame.draw.rect(self.surface, self.color["box"], (x, y, unit_size, unit_size), 1)
    def render(self):
        self.draw_layout()
        self.draw_block()
    def save_block_on_matrix(self):
        for i in range(len(self.block.data)):
            i_ = self.block.y+i
            for j in range(len(self.block.data[i])):
                    j_ = self.block.x+j
                    if self.block.data[i][j]==1:
                        self.matrix[i_][j_] = 1
    def check_and_Work_on_clearing_lines(self):
        indices_to_be_removed = []
        for index in range(ROWS):
            if 0 not in self.matrix[index]:
                indices_to_be_removed.append(index)
        temp_matrix = self.matrix[::]
        for index in indices_to_be_removed:
            temp_matrix.pop(index)
        for _ in range(len(indices_to_be_removed)):
            new_empty_row = [0]*COLS
            temp_matrix.insert(0, new_empty_row[:])
        self.matrix = temp_matrix[::]
    def action(self, dont_move=False):
        if self.will_block_touch_wall() or self.will_block_touch_other_blocks_by_moving_down():
            self.save_block_on_matrix()
            self.block.feed()
        else:
            if not dont_move:
                self.move_blocks()
        self.check_and_Work_on_clearing_lines()
    def run(self):
        while self.play:
            moved_on_side = False
            self.surface.fill(self.color["background"])
            self.mouse=pygame.mouse.get_pos()
            self.click=pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==KEYDOWN:
                    if event.key==K_TAB:
                        self.play=False
                    elif event.key==K_LEFT:
                        self.block.move(-1)
                        moved_on_side = True
                    elif event.key==K_RIGHT:
                        self.block.move(1)
                        moved_on_side = True
                    elif event.key==K_SPACE:
                        self.block.rotate()
            #--------------------------------------------------------------
            self.action(dont_move=moved_on_side)
            self.render()
            # -------------------------------------------------------------
            pygame.display.update()
            ft.tick(fps)



if  __name__ == "__main__":
    app = App(surface)
    app.run()

