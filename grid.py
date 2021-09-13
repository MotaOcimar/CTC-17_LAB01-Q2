from typing import List, Tuple, Union
from cell import Cell, WhiteCell, NumberedBlackCell, BlackCell


class Grid:
  """Representa o tabuleiro."""
  def __init__(self, n:int, init_data:List[str]):
    self.n = n # Tamanho do lado do tabuleiro, suposto quadrado.
    self.model:List[List[Cell]] = None # Matriz que armazena as células
    self.nmblkcell_list:List[NumberedBlackCell] = [] # Uma vista que contem
    # as células pretas numeradas
    self.whitecell_list:List[WhiteCell] = [] # || as células brancas
    
    self.parse_strlist(init_data)
    self.add_cell_links()
    self.order_nmblkcell_list()
    self.order_whitecell_list()

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
          self.whitecell_list.append(cell) # adicionando à lista da view
        elif char == 'x':
          cell = BlackCell(i,j)
        else: # Celula preta numerada
          cell = NumberedBlackCell(i,j,int(char))
          self.nmblkcell_list.append(cell) # adicionando à lista da view
        line_cell_list.append(cell)
      grid_model.append(line_cell_list)
    
    self.model = grid_model

  def add_cell_links(self):
    # método para armazenar para cada par (célula preta numerada, celula
    # branca adjacente) as referencias de uma célula na outra
    for nmblk in self.nmblkcell_list:
      for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
        ni, nj = nmblk.i+di, nmblk.j+dj
        if 0 <= ni < self.n and 0 <= nj < self.n \
        and (whitenei := self.model[ni][nj]).iswhite():
          prevnmblk = whitenei.nmblknei_highest
          
          if prevnmblk is None \
          or nmblk.num > prevnmblk.num \
          or (nmblk.num == prevnmblk.num 
          and nmblk.i*self.n + nmblk.j < prevnmblk.i*self.n + prevnmblk.j):
            whitenei.nmblknei_highest = nmblk
          
          nmblk.add_whitenei(whitenei)

  def order_nmblkcell_list(self):
    self.nmblkcell_list.sort(key=lambda c: c.num, reverse=True)

  def order_whitecell_list(self):
    has_nmblknei_list = []
    not_nmblknei_list = []
    for c in self.whitecell_list:
      if c.nmblknei_highest is not None:
        has_nmblknei_list.append(c)
      else:
        not_nmblknei_list.append(c)

    has_nmblknei_list.sort(key=lambda c: c.nmblknei_highest.num, reverse=True)

    self.whitecell_list = has_nmblknei_list + not_nmblknei_list   

  def satisfaz_tudo(self) -> bool:
    return self.satisfaz_todas_luzes() and self.satisfaz_todas_dicas()

  def satisfaz_todas_luzes(self) -> bool:
    return all(cell.issatisfied() for cell in self.whitecell_list)

  def satisfaz_todas_dicas(self) -> bool:
    return all(cell.issatisfied() for cell in self.nmblkcell_list)

  def quebra_alguma_dica(self) -> bool:
    return any(cell.isbroken() for cell in self.nmblkcell_list)

  def __str__(self) -> str:
    return '\n'.join(''.join(str(cell) for cell in line)
                     for line in self.model)

  def add_lamp(self, cell:WhiteCell):
    cell.haslamp = True
    cell.lightup()
    i, j = cell.i, cell.j
    for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
      ni, nj = i+di, j+dj
      while 0 <= ni < self.n and 0 <= nj < self.n and \
            (neig := self.model[ni][nj]).iswhite():
        neig.lightup()
        ni, nj = ni+di, nj+dj

  def remove_lamp(self, cell:WhiteCell):
    cell.haslamp = False
    cell.lightdown()
    i, j = cell.i, cell.j
    for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
      ni, nj = i+di, j+dj
      while 0 <= ni < self.n and 0 <= nj < self.n and \
            (neig := self.model[ni][nj]).iswhite():
        neig.lightdown()
        ni, nj = ni+di, nj+dj

  def can_place_lamp(self, cell:WhiteCell) -> bool:
    return not cell.issatisfied()

  def prox_i(self, i:int) -> int:
    i += 1
    while i < len(self.whitecell_list):
      cell = self.whitecell_list[i]
      if self.can_place_lamp(cell):
        return i
      i += 1
    return len(self.whitecell_list)

  def solve(self):
    self._preprocess()
    
    won = False
    
    if not self.satisfaz_tudo():
      i = 0
      while i < len(self.whitecell_list):
        if self._recsolver(i):
          won = True
          break
        i = self.prox_i(i)
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
      for nmblkcell in self.nmblkcell_list:
        neig_livres = 0
        neig_lamps = 0
        neig_list = nmblkcell.whitenei_list
        
        for neig in neig_list:
          if neig.haslamp:
            neig_lamps += 1
          elif not neig.issatisfied():
            neig_livres += 1
        
        if neig_livres == nmblkcell.num - neig_lamps:
          for neig in neig_list:
            if not neig.issatisfied():
              self.add_lamp(neig)
              istherechange = True

  def _recsolver(self, i:int) -> bool:
    cell = self.whitecell_list[i]
    self.add_lamp(cell)
    hintOK = not self.quebra_alguma_dica()
    if not hintOK:
      self.remove_lamp(cell)
      return False
    else:
      won = self.satisfaz_tudo()
      if won:
        return True
      else:
        next_i = self.prox_i(i)
        while next_i < len(self.whitecell_list):
          if self._recsolver(next_i):
            return True
          next_i = self.prox_i(next_i)
        self.remove_lamp(cell)
        return False
