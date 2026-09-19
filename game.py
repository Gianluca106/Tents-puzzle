import g2d
import os
from boardgame import BoardGame
from boardgamegui import gui_play, BoardGameGui

W, H = 40, 40

# ==========================================
# 1. FUNZIONI DI UTILITÀ
# ==========================================
def get_sort_key(filename):
    parts = filename.lower().split('-')
    size = 999
    difficulty = 2 
    for p in parts:
        if 'x' in p:
            nums = p.split('x')
            if nums[0].isdigit():
                size = int(nums[0])
                break
    if 'easy' in filename.lower(): difficulty = 1
    elif 'medium' in filename.lower(): difficulty = 2
    elif 'hard' in filename.lower() or 'special' in filename.lower(): difficulty = 3
    return (size, difficulty, filename)

# ==========================================
# 2. LOGICA GIOCO
# ==========================================
class Tents(BoardGame):
    def __init__(self):
        self._grid = []
        self._col_targets = []
        self._row_targets = []
        self._in_intro = True 
        self._in_outro = False
        self._solution = None 
        self._levels_list = []
        
        # Variabili per l'Hint Lampeggiante
        self._hint_cell = None  # (x, y) della cella suggerita
        self._hint_visible = False # Stato visibilità per lampeggio

        try:
            all_files = [
                f for f in os.listdir('.') 
                if f.endswith('.txt') and 'license' not in f.lower() and 'readme' not in f.lower()
            ]
            if not all_files: 
                print("Attenzione: Nessun file .txt trovato nella cartella.")
            else:
                self._levels_list = sorted(all_files, key=get_sort_key)
        except Exception as e:
            print(f"Errore lettura file: {e}")

        self._current_level_index = 0
        self.load_current_level()

    def cols(self): return self._w + 1
    def rows(self): return self._h + 1
    def size(self): return self._size

    def read(self, x, y):
        # 1. Intestazioni
        if x == 0 and y == 0: return ""
        if y == 0 and x > 0: return str(self._col_targets[x-1])
        if x == 0 and y > 0: return str(self._row_targets[y-1])
        
        # 2. Contenuto Griglia
        gx, gy = x - 1, y - 1
        
        # -- GESTIONE HINT LAMPEGGIANTE --
        # Se questa è la cella dell'hint ed è in fase "visibile"
        if self._hint_cell == (x, y) and self._hint_visible:
            return "*" # Restituisci l'annotazione Gialla (definita nel main)
        
        val = self._grid[gy][gx]
        
        if val == 1: return "🌳"
        if val == 2: return "⛺"
        if val == 3: return "-"
        return ""

    def start_game(self):
        self._in_intro = False
        self._in_outro = False

    def load_current_level(self):
        self._grid = [] 
        self._col_targets = []
        self._row_targets = []
        self._solution = None
        self._w = 5
        self._h = 5
        self._size = 40
        self.stop_hint() # Resetta hint al cambio livello

        if not self._levels_list:
            self._setup_fallback()
        else:
            filename = self._levels_list[self._current_level_index]
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                
                header = lines[0]
                start = header.find('.')
                col_data = header[start+1:] if start != -1 else header
                
                self._col_targets = [int(c, 36) for c in col_data]
                self._w = len(self._col_targets)
                self._h = len(lines) - 1
                
                for line in lines[1:]:
                    self._row_targets.append(int(line[0], 36))
                    row_data = []
                    for char in line[1:]:
                        row_data.append(1 if char == 'T' else 0)
                    self._grid.append(row_data)

                self._compute_solution()
                
            except Exception as e:
                print(f"Errore caricamento {filename}: {e}")
                self._setup_fallback()
        
        # Ridimensiona finestra
        w_pixels = self.cols() * W
        h_pixels = self.rows() * H + H 
        g2d.init_canvas((w_pixels, h_pixels))

    def _setup_fallback(self):
        self._w, self._h, self._size = 5, 5, 40
        self._grid = [[0]*5 for _ in range(5)]
        self._col_targets = [0]*5
        self._row_targets = [0]*5
        self._solution = None

    def next_level(self):
        if self._in_outro:
            self._in_outro = False
            self._in_intro = True
            self._current_level_index = 0
            self.load_current_level()
            return
        if self._current_level_index >= len(self._levels_list) - 1:
            self._in_outro = True
        else:
            self._current_level_index += 1
            self.load_current_level()

    def restart_level(self):
        self.load_current_level()

    # --- METODI PER GESTIRE IL LAMPEGGIO ---
    def trigger_hint(self):
        hint = self.get_hint()
        if hint:
            self._hint_cell = (hint[0], hint[1]) # x, y (1-based per la read)
            self._hint_visible = True
    
    def toggle_hint_blink(self):
        self._hint_visible = not self._hint_visible
        
    def stop_hint(self):
        self._hint_cell = None
        self._hint_visible = False
        
    def is_hint_active(self):
        return self._hint_cell is not None
    # ---------------------------------------

    def play(self, x, y, action=None):
        if action == "next": self.next_level(); return
        if action == "reset": self.restart_level(); return
        if action == "solve_grass": self.solve_grass(); return
        if action == "solve_tents": self.solve_tents(); return
        
        if action == "hint": 
            self.trigger_hint() # Avvia il lampeggio invece dell'alert
            return

        if self._in_intro or self._in_outro: 
            if self._in_intro: self.start_game()
            elif self._in_outro: self.next_level()
            return

        if self._is_level_solved():
            return
        
        # Se clicco mentre c'è un hint attivo, lo fermo
        if self.is_hint_active():
            self.stop_hint()

        if x == 0 or y == 0: return 
        
        gx, gy = x - 1, y - 1
        val = self._grid[gy][gx]
        
        if val == 1: return 
        
        if val == 0:   self._grid[gy][gx] = 3
        elif val == 3: self._grid[gy][gx] = 2
        elif val == 2: self._grid[gy][gx] = 0

    def _compute_solution(self):
        clean_grid = []
        trees = []
        for y in range(self._h):
            row_data = []
            for x in range(self._w):
                val = 1 if self._grid[y][x] == 1 else 0
                row_data.append(val)
                if val == 1: trees.append((x, y))
            clean_grid.append(row_data)
        
        r_counts = [0] * self._h
        c_counts = [0] * self._w
        
        if self._backtrack(clean_grid, trees, 0, r_counts, c_counts):
            self._solution = clean_grid
        else:
            self._solution = None

    def _backtrack(self, grid, trees, idx, r_cnt, c_cnt):
        if idx == len(trees): return True
        tx, ty = trees[idx]
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = tx + dx, ty + dy
            if 0 <= nx < self._w and 0 <= ny < self._h:
                neighbors.append((nx, ny))
        
        for nx, ny in neighbors:
            if grid[ny][nx] != 0: continue 
            if r_cnt[ny] >= self._row_targets[ny]: continue
            if c_cnt[nx] >= self._col_targets[nx]: continue
            
            conflict = False
            for adx in [-1, 0, 1]:
                for ady in [-1, 0, 1]:
                    if adx == 0 and ady == 0: continue
                    ax, ay = nx + adx, ny + ady
                    if 0 <= ax < self._w and 0 <= ay < self._h:
                        if grid[ay][ax] == 2:
                            conflict = True; break
                if conflict: break
            if conflict: continue
            
            grid[ny][nx] = 2
            r_cnt[ny] += 1
            c_cnt[nx] += 1
            
            if self._backtrack(grid, trees, idx + 1, r_cnt, c_cnt): return True
            
            grid[ny][nx] = 0
            r_cnt[ny] -= 1
            c_cnt[nx] -= 1
        return False

    def solve_grass(self):
        if not self._solution: return
        for y in range(self._h):
            for x in range(self._w):
                if self._grid[y][x] == 1: continue 
                if self._solution[y][x] != 2:
                    self._grid[y][x] = 3

    def solve_tents(self):
        if not self._solution: return
        for y in range(self._h):
            for x in range(self._w):
                if self._solution[y][x] == 2:
                    self._grid[y][x] = 2

    def get_hint(self):
        if not self._solution: return None
        for y in range(self._h):
            for x in range(self._w):
                if self._grid[y][x] == 0:
                     if self._solution[y][x] == 2: return (x+1, y+1, 2)
                     else: return (x+1, y+1, 3)
        return None

    def _is_level_solved(self):
        if not self._solution: return False
        for y in range(self._h):
            for x in range(self._w):
                current = self._grid[y][x]
                sol = self._solution[y][x]
                is_tent_sol = (sol == 2)
                is_tent_cur = (current == 2)
                if is_tent_sol != is_tent_cur:
                    return False
        return True

    def finished(self):
        return False

    def _has_touching_tents(self):
        for y in range(self._h):
            for x in range(self._w):
                if self._grid[y][x] == 2:
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0: continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self._w and 0 <= ny < self._h:
                                if self._grid[ny][nx] == 2:
                                    return True
        return False

    def status(self):
        if self._in_intro: return "Tents Puzzle"
        if not self._levels_list: return "Nessun livello"
        
        level_num = self._current_level_index + 1
        
        msg = ""
        if self._has_touching_tents():
            msg = "ERR: Tende vicine!"
        elif self._is_level_solved():
            msg = "RISOLTO!"
        else:
            msg = "Gioca"
            
        cmds = "[N]ext [R]eset"
        return f"Lv {level_num}: {msg} | {cmds}"

