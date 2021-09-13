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
        (neig := self.model[ni][nj]).iswhite():
          cell.add_whitenei(neig)

  def satisfaz_tudo(self) -> bool:
    return self.satisfaz_todas_luz() and self.satisfaz_todas_dicas()

  def satisfaz_todas_luz(self) -> bool:
    return all(cell.issatisfied() for cell in self.whitecell_list)

  def satisfaz_todas_dicas(self) -> bool:
    return all(cell.issatisfied() for cell in self.numblkcell_list)

  def quebra_alguma_dica(self) -> bool:
    return any(cell.isbroken() for cell in self.numblkcell_list)

  def __str__(self) -> str:
    return '\n'.join(''.join(str(cell) for cell in line)
                     for line in self.model) # pythonic.com.br

  def add_lamp(self, pos:Tuple[int,int]): # se self.model[i][j] não for branco, dá ruim.
    m = self.model
    i, j = pos
    cell:WhiteCell = m[i][j]
    cell.haslamp = True
    cell.lightup()
    for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
      ni, nj = i+di, j+dj
      while 0 <= ni < self.n and 0 <= nj < self.n and \
            (neig := self.model[ni][nj]).iswhite():
        neig.lightup()
        ni, nj = ni+di, nj+dj

  def remove_lamp(self, pos:Tuple[int,int]):
    m = self.model
    i, j = pos
    cell:WhiteCell = m[i][j]
    cell.haslamp = False
    cell.lightdown()
    for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
      ni, nj = i+di, j+dj
      while 0 <= ni < self.n and 0 <= nj < self.n and \
            (neig := self.model[ni][nj]).iswhite():
        neig.lightdown()
        ni, nj = ni+di, nj+dj

  def canplacelamp(self, pos:Tuple[int,int]) -> bool:
    i, j = pos
    cell = self.model[i][j]
    return cell.iswhite() and not cell.issatisfied()

  def prox_pos_valida(self, pos:Tuple[int, int]) -> Union[Tuple[int, int], None]:
    i, j = pos
    
    while True:
      j+=1
      if j == self.n:
        i+=1
        j=0

      if not(0 <= i < self.n and 0 <= j < self.n):
        return None
           
      if self.canplacelamp(newpos := (i, j)):
        return newpos

  def solve(self):
    self._preprocess()
    
    won = False
    
    if not self.satisfaz_tudo():
      pos = (0,-1)
      while (pos := self.prox_pos_valida(pos)) is not None:
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
    istherechange = True
    while istherechange:
      istherechange = False
      for numblkcell in self.numblkcell_list:
        neig_livres = 0
        neig_lamps = 0
        neig_list = numblkcell.whitenei_list
        
        for neig in neig_list:
          if neig.haslamp:
            neig_lamps += 1
          elif not neig.issatisfied():
            neig_livres += 1
        
        if neig_livres == numblkcell.tip - neig_lamps:
          for neig in neig_list:
            if not neig.issatisfied():
              self.add_lamp((neig.i, neig.j))
              istherechange = True

  def _recsolver(self, pos:Tuple[int, int]) -> bool:
    self.add_lamp(pos)
    hintOK = not self.quebra_alguma_dica()
    if not hintOK:
      self.remove_lamp(pos)
      return False
    else:
      won = self.satisfaz_tudo()
      if won:
        return True
      else:
        next_pos = pos
        while (next_pos := self.prox_pos_valida(next_pos)) is not None:
          if self._recsolver(next_pos):
            return True
        self.remove_lamp(pos)
        return False
