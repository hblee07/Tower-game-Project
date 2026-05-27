import os, json, pygame, math
from collections import deque
from settings import GRID_SIZE, CELL_SIZE, COLOR_GRID, COLOR_PATH, STAGE_THEMES
EMPTY, OBSTACLE, TOWER, START, END = 0, 1, 2, 3, 4

class Grid:
    def __init__(self):
        self.cells = [[EMPTY]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.start=(0,GRID_SIZE//2)
        self.end=(GRID_SIZE-1,GRID_SIZE//2)
        self.path=[]; self.thorn_overlays=[]
        self.effect_manager=None
        
        # 🎨 [기본 테마 초기화] settings.py에서 선언한 STAGE_THEMES 데이터를 가져와 연동합니다.
        self.theme = STAGE_THEMES[1] 
    
    def set_theme(self, stage_id):
        # 💡 GameScene이 생성될 때 stage_id를 받아 타일 테마를 완전히 스위칭합니다.
        if stage_id in STAGE_THEMES:
            self.theme = STAGE_THEMES[stage_id]
    
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
                
                # 🎨 [테마 컬러 분기] 
                # 기본 바탕 색상은 이제 스테이지별 빈 땅('grid') 색상을 따릅니다.
                color = self.theme['grid']
                
                if (c,r) in self.path: 
                    # 몬스터 길은 스테이지별 길('path') 색상을 따릅니다.
                    color = self.theme['path']
                    
                if self.is_thorn(c,r): 
                    # 가시 장판은 기본 가시 이펙트 색상과 조화가 어우러지도록 테마 믹스 처리
                    color=(65,95,45)
                    
                cell=self.cells[r][c]
                if cell==OBSTACLE: 
                    # 💡 벽(장애물)도 숲/사막/얼음에 맞춰 다르게 보일 수 있도록 믹스업
                    # 만약 STAGE_THEMES에 'wall'을 추가 정의하지 않은 경우 가독성 조정을 거친 톤 다운 색상을 씁니다.
                    if 'wall' in self.theme:
                        color = self.theme['wall']
                    else:
                        color = tuple(max(0, val - 20) for val in self.theme['grid']) # 빈땅보다 살짝 어둡게 자동 연산
                elif cell==TOWER: 
                    color=(45,45,55)
                elif cell==START: 
                    color=(210,70,70)
                elif cell==END: 
                    color=(70,190,80)
                    
                pygame.draw.rect(surface,color,rect)
                
                # 격자 테두리선은 바깥 배경색과 매칭되도록 연출합니다.
                pygame.draw.rect(surface, self.theme['bg'], rect, 1)

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