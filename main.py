from random import randint
import pickle
from copy import deepcopy
from copy import copy
from random import randrange


class Board:
    def __init__(self, height: int, width: int) -> None:
        self._height = height
        self._width = width
        self._table = [[0] * width for i in range(height)]

    def print_board(self) -> None:
        for i in range(self._height):
            print(*self._table[i])
        print()

    def __setitem__(self, pos: (int, int), value: int) -> None:
        row, column = pos
        self._table[row][column] = value

    def __getitem__(self, pos: (int, int)) -> int:
        row, column = pos
        return self._table[row][column]

    def get_table(self):
        return deepcopy(self._table)

    def save_table(self, file: str = "saves.pickle") -> None:
        with open(file, 'wb') as f:
            pickle.dump(self._table, f)

    def load_table(self, file: str = "saves.pickle") -> None:
        with open(file, 'rb') as f:
            self._table = pickle.load(f)


class Sudoku_board(Board):
    __BLOCK_LEN = 3
    __MISSED_CELL = -1
    __SEPARATOR = "."
    __MATRIX_LEN = __BLOCK_LEN * __BLOCK_LEN

    def print_board(self) -> None:
        for i in range(self.__MATRIX_LEN):
            if i % self.__BLOCK_LEN == 0 and i != 0:
                print(self.__SEPARATOR * (self.__MATRIX_LEN + self.__BLOCK_LEN - 1))
            for j in range(self.__MATRIX_LEN):
                if j % self.__BLOCK_LEN == 0 and j != 0:
                    print(self.__SEPARATOR, end="")
                if self._table[i][j] == self.__MISSED_CELL:
                    print(" ", end="")
                else:
                    print(self._table[i][j], end="")
            print()
        print()

    def get_block_len(self) -> int:
        return self.__BLOCK_LEN

    def get_missed_cell(self) -> int:
        return self.__MISSED_CELL

    def __init__(self) -> None:
        Board.__init__(self, self.__MATRIX_LEN, self.__MATRIX_LEN)
        self.__create_template()

    def __create_template(self) -> None:
        for i in range(self._height):
            for j in range(self._width):
                self._table[i][j] = ((i % 3) * 3 + (i // 3) + j) % 9 + 1

    def __transpose(self) -> None:
        for i in range(self._height):
            for j in range(i, self._width):
                self._table[i][j], self._table[j][i] = self._table[j][i], self._table[i][j]

    def __get_random_areas(self) -> (int, int):
        area1 = randrange(0, self.__BLOCK_LEN)
        area2 = (randrange(area1 + 1, self.__BLOCK_LEN + area1)) % self.__BLOCK_LEN  # Random area2 != area1
        return area1, area2

    def __get_random_block_lines(self) -> (int, int):
        block = randrange(0, self.__BLOCK_LEN)
        line1, line2 = self.__get_random_areas()
        return block * self.__BLOCK_LEN + line1, block * self.__BLOCK_LEN + line2

    def __swap_block_rows(self) -> None:
        row1, row2 = self.__get_random_block_lines()
        self._table[row1], self._table[row2] = self._table[row2], self._table[row1]

    def __swap_block_columns(self) -> None:
        self.__transpose()
        self.__swap_block_rows()
        self.__transpose()

    def __swap_big_rows(self) -> None:
        big_row1, big_row2 = self.__get_random_areas()
        for i in range(self.__BLOCK_LEN):
            self._table[big_row1 * self.__BLOCK_LEN + i], self._table[big_row2 * self.__BLOCK_LEN + i] = \
                self._table[big_row2 * self.__BLOCK_LEN + i], self._table[big_row1 * self.__BLOCK_LEN + i]

    def __swap_big_columns(self) -> None:
        self.__transpose()
        self.__swap_big_rows()
        self.__transpose()

    __GENERATING_LIST = [__transpose, __swap_big_columns,
                         __swap_block_rows, __swap_block_rows, __swap_block_columns]

    def generate(self, skipped) -> bool:
        self.__create_template()
        epochs = 20
        for _ in range(epochs):
            self.__GENERATING_LIST[randrange(0, len(self.__GENERATING_LIST))](self)
        return self.__remove_cells(skipped)

    def variants(self, row: int, column: int) -> set:
        n = self.__BLOCK_LEN
        all_variants = set(i for i in range(1, n ** 2 + 1))
        row_set = set()
        column_set = set()
        block_set = set()
        for i in range(n ** 2):
            column_set.add(self[i, column])
            row_set.add(self[row, i])
            block_set.add(self[(row // n * n + i % n, column // n * n + i // n)])
        return all_variants - (row_set | column_set | block_set)

    def best_cell(self) -> (int, int):
        n = self.get_block_len()
        min_var_numb = n ** 2
        cords = (self.get_missed_cell(), self.get_missed_cell())
        for i in range(n ** 2):
            for j in range(n ** 2):
                if self[i, j] == self.get_missed_cell():
                    var_numb = len(self.variants(i, j))
                    if var_numb < min_var_numb:
                        min_var_numb = var_numb
                        cords = (i, j)
        return cords

    def __remove_cells(self, numb: int) -> bool:
        cells_list = [(i, j) for i in range(self.__MATRIX_LEN) for j in range(self.__MATRIX_LEN)]
        removed = 0
        while len(cells_list) != 0 and removed != numb:
            cell = cells_list[randrange(0, len(cells_list))]
            cells_list.remove(cell)
            value = self._table[cell[0]][cell[1]]
            self._table[cell[0]][cell[1]] = self.__MISSED_CELL
            variants = self.variants(*cell)
            for digit in variants:
                if digit != value:
                    if Sudoku_solver.solve(self, False):
                        self._table[cell[0]][cell[1]] = value
                        break
            else:
                removed += 1
        return removed == numb

    def __copy__(self):
        sudoku_copy = type(self)()
        sudoku_copy._table = deepcopy(self._table)
        return sudoku_copy


class Sudoku_solver:
    @staticmethod
    def solve(sudoku: Sudoku_board, is_show: bool = True) -> bool:
        cords = sudoku.best_cell()
        if cords[0] == sudoku.get_missed_cell():
            if is_show:
                sudoku.print_board()
            return True
        variants = sudoku.variants(*cords)
        for digit in variants:
            sudoku_copy = copy(sudoku)
            sudoku_copy[cords[0], cords[1]] = digit
            if is_show:
                print(*cords, digit)
                sudoku.print_board()
            if Sudoku_solver.solve(sudoku_copy, is_show):
                return True
        return False


class Sudoku_game:
    def __init__(self):
        self.sudoku = Sudoku_board()

    def generate(self, missed: int):
        return self.sudoku.generate(missed)

    def compute(self):
        Sudoku_solver.solve(self.sudoku)

    def load(self, *args):
        try:
            self.sudoku.load_table(*args)
            self.sudoku.print_board()
        except FileNotFoundError:
            print("File not found")

    def save(self, *args):
        try:
            self.sudoku.save_table(*args)
        except FileNotFoundError:
            print("File not found")

    def begin(self):
        try:
            if not self.generate(int(input())):
                print("Algorithm cannot create this sudoku")
                self.begin()
        except ValueError:
            print("Wrong format")
            self.begin()
        self.sudoku.print_board()
        while self.sudoku.best_cell()[0] != self.sudoku.get_missed_cell():
            s = input().split()
            if s[0] == "new":
                self.begin()
            if s[0] == "load":
                if len(s) != 1:
                    self.load(s[1])
                else:
                    self.load()
                continue
            if s[0] == "save":
                if len(s) != 1:
                    self.save(s[0])
                else:
                    self.save()
                continue
            if s[0] == "compute":
                self.compute()
                break
            try:
                row, column, value = map(int, s)
                self.sudoku[row - 1, column - 1] = value
                self.sudoku.print_board()
            except ValueError:
                print("Wrong format")


Sudoku = Sudoku_game()
Sudoku.begin()
