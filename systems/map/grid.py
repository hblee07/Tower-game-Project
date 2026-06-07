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
        self.theme = STAGE_THEMES[1] 
    
    def set_theme(self, stage_id):
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
        surface.fill(self.theme.get('bg', (18, 20, 28)))
        
        LINE_COLOR = self.theme.get('neon_line', (33, 33, 255))
        CLOSE_COLOR = self.theme.get('neon_close', (15, 15, 40))
        
        GRID_GUIDE_COLOR = self.theme.get('grid', (30,30,45))


        THICK = 2
        CUT = 6 

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                cell = self.cells[r][c]
                if cell == START: 
                    pygame.draw.rect(surface, (230, 50, 50), rect, width=2, border_radius=4)
                    continue
                elif cell == END: 
                    pygame.draw.rect(surface, (50, 230, 80), rect, width=2, border_radius=4)
                    continue
                elif cell == TOWER:
                    pygame.draw.rect(surface, (70, 75, 90), rect, border_radius=4)
                    continue
                
                if cell == OBSTACLE:
                    pygame.draw.rect(surface, CLOSE_COLOR, rect, border_radius=4)
                    up    = (r > 0 and self.cells[r-1][c] == OBSTACLE)
                    down  = (r < GRID_SIZE - 1 and self.cells[r+1][c] == OBSTACLE)
                    left  = (c > 0 and self.cells[r][c-1] == OBSTACLE)
                    right = (c < GRID_SIZE - 1 and self.cells[r][c+1] == OBSTACLE)
                    if not up:
                        x1 = x + CUT if not left else x
                        x2 = x + CELL_SIZE - CUT if not right else x + CELL_SIZE
                        pygame.draw.line(surface, LINE_COLOR, (x1, y), (x2, y), width=THICK)
                        
                    if not down:
                        x1 = x + CUT if not left else x
                        x2 = x + CELL_SIZE - CUT if not right else x + CELL_SIZE
                        pygame.draw.line(surface, LINE_COLOR, (x1, y + CELL_SIZE), (x2, y + CELL_SIZE), width=THICK)
                        
                    if not left:
                        y1 = y + CUT if not up else y
                        y2 = y + CELL_SIZE - CUT if not down else y + CELL_SIZE
                        pygame.draw.line(surface, LINE_COLOR, (x, y1), (x, y2), width=THICK)
                        
                    if not right:
                        y1 = y + CUT if not up else y
                        y2 = y + CELL_SIZE - CUT if not down else y + CELL_SIZE
                        pygame.draw.line(surface, LINE_COLOR, (x + CELL_SIZE, y1), (x + CELL_SIZE, y2), width=THICK)
                    if not up and not left:
                        pygame.draw.line(surface, LINE_COLOR, (x + CUT, y), (x, y + CUT), width=THICK)

                    if not up and not right:
                        pygame.draw.line(surface, LINE_COLOR, (x + CELL_SIZE - CUT, y), (x + CELL_SIZE, y + CUT), width=THICK)

                    if not down and not left:
                        pygame.draw.line(surface, LINE_COLOR, (x, y + CELL_SIZE - CUT), (x + CUT, y + CELL_SIZE), width=THICK)

                    if not down and not right:
                        pygame.draw.line(surface, LINE_COLOR, (x + CELL_SIZE - CUT, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE - CUT), width=THICK)
                
                elif cell==EMPTY and (c,r) not in self.path:
                    center_x, center_y = x + CELL_SIZE // 2, y + CELL_SIZE // 2
                    pygame.draw.circle(surface, GRID_GUIDE_COLOR, (center_x, center_y), 5)
                    
                    
        
        
        if hasattr(self, 'path') and len(self.path) > 1:
            path_points = []
            for (c, r) in self.path:
                center_x = c * CELL_SIZE + CELL_SIZE // 2
                center_y = r * CELL_SIZE + CELL_SIZE // 2
                path_points.append((center_x, center_y))
            
            PATH_LINE_COLOR = self.theme.get('path', COLOR_PATH)

            pygame.draw.lines(surface, PATH_LINE_COLOR, False, path_points, width=2)

            for pt in path_points:
                dot_color = tuple(min(255, v + 40) for v in PATH_LINE_COLOR)
                pygame.draw.circle(surface, dot_color, pt, 2)

        if hasattr(self, 'thorn_overlays'):
            for overlay in self.thorn_overlays:
                tc, tr = overlay['center']

                cx = tc * CELL_SIZE + CELL_SIZE // 2
                cy = tr * CELL_SIZE + CELL_SIZE // 2
                pixel_radius = int(overlay['radius'] * CELL_SIZE)

                surf_size = pixel_radius * 2

                overlay_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                pygame.draw.circle(overlay_surf, (50, 200, 80, 60), (pixel_radius, pixel_radius), pixel_radius)

                pygame.draw.circle(overlay_surf, (120, 255, 150, 180), (pixel_radius, pixel_radius), pixel_radius, width=1)

                surface.blit(overlay_surf, (cx - pixel_radius, cy - pixel_radius))



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