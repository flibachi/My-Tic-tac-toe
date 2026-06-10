from typing import List


class Board:
    def __init__(self, size: int = 3):
        self.size = size
        self.grid: List[List[int]] = [[0 for _ in range(size)] for _ in range(size)]

    def __str__(self):
        return '\n'.join([''.join(map(str, row)) for row in self.grid])