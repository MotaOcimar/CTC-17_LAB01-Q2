import itertools as itt
from typing import List, Tuple, Union
from abc import ABCMeta, abstractmethod


class Cell(metaclass=ABCMeta):
  """Representa uma célula do tabuleiro."""
  @abstractmethod
  def __init__(self, i:int, j:int):
    self.i, self.j = i, j
    
  @abstractmethod
  def __str__(self) -> str:
    pass

  @abstractmethod
  def issatisfied(self) -> bool:
    pass
  
  def hastip(self) -> bool:
    return isinstance(self, NumberedBlackCell)

  def iswhite(self) -> bool:
    return isinstance(self, WhiteCell)


class WhiteCell(Cell):
  """Representa célula branca."""
  def __init__(self, i:int, j:int):
    super().__init__(i, j)
    
    self.light_level = 0 # quantas lampadas iluminam essa casa
    #self.constraint_level = 0# se for maior que 0 não pode pôr lampada aqui
    self.haslamp = False # se tem uma lampada aqui
    #self.hastipnei = False # se está ao lado de uma célula preta numerada
    #self.tipnei_list:List[NumberedBlackCell] = [] # lista de células pretas
    #   numeradas adjacentes
    
    # self.affwhite_list:List[WhiteCell] = [] # Não guardei a lista de
    #   células brancas que tem constraint com esta por causa da
    #   complexidade em memória.
  
  def issatisfied(self) -> bool:
    return self.light_level > 0

  # def canplacelamp(self) -> bool:
  #   return self.constraint_level == 0

  def lightup(self):
    self.light_level += 1
    #self.constraint_level += 1
  
  def lightdown(self):
    self.light_level -= 1
    #self.constraint_level -= 1

  # def addlamp(self): # Exige processamento externo pois modifica outras
  #   células, então implementarei como função externa.
  
  # def remlamp(self): # Idem ao caso anterior.
  
  # def add_tipnei(self, tipnei):
  #   self.hastipnei = True
  #   self.tipnei_list.append(tipnei)

  def __str__(self) -> str:
    if self.haslamp:
      return '*'
    # elif self.light_level > 0:
    #   return '+'
    else:
      return '.'

class BlackCell(Cell):
  """Representa célula preta"""
  def __init__(self, i:int, j:int):
    super().__init__(i, j)

  def __str__(self) -> str:
    return 'x'

  def issatisfied(self) -> bool:
      return True


