class KeyBind:
    def __init__(self, dic):
        self.A = ord(dic["A"])
        self.B = ord(dic["B"])
        self.C = ord(dic["C"])
    
    @property
    def keys(self):
        return [self.A, self.B, self.C]

class Player:
    def __init__(self, id_: str, name: str, matches_num: int, win_num: int, keybind: dict):
        self.id_ = id_
        self.name = name
        self.matches_num = matches_num
        self.win_num = win_num
        self.keybind = KeyBind(keybind)



