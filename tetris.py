from settings import*
import math
from tetromino import Tetromino
import pygame.freetype as ft

class Text:
    def __init__(self, app):
        self.app = app
        self.font = ft.Font(FONT_PATH)
        
    def draw(self):
        self.font.render_to(self.app.screen, (WIN_W * 0.595, WIN_H * 0.02), 
                            text='N_Factorial"s Tetris', 
                            fgcolor='white',
                            size=TILE_SIZE * 0.6,
                            bgcolor='red')
        
        self.font.render_to(self.app.screen, (WIN_W * 0.67, WIN_H * 0.22),
                            text='next', 
                            fgcolor='white',
                            size=TILE_SIZE * 1.4, 
                            bgcolor='red')
        
        self.font.render_to(self.app.screen, (WIN_W * 0.67, WIN_H * 0.67),
                            text='score', 
                            fgcolor='white',
                            size=TILE_SIZE * 1.4, 
                            bgcolor='red')
        
        self.font.render_to(self.app.screen, (WIN_W * 0.70, WIN_H * 0.8),
                            text=f'{self.app.tetris.score}', 
                            fgcolor='white',
                            size=TILE_SIZE * 1.8)

class Tetris:
    def __init__ (self,app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.speed_up = False
        self.check_game_over = False
        
        self.score = 0
        self.full_lines = 0
        self.points_per_lines = {0:0, 1:150, 2:300, 3:600, 4:1200, 5:1500, 6:1800, 7:2100, 8:2500, 9:3000}
    
    def get_score(self):
        self.score += self.points_per_lines[self.full_lines]
        self.full_lines = 0
        
    def check_full_lines(self):
        row = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1):
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x]
                
                if self.field_array[y][x]:
                    self.field_array[row][x].pos = vec(x, y)

            if sum(map(bool, self.field_array[y])) < FIELD_W:
                row -= 1
            else:
                for x in range(FIELD_W):
                    self.field_array[row][x].alive = False
                    self.field_array[row][x] = 0
                
                pg.mixer.init()                        # here is i am removing the line if this line fulled
                pg.mixer.music.load(SOUNDS_LINECLEAR_PATH)
                pg.mixer.music.play(loops=0)    
                                 
                self.full_lines += 1
                
    def put_tetromino_blocks_in_array(self):
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            self.field_array[y][x] = block
    
    def get_field_array(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def is_game_over(self):
        if self.tetromino.blocks[0].pos.y == INIT_POS_OFFSET[1]:
            pg.mixer.init()
            pg.mixer.music.load(SOUNDS_END_PATH)        #here is I am adding a music file for giving a signal that gave over
            pg.mixer.music.play(loops=0)
            pg.time.wait(1000)
            #--------------------- I am going to store date to the txt file
            file_path = MAXIMUM_SCORE_PATH
            my_score = self.score 
            with open(file_path, "r") as file:
                stored_number = int(file.readline().strip())
            if my_score > stored_number: 
                with open(file_path, "w") as file:
                    file.write(str(my_score))                   
            #---------------------------   
            return True
    
    def check_tetromino_landing(self):
        if self.tetromino.landing:
            if self.is_game_over():
                self.check_game_over = True             #here is I am giving a true to boolean to finishing the game
                # self.__init__(self.app)               #now I do not need to restart I just to create menu panel
            else:
                self.speed_up = False
                self.put_tetromino_blocks_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)  # here I am creating a new shape
                pg.mixer.init()
                pg.mixer.music.load(SOUNDS_DROP_PATH)
                pg.mixer.music.play(loops=0)

        
    def control(self, pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction='right')
        elif pressed_key == pg.K_UP:
            self.tetromino.rotate()
        elif pressed_key == pg.K_DOWN:
            self.speed_up = True
        
    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black', (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        
    def update(self):
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]
        if trigger:
            self.check_full_lines()
            self.tetromino.update()
            self.check_tetromino_landing()
            self.get_score()
        self.sprite_group.update()
    
    def draw(self):
        self.draw_grid()
        self.sprite_group.draw(self.app.screen)