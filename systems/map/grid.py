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
        # 1. 배경 초기화
        surface.fill(self.theme.get('bg', (18, 20, 28)))
        
        LINE_COLOR = self.theme.get('neon_line', (33, 33, 255))
        CLOSE_COLOR = self.theme.get('neon_close', (15, 15, 40))
        
        GRID_GUIDE_COLOR = self.theme.get('grid', (30,30,45))


        THICK = 2
        CUT = 6  # 꼭짓점 깎기 크기

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                cell = self.cells[r][c]
                
                # --- [1. 특수 타일 및 장판 처리] ---
                if self.is_thorn(c, r):
                    pygame.draw.rect(surface, (45, 85, 35), rect)
                    continue
                if cell == START: 
                    pygame.draw.rect(surface, (230, 50, 50), rect, width=2, border_radius=4)
                    continue
                elif cell == END: 
                    pygame.draw.rect(surface, (50, 230, 80), rect, width=2, border_radius=4)
                    continue
                elif cell == TOWER:
                    pygame.draw.rect(surface, (70, 75, 90), rect, border_radius=4)
                    continue
                
                # --- [2. 벽 (OBSTACLE) 그리기] ---
                if cell == OBSTACLE:
                    # 벽 안쪽 채우기
                    pygame.draw.rect(surface, CLOSE_COLOR, rect, border_radius=4)
                    
                    # 4방향 이웃 확인
                    up    = (r > 0 and self.cells[r-1][c] == OBSTACLE)
                    down  = (r < GRID_SIZE - 1 and self.cells[r+1][c] == OBSTACLE)
                    left  = (c > 0 and self.cells[r][c-1] == OBSTACLE)
                    right = (c < GRID_SIZE - 1 and self.cells[r][c+1] == OBSTACLE)
                    
                    # 💡 [직선 그리기 개조] 대각선이나 다른 축의 간섭을 완전히 제거
                    # 가로선을 그릴 때는 좌우(left, right)만 보고, 세로선을 그릴 때는 상하(up, down)만 봅니다.
                    
                    # ① 위쪽 가로선
                    if not up:
                        x1 = x + CUT if not left else x
                        x2 = x + CELL_SIZE - CUT if not right else x + CELL_SIZE
                        pygame.draw.line(surface, LINE_COLOR, (x1, y), (x2, y), width=THICK)
                        
                    # ② 아래쪽 가로선
                    if not down:
                        x1 = x + CUT if not left else x
                        x2 = x + CELL_SIZE - CUT if not right else x + CELL_SIZE
                        pygame.draw.line(surface, LINE_COLOR, (x1, y + CELL_SIZE), (x2, y + CELL_SIZE), width=THICK)
                        
                    # ③ 왼쪽 세로선
                    if not left:
                        y1 = y + CUT if not up else y
                        y2 = y + CELL_SIZE - CUT if not down else y + CELL_SIZE
                        pygame.draw.line(surface, LINE_COLOR, (x, y1), (x, y2), width=THICK)
                        
                    # ④ 오른쪽 세로선
                    if not right:
                        y1 = y + CUT if not up else y
                        y2 = y + CELL_SIZE - CUT if not down else y + CELL_SIZE
                        pygame.draw.line(surface, LINE_COLOR, (x + CELL_SIZE, y1), (x + CELL_SIZE, y2), width=THICK)
                    
                    # 💡 [모퉁이 사선 마감] 길과 맞닿은 순수 '외곽 꼭짓점'일 때만 사선을 그립니다.
                    # 좌상단 모퉁이 (위와 왼쪽이 모두 길일 때만 사선 마감)
                    if not up and not left:
                        pygame.draw.line(surface, LINE_COLOR, (x + CUT, y), (x, y + CUT), width=THICK)

                    # 우상단 모퉁이
                    if not up and not right:
                        pygame.draw.line(surface, LINE_COLOR, (x + CELL_SIZE - CUT, y), (x + CELL_SIZE, y + CUT), width=THICK)

                    # 좌하단 모퉁이
                    if not down and not left:
                        pygame.draw.line(surface, LINE_COLOR, (x, y + CELL_SIZE - CUT), (x + CUT, y + CELL_SIZE), width=THICK)

                    # 우하단 모퉁이
                    if not down and not right:
                        pygame.draw.line(surface, LINE_COLOR, (x + CELL_SIZE - CUT, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE - CUT), width=THICK)
                
                elif cell==EMPTY and (c,r) not in self.path:
                    #pygame.draw.rect(surface, GRID_GUIDE_COLOR, rect, width=1)
                    center_x, center_y = x + CELL_SIZE // 2, y + CELL_SIZE // 2
                    pygame.draw.circle(surface, GRID_GUIDE_COLOR, (center_x, center_y), 5)
        
        
        
        
        if hasattr(self, 'path') and len(self.path) > 1:
            path_points = []
            for (c, r) in self.path:
                # 각 이동경로 타일의 정중앙 픽셀 좌표 계산
                center_x = c * CELL_SIZE + CELL_SIZE // 2
                center_y = r * CELL_SIZE + CELL_SIZE // 2
                path_points.append((center_x, center_y))
            
            # 스테이지 테마 색상 연동
            PATH_LINE_COLOR = self.theme.get('path', COLOR_PATH)
            
            # 1) 전체 경로를 관통하는 부드러운 네온 가이드라인 (두께 2)
            pygame.draw.lines(surface, PATH_LINE_COLOR, False, path_points, width=2)
            
            # 2) 가이드라인 위에 일정한 간격으로 박히는 작은 원형 노드(도트)들
            for pt in path_points:
                dot_color = tuple(min(255, v + 40) for v in PATH_LINE_COLOR) # 선보다 살짝 더 밝은 빛 효과
                pygame.draw.circle(surface, dot_color, pt, 2)



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