# ==========================================
# 3. GUI ESTESA (PER IL BLINKING)
# ==========================================
class BlinkingGui(BoardGameGui):
    def __init__(self, game, actions, annots):
        super().__init__(game, actions, annots)
        self._hint_timer = 0

    def tick(self):
        # 1. Esegue la logica standard (input mouse/tastiera)
        super().tick()
        
        # 2. Gestisce il lampeggio
        if self._game.is_hint_active():
            self._hint_timer += 1
            
            # Lampeggia ogni 10 frame (ca. 0.3 secondi)
            if self._hint_timer % 10 == 0:
                self._game.toggle_hint_blink()
                self.update_buttons() # Ridisegna la griglia
            
            # Ferma il lampeggio dopo 90 frame (3 secondi)
            if self._hint_timer >= 90:
                self._game.stop_hint()
                self.update_buttons()
                self._hint_timer = 0

# Funzione custom per avviare la nostra GUI estesa
def custom_gui_play(game, actions, annots):
    g2d.init_canvas((game.cols() * W, game.rows() * H + H))
    ui = BlinkingGui(game, actions, annots)
    g2d.main_loop(ui.tick)

if __name__ == "__main__":
    game = Tents()
    
    GREEN = (200, 255, 200)
    YELLOW = (255, 255, 0)
    
    # Mappa i suffissi ai colori:
    # "-" -> Verde (Prato)
    # "*" -> Giallo (Hint Lampeggiante)
    annots = {"-": (GREEN, 0), "*": (YELLOW, 0)}
    
    actions = {
        "LeftButton": "",     
        "n": "next",          
        "r": "reset",         
        "g": "solve_grass",   
        "t": "solve_tents",
        "a": "hint"
    }
    
    # Usiamo la nostra funzione custom invece di gui_play standard
    custom_gui_play(game, actions=actions, annots=annots)