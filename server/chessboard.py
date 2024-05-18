def genboard(size):
    return [[None for _ in range(size)] for _ in range(size)]


class ChessBoard:
    def __init__(self, size: int, players: list):
        self.size = size
        self.players = players

        self.board = {p: genboard(size) for p in players}

    def get(self, player, x, y):
        return self.board[player][x][y]
    
    def set(self, player, x, y, value):
        self.board[player][x][y] = value

    def place_boat(self, player, x, y):
        self.set(player, x, y, 'B')

    def attack(self, player, x, y):
        match self.get(player, x, y):
            case 'B':
                self.set(player, x, y, 'X')
            case None:
                return False

    def isdead(self, player):
        return not any('B' in row for row in self.board[player])
