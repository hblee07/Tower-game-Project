import os, json, pygame, math
from collections import deque
from settings import GRID_SIZE, CELL_SIZE, COLOR_GRID, COLOR_PATH
EMPTY, OBSTACLE, TOWER, START, END = 0, 1, 2, 3, 4

class Grid:
    def __init__(self):
        self.cells = [[EMPTY]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.start=(0,GRID_SIZE//2)
        self.end=(GRID_SIZE-1,GRID_SIZE//2)
        self.path=[]; self.thorn_overlays=[]
        self.effect_manager=None
    
    def is_valid(self,c,r): 
        return 0<=c<GRID_SIZE and 0<=r<GRID_SIZE
    
    def load_layout(self, layout, start, end):
        self.cells = [row[:] for row in layout]
        self.start=tuple(start); self.end=tuple(end)
        self.cells[self.start[1]][self.start[0]]=START
        self.cells[self.end[1]][self.end[0]]=END
    
    def pixel_to_grid(self,x,y): 
        return int(x//CELL_SIZE), int(y//CELL_SIZE)
    
    def grid_to_pixel_center(self,c,r): 
        return c*CELL_SIZE+CELL_SIZE//2, r*CELL_SIZE+CELL_SIZE//2
    
    def is_walkable(self,c,r): 
        return self.is_valid(c,r) and self.cells[r][c] not in (OBSTACLE,TOWER)
    
    def is_placeable(self,c,r): 
        return self.is_valid(c,r) and self.cells[r][c]==EMPTY
    
    def place_tower(self,c,r): 
        self.cells[r][c] = TOWER
    
    def remove_tower(self,c,r):
        if self.is_valid(c,r) and self.cells[r][c]==TOWER: self.cells[r][c] = EMPTY
    
    def activate_thorn_overlay(self, center, radius_cells, duration=5.0): 
        self.thorn_overlays.append({'center':center,'radius':radius_cells,'timer':duration})
    
    def update_thorn_overlays(self, dt):
        for o in self.thorn_overlays: o['timer'] -= dt
        self.thorn_overlays = [o for o in self.thorn_overlays if o['timer'] > 0]
    
    def is_thorn(self,c,r):
        return any(math.hypot(c-o['center'][0], r-o['center'][1]) <= o['radius'] for o in self.thorn_overlays)
    
    def draw(self, surface):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect=pygame.Rect(c*CELL_SIZE,r*CELL_SIZE,CELL_SIZE,CELL_SIZE)
                color=COLOR_GRID
                if (c,r) in self.path: 
                    color=COLOR_PATH
                if self.is_thorn(c,r): 
                    color=(65,95,45)
                cell=self.cells[r][c]
                if cell==OBSTACLE: 
                    color=(85,88,95)
                elif cell==TOWER: 
                    color=(45,45,55)
                elif cell==START: 
                    color=(210,70,70)
                elif cell==END: 
                    color=(70,190,80)
                pygame.draw.rect(surface,color,rect)
                pygame.draw.rect(surface,(55,58,64),rect,1)

class Pathfinder:
    def find_path(self, grid):
        q=deque([grid.start])
        parent={grid.start:None}
        while q:
            c,r=q.popleft()
            if (c,r)==grid.end: 
                return self.reconstruct(parent, grid.end)
            for dc,dr in [(1,0),(-1,0),(0,1),(0,-1)]:
                nc,nr=c+dc,r+dr
                if not grid.is_walkable(nc,nr) and (nc,nr) != grid.end: 
                    continue
                if (nc,nr) not in parent:
                    parent[(nc,nr)]=(c,r); q.append((nc,nr))
        return []
    def reconstruct(self,parent,end):
        path=[]
        node=end
        while node is not None: 
            path.append(node); node=parent[node]
        return list(reversed(path))
    def is_fully_blocked(self, grid): 
        return len(self.find_path(grid))==0

class StageLoader:
    def load(self, stage_id):
        path=os.path.join(os.path.dirname(__file__),'stages',f'stage{stage_id}.json')
        with open(path,'r',encoding='utf-8') as f: data=json.load(f)
        data['start']=tuple(data['start'])
        data['end']=tuple(data['end'])
        return data
