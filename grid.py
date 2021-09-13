from typing import List, Tuple, Union
from cell import Cell, WhiteCell, NumberedBlackCell, BlackCell


class Grid:
  """Representa o tabuleiro."""
  def __init__(self, n:int, init_data:List[str]) -> None:
    # normal variables
    self.n = n
    self.model:List[List[Cell]]
    self.numblkcell_list:List[NumberedBlackCell] = []
    self.whitecell_list:List[WhiteCell] = []
    self.parse_strlist(init_data)
    self.add_cell_links()

    self.print_i = 0
    self.print_i_max = 1

    
  def parse_strlist(self, strlist:List[str]):
    # Format check already done in file reading function, strlist suposed
    # valid.
    grid_model:List[List[Cell]] = []

    for i, line in enumerate(strlist):
      line_cell_list = []
      for j, char in enumerate(line):
        cell:Cell
        if char == '.':
          cell = WhiteCell(i,j)
          self.whitecell_list.append(cell)
        elif char == 'x':
          cell = BlackCell(i,j)
        else: # Celula preta numerada
          cell = NumberedBlackCell(i,j,int(char))
          self.numblkcell_list.append(cell)
        line_cell_list.append(cell)
      grid_model.append(line_cell_list)
    
    self.model = grid_model

  def add_cell_links(self):
    for cell in self.numblkcell_list:
      for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
        ni, nj = cell.i+di, cell.j+dj
        if 0 <= ni < self.n and 0 <= nj < self.n and \
        (neig := self.model[ni][nj]).is_white():
          cell.add_adjacent_whitecell(neig)

  def satisfies_all_rules(self) -> bool:
    return self.satisfies_all_whitecells() and self.satisfies_all_tips()

  def satisfies_all_whitecells(self) -> bool:
    return all(cell.is_satisfied() for cell in self.whitecell_list)

  def satisfies_all_tips(self) -> bool:
    return all(cell.is_satisfied() for cell in self.numblkcell_list)

  def break_any_tip(self) -> bool:
    return any(cell.is_broken() for cell in self.numblkcell_list)

  def __str__(self) -> str:
    return '\n'.join(''.join(str(cell) for cell in line)
                     for line in self.model) # pythonic.com.br

  def add_lamp(self, pos:Tuple[int,int]): # se self.model[i][j] não for branco, dá ruim.
    m = self.model
    i, j = pos
    cell:WhiteCell = m[i][j]
    cell.has_lamp = True
    cell.lightup()
    for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
      ni, nj = i+di, j+dj
      while 0 <= ni < self.n and 0 <= nj < self.n and \
            (neig := self.model[ni][nj]).is_white():
        neig.lightup()
        ni, nj = ni+di, nj+dj

  def remove_lamp(self, pos:Tuple[int,int]):
    m = self.model
    i, j = pos
    cell:WhiteCell = m[i][j]
    cell.has_lamp = False
    cell.lightdown()
    for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
      ni, nj = i+di, j+dj
      while 0 <= ni < self.n and 0 <= nj < self.n and \
            (neig := self.model[ni][nj]).is_white():
        neig.lightdown()
        ni, nj = ni+di, nj+dj

  def can_place_lamp(self, pos:Tuple[int,int]) -> bool:
    i, j = pos
    cell = self.model[i][j]
    return cell.is_white() and not cell.is_satisfied()

  def next_valid_position(self, pos:Tuple[int, int]) -> Union[Tuple[int, int], None]:
    i, j = pos
    
    while True:
      j+=1
      if j == self.n:
        i+=1
        j=0

      if not(0 <= i < self.n and 0 <= j < self.n):
        return None
           
      if self.can_place_lamp(newpos := (i, j)):
        return newpos

  def solve(self):
    self._preprocess()
    
    won = False
    
    if not self.satisfies_all_rules():
      pos = (0,-1)
      while (pos := self.next_valid_position(pos)) is not None:
        if self._recsolver(pos):
          won = True
          break
    else:
      won = True
    
    if won:
      print(self)
    else:
      print("impossivel")

  def _preprocess(self):
    is_there_change = True
    while is_there_change:
      is_there_change = False
      for numblkcell in self.numblkcell_list:
        neig_empty = 0
        neig_lamps = 0
        neig_list = numblkcell.adjacent_whitecells
        
        for neig in neig_list:
          if neig.has_lamp:
            neig_lamps += 1
          elif not neig.is_satisfied():
            neig_empty += 1
        
        if neig_empty == numblkcell.tip - neig_lamps:
          for neig in neig_list:
            if not neig.is_satisfied():
              self.add_lamp((neig.i, neig.j))
              is_there_change = True

  def _recsolver(self, pos:Tuple[int, int]) -> bool:
    self.add_lamp(pos)
    tip_ok = not self.break_any_tip()
    if not tip_ok:
      self.remove_lamp(pos)
      return False
    else:
      won = self.satisfies_all_rules()
      if won:
        return True
      else:
        next_pos = pos
        while (next_pos := self.next_valid_position(next_pos)) is not None:
          if self._recsolver(next_pos):
            return True
        self.remove_lamp(pos)
        return False
