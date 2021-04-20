import json

import pygame

from stage import Stage

class GameConfig:
    def __init__(self, json_path: str):
        with open(json_path, "r") as f:
            dic = json.load(f)
        self.dic = dic
        self.stages = {}
        self.characters = {}
        self.players = {}

        self.load()
    
    def load(self):
        self.load_stages()
        self.load_images()
    
    def load_stages(self):
        tmp_dic = self.dic.get("stage")
        if tmp_dic:
            with open(tmp_dic["path"], "r") as f:
                json_data = json.load(f)
            
            self.stages = {key: Stage(key, dic["name"], pygame.image.load(dic["path"])) for key, dic in sorted(json_data.items(), key=lambda x: -int(x[0]), reverse=True)}
            print(self.stages)
    
    def load_characters(self):
        pass

    def load_players(self):
        pass
    
    def load_images(self):
        import glob


if __name__ == "__main__":
    game_config = GameConfig("./jsons/config.json")