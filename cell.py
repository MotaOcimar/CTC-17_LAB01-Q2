from typing import List
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
  def is_satisfied(self) -> bool:
    pass
  
  def has_tip(self) -> bool:
    return isinstance(self, NumberedBlackCell)

  def is_white(self) -> bool:
    return isinstance(self, WhiteCell)


class WhiteCell(Cell):
  """Representa célula branca."""
  def __init__(self, i:int, j:int):
    super().__init__(i, j)
    
    self.light_level = 0 # quantas lampadas iluminam essa casa
    self.has_lamp = False # se tem uma lampada aqui
  
  def is_satisfied(self) -> bool:
    return self.light_level > 0

  def lightup(self):
    self.light_level += 1
  
  def lightdown(self):
    self.light_level -= 1

  def __str__(self) -> str:
    if self.has_lamp:
      return '*'
    elif self.light_level > 0:
      return '+'
    else:
      return '.'

class BlackCell(Cell):
  """Representa célula preta"""
  def __init__(self, i:int, j:int):
    super().__init__(i, j)

  def __str__(self) -> str:
    return 'x'

  def is_satisfied(self) -> bool:
      return True


class NumberedBlackCell(BlackCell):
  """Representa célula preta com dica"""
  def __init__(self, i:int, j:int, tip:int):
    super().__init__(i, j)
    
    self.tip = tip # o número da dica.
    self.adjacent_whitecells:List[WhiteCell] = [] # contém a lista das células
    #   brancas adjacentes. Como o tamanho é no máximo quatro, eu botei a
    #   lista dentro da célula.

  def add_adjacent_whitecell(self, cell:WhiteCell):
    self.adjacent_whitecells.append(cell)

  def is_satisfied(self) -> bool:
    return sum(1 for lamp in self.adjacent_whitecells if lamp.has_lamp) == \
      self.tip

  def is_broken(self) -> bool:
    return sum(1 for lamp in self.adjacent_whitecells if lamp.has_lamp) > \
      self.tip

  def __str__(self) -> str:
    return str(self.tip)
