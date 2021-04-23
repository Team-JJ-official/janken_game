from typing import List, Union
import json
import os
import glob

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
        """全てを読み込む
        """
        self.load_stages()
        self.load_components()
    
    def load_json(self, path: str) -> dict:
        """JSONを読み込んで辞書を返す．
        """
        with open(path, "r") as f:
            dic = json.load(f)
        return dic
    
    def _load_surface(self, path: str) -> pygame.surface.Surface:
        """ファイル名を指定すると，画像をSurfaceで読み込んで返す．
        """
        return pygame.image.load(path)
    
    def _load_surfaces(self, dir_path: str) -> List[pygame.surface.Surface]:
        """ディレクトリを指定すると，内部のファイルを全て読み込んで\
        Surfaceのリストで返す．リストはファイル名でソートされている．
        """
        surfaces = []
        for path in sorted(glob.glob(os.path.join(dir_path, "*"))):
            surfaces.append(self._load_surface(path))
        return surfaces
    
    def _load_surface_from_path_or_dir(self, path: str) -> Union[pygame.surface.Surface, List[pygame.surface.Surface]]:
        """ファイル名を指定した場合はSurfaceを，\
        ディレクトリを指定した場合はSurfaceのリストを返す．
        """
        if os.path.isdir(path):
            return self._load_surfaces(dir_path=path)
        else:
            return self._load_surface(path=path)
    
    def load_stages(self):
        """self.stagesにステージを読み込む．
        """
        tmp_dic = self.dic.get("stages")
        if tmp_dic:
            json_data = self.load_json(tmp_dic["path"])
            
            self.stages = {key: Stage(key, dic["name"], pygame.image.load(dic["path"])) for key, dic in sorted(json_data.items(), key=lambda x: -int(x[0]), reverse=True)}
            print(self.stages)
    
    def load_characters(self):
        pass

    def load_players(self):
        pass
    
    def load_components(self):
        """self.componentsに，共通して使いそうな画像類を読み込む．
        """
        tmp_dic = self.dic.get("components")
        if tmp_dic:
            json_data = self.load_json(tmp_dic["path"])

            self.components = {
                name: self._load_surface_from_path_or_dir(dic["path"])
                for name, dic in json_data.items()
            }


if __name__ == "__main__":
    game_config = GameConfig("./jsons/config.json")
    print()