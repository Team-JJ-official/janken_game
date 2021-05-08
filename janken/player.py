class KeyBind:
    def __init__(self, dic):
        self.A = ord(dic["A"])
        self.B = ord(dic["B"])
        self.C = ord(dic["C"])

class Player:
    def __init__(self, _id: str, name: str, matches_num: int, win_num: int, keybind: dict):
        self._id = _id
        self.name = name
        self.matches_num = matches_num
        self.win_num = win_num
        self.keybind = KeyBind(keybind)



