class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}

    def isempty(self):
        return len(self.players) == 0
    
    def add_player(self, name, client):
        if len(self.players) < 2 and name not in self.players:
            self.players[name] = client
            return True
        return False
    
    def remove_client(self, client):
        del self.players[client]

    def send(self, from_: str, message):
        to = list(self.players.keys() - {from_})[0]

        self.players[to].send(message)
