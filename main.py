from typing import List
from grid import Grid


def read_tabs_file(filename:str) -> List[Grid]:
  grid_list: List[Grid] = []  # return variable
  
  with open(filename) as file:
    # reading and formatting contents of filename
    text = file.readlines()

    # parsing for state variables
    is_parsing_grid = False
    current_grid_size = 0
    current_grid_str_list:List[str] = []

    # line parsing for
    for line_i, line in enumerate(text):
      if (len(line) > 0 and not line.isspace()): # ignore empty lines or
        # with whitespace only.

        # character whitespace filter and mistake checking
        charlist = []
        for c_i, c in enumerate(line):
          if not c.isspace(): # ignore leading, end or in-middle whitespace
            if c not in '.x01234':
              print(f"arquivo {filename}: caractere '{c}' não \
                    reconhecido.linha={line_i} coluna={c_i}.")
              raise RuntimeError
            charlist.append(c)
        clean_line = ''.join(charlist)
        
        # change line parsing for state
        if not is_parsing_grid:  # starts creating a new grid
          is_parsing_grid = True
          current_grid_size = len(clean_line)
          current_grid_str_list = []
          current_grid_str_list.append(clean_line)
        else:  # continue reading a already started grid
          if bad_size := len(clean_line) != current_grid_size:
            print(f'''arquivo {filename}: linha "{line}" de tamanho \
                  {bad_size} diferente das anteriores, de tamanho \
                  {current_grid_size}. linha={line_i}.''')
            raise RuntimeError
          current_grid_str_list.append(clean_line)

        if len(current_grid_str_list) == current_grid_size: # full grid read
          grid_list.append(Grid(current_grid_size, current_grid_str_list))
          is_parsing_grid = False
    # line parsing for end

    if is_parsing_grid: # file ended during a grid read.
      print(f'arquivo {filename}: file ended with incomplete grid.')
      raise RuntimeError
  
  return grid_list


if __name__=='__main__':
  input_filename = 'init_tabs.txt'
  grid_list = read_tabs_file(input_filename)

  for i, grid in enumerate(grid_list):
    print(i)
    grid.solve()
    print()
