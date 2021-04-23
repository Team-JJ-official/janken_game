import json

import pygame

from stage import Stage
from character import Character

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
        self.load_characters()
    
    def load_stages(self):
        tmp_dic = self.dic.get("stage")
        if tmp_dic:
            with open(tmp_dic["path"], "r") as f:
                json_data = json.load(f)
            
            self.stages = {key: Stage(key, dic["name"], pygame.image.load(dic["path"])) for key, dic in sorted(json_data.items(), key=lambda x: -int(x[0]), reverse=True)}
            print(self.stages)
    
    def load_characters(self):
        tmp_dic = self.dic.get("character", False)
        if tmp_dic:
            with open(tmp_dic["path"], "r") as f:
                json_data = json.load(f)
            self.characters = {
                key: Character(
                    id_=    key,
                    name=   dic["name"],
                    face=   pygame.image.load(dic["face_image_path"]),
                    gu=     pygame.image.load(dic["gu_image_path"]),
                    choki=  pygame.image.load(dic["choki_image_path"]),
                    pa=     pygame.image.load(dic["pa_image_path"])
                )
                for key, dic in json_data.items()
            }

    def load_players(self):
        pass
    
    def load_images(self):
        import glob


if __name__ == "__main__":
    game_config = GameConfig("./jsons/config.json")
    print(game_config.stages)