class NumberedBlackCell(BlackCell):
  """Representa célula preta com dica"""
  def __init__(self, i:int, j:int, tip:int):
    super().__init__(i, j)
    
    self.tip = tip # o número da dica.
    self.whitenei_list:List[WhiteCell] = [] # contém a lista das células
    #   brancas adjacentes. Como o tamanho é no máximo quatro, eu botei a
    #   lista dentro da célula.
    #self.lampnei_num:int = 0 # contém quantas casas brancas adjacentes
    #   possuem lampada.

  def add_whitenei(self, cell:WhiteCell):
    self.whitenei_list.append(cell)

  # def add_whitenei_list(self, whitenei_list:List[WhiteCell]):
  #   self.whitenei_list = whitenei_list

  #   if self.tip == 0:
  #     for cell in self.whitenei_list:
  #       cell.constraint_level += 1

  def issatisfied(self) -> bool:
    return sum(1 for lamp in self.whitenei_list if lamp.haslamp) == \
      self.tip

  def isbroken(self) -> bool:
    return sum(1 for lamp in self.whitenei_list if lamp.haslamp) > \
      self.tip
  # def get_whitenei_not_constrained(self):
  #   return [nei for nei in self.whitenei_list if nei.canplacelamp()]

  # def neighbor_lamp_added(self): # método para notificar esta célula que
  #   #   uma lâmpada foi posta ao lado.
  #   self.lampnei_num += 1
  #   if self.lampnei_num == self.tip: # o constraint começa a valer quando
  #     #   encheu as vagas.
  #     for cell in self.whitenei_list:
  #       cell.constraint_level += 1
  
  # def neighbor_lamp_removed(self):
  #   self.lampnei_num -= 1
  #   if self.lampnei_num == self.tip - 1:
  #     for cell in self.whitenei_list:
  #       cell.constraint_level -= 1

  def __str__(self) -> str:
    return str(self.tip)


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
    
    # helper variables to lessen the solving process complexity
    # self.num_lits = 0
    # self.target_num_lits = sum(1 for cell in itt.chain(*self.model) if
    #   cell.iswhite()) # O único propósito de todos os chain
      # desse programa é substituir for aninhado.

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

    # for i, j in itt.product(range(self.n), range(self.n)):
    #   cell = self.model[i][j]
    #   if cell.hastip():
    #     whitenei_list = []
    #     for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
    #       ni, nj = i + di, j + dj
    #       if 0 <= ni < self.n and 0 <= nj < self.n:
    #         neicell = self.model[ni][nj]
    #         if neicell.iswhite():
    #           whitenei_list.append(neicell)
    #           neicell.add_tipnei(cell)
    #     cell.add_whitenei_list(whitenei_list)

  # def issolved(self) -> bool:
  #   return self.num_lits == self.target_num_lits
  #   # return not any(cell.iswhite() and not cell.islit()
  #   #                for cell in itt.chain(*self.model))

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

  # def lightupcell(self, cell:Cell):
  #   cell.lightup()
  #   self.num_lits+=1
  
  # def lightdowncell(self, cell:Cell):
  #   cell.lightdown()
  #   self.num_lits-=1
 
  # def addlamp(self, i, j): # se self.model[i][j] não for branco, dá ruim.
  #   m = self.model
  #   cell:WhiteCell = m[i][j]
  #   cell.haslamp = True
  #   # if cell.hastipnei:
  #   #   for tipnei in cell.tipnei_list:
  #   #     tipnei.neighbor_lamp_added()
  #   self.lightupcell(cell)
  #   for di, dj in ((1,0), (0,1), (-1,0), (0,-1)):
  #     ni, nj = i+di, j+dj
  #     while 0 <= ni < self.n and 0 <= nj < self.n and \
  #           (neig := self.model[ni][nj]).iswhite():
  #       self.lightupcell(neig)

  def add_lamp(self, pos:Tuple[int,int]): # se self.model[i][j] não for branco, dá ruim.
    m = self.model
    i, j = pos
    cell:WhiteCell = m[i][j]
    cell.haslamp = True
    # if cell.hastipnei:
    #   for tipnei in cell.tipnei_list:
    #     tipnei.neighbor_lamp_added()
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
    # if cell.hastipnei:
    #   for tipnei in cell.tipnei_list:
    #     tipnei.neighbor_lamp_removed()
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

  # def get_next_unconstrained_white_cell(self, start_i:int, start_j:int):
  #   pass

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
        # print(''.join(str(cell) for cell in neig_list))
        
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
      # print()

  def _recsolver(self, pos:Tuple[int, int]) -> bool:
    self.add_lamp(pos)
    # print(self)
    # print()
    # self.print_i += 1
    # if self.print_i >= self.print_i_max:
    #   self.print_i = 0
    #   print(self)
    #   print()
    hintOK = not self.quebra_alguma_dica()
    if not hintOK:
      self.remove_lamp(pos)
      # print('rem')
      # print(self)
      # print()
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


def read_tabs_file(filename:str) -> List[Grid]:
  grid_list: List[Grid] = []  # return variable
  
  with open(filename) as file:
    # reading and formatting contents of filename
    text = file.readlines()
    # for line in text:
    #     line = line.strip()
    # text = [line for line in text if len(line) > 0]

    # parsing for state variables
    is_parsing_grid = False
    cur_grid_size = 0
    cur_grid_strlist:List[str] = []

    # line parsing for
    for line_i, line in enumerate(text):
      if (len(line) > 0 and not line.isspace()): # ignore empty lines or
        # with whitespace only.

        # character whitespace filter and mistake checking
        charlist = []
        for c_i, c in enumerate(line):
          if not c.isspace(): # ignore leading, end or inmiddle whitespace
            if c not in '.x01234':
              print(f"arquivo {filename}: caractere '{c}' não \
                    reconhecido.linha={line_i} coluna={c_i}.")
              raise RuntimeError
            charlist.append(c)
        clean_line = ''.join(charlist)
        
        # change line parsing for state
        if not is_parsing_grid:  # starts creating a new grid
          is_parsing_grid = True
          cur_grid_size = len(clean_line)
          cur_grid_strlist = []
          cur_grid_strlist.append(clean_line)
        else:  # continue reading a already started grid
          if bad_size := len(clean_line) != cur_grid_size:  # Por algum
            # motivo chegou uma linha de tamanho diferente do esperado
            print(f'''arquivo {filename}: linha "{line}" de tamanho \
                  {bad_size} diferente das anteriores, de tamanho \
                  {cur_grid_size}. linha={line_i}.''')
            raise RuntimeError
          cur_grid_strlist.append(clean_line)

        if len(cur_grid_strlist) == cur_grid_size: # full grid read
          grid_list.append(Grid(cur_grid_size, cur_grid_strlist))
          is_parsing_grid = False
    # line parsing for end

    if is_parsing_grid: # file ended during a grid read.
      print(f'arquivo {filename}: file ended with incomplete grid.')
      raise RuntimeError
  
  return grid_list


if __name__=='__main__':
  init_tabs_fname = 'init_tabs.txt'
  grid_list = read_tabs_file(init_tabs_fname)

  # grid_list[4].solve()
  for i, grid in enumerate(grid_list):
    print(i)
    grid.solve()
    print()
