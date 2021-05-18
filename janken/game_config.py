from typing import List, Union
import json
import os
import glob

import pygame

from stage import Stage
from character import Character
from player import Player

class GameConfig:
    def __init__(self, json_path: str):
        with open(json_path, "r") as f:
            dic = json.load(f)
        self.dic = dic
        self.stages = {}
        self.characters = {}
        self.players = {}
        self.components = {}

        self.check_pygame_inits()
        self.load()

    def check_pygame_inits(self):
        if not pygame.get_init():
            pygame.init()
    
    def load(self):
        """全てを読み込む
        """
        self.load_stages()
        self.load_characters()
        self.load_players()
        self.load_components()
        self.load_sounds()
    
    def _save_json(self, dic: dict, path: str):
        """辞書をJSON形式で保存する

        Args:
            dic (dict): 辞書
            path (str): 保存パス
        """
        with open(path, "w") as f:
            json.dump(dic, f, indent=4, ensure_ascii=False)
    
    def _load_json(self, path: str) -> dict:
        """JSONを読み込んで辞書を返す．
        """
        with open(path, "r") as f:
            dic = json.load(f)
        return dic
    
    def _do_transpalent(self, surface: pygame.surface.Surface):
        """透過できていないSurfaceを，(0, 0)の色で透過する
        """
        surface.set_colorkey(surface.get_at((0, 0)))
    
    def _load_surface(self, path: str, do_transpalent=False) -> pygame.surface.Surface:
        """ファイル名を指定すると，画像をSurfaceで読み込んで返す．\
        do_transpalent=Trueの場合は，背景を透過する．
        """
        surface = pygame.image.load(path)
        
        if pygame.display.get_surface():
            if do_transpalent:
                surface.convert_alpha()
                self._do_transpalent(surface)
            else:
                surface.convert()
        
        return surface
    
    def _load_surfaces(self, dir_path: str, do_transpalent=False) -> List[pygame.surface.Surface]:
        """ディレクトリを指定すると，内部のファイルを全て読み込んで\
        Surfaceのリストで返す．リストはファイル名でソートされている．\
        do_transpalent=Trueの場合は，背景を透過する．
        """
        surfaces = []
        for path in sorted(glob.glob(os.path.join(dir_path, "*"))):
            surfaces.append(self._load_surface(path, do_transpalent=do_transpalent))
        return surfaces
    
    def _load_surface_from_path_or_dir(self, path: str, do_transpalent=False) -> Union[pygame.surface.Surface, List[pygame.surface.Surface]]:
        """ファイル名を指定した場合はSurfaceを，\
        ディレクトリを指定した場合はSurfaceのリストを返す．\
        do_transpalent=Trueの場合は，背景を透過する．
        """
        if os.path.isdir(path):
            return self._load_surfaces(dir_path=path, do_transpalent=do_transpalent)
        else:
            return self._load_surface(path=path, do_transpalent=do_transpalent)
    
    def load_stages(self):
        """self.stagesにステージを読み込む．
        """
        tmp_dic = self.dic.get("stages")
        if tmp_dic:
            json_data = self._load_json(tmp_dic["path"])
            
            self.stages = {key: Stage(key, dic["name"], pygame.image.load(dic["path"])) for key, dic in sorted(json_data.items(), key=lambda x: -int(x[0]), reverse=True)}
    
    def load_characters(self):
        tmp_dic = self.dic.get("character", False)
        if tmp_dic:
            with open(tmp_dic["path"], "r") as f:
                json_data = json.load(f)
            self.characters = {
                key: Character(
                    id_=    key,
                    name=   dic["name"],
                    face=   self._load_surface(dic["face_image_path"]),
                    gu=     self._load_surface(dic["gu_image_path"]),
                    choki=  self._load_surface(dic["choki_image_path"]),
                    pa=     self._load_surface(dic["pa_image_path"]),
                    select_voice= self._load_sound(dic["select_voice_path"])
                )
                for key, dic in json_data.items()
            }

    def load_players(self):
        tmp_dic = self.dic.get("player", False)
        if tmp_dic:
            with open(tmp_dic["path"], "r") as f:
                json_data = json.load(f)
            self.players = {
                key: Player(
                    id_=    key,
                    name=   dic["name"],
                    matches_num= dic["matches_num"],
                    win_num= dic["win_num"],
                    keybind= dic["key_bind"]
                )
                for key, dic in json_data.items()
            }
    
    def save_players(self) -> bool:
        """プレイヤー情報を保存する

        Returns:
            bool: 保存成功したかどうか
        """
        tmp_dic = self.dic.get("player", False)
        if tmp_dic:
            save_path = tmp_dic["path"]
            dic = {}
            for key, player in self.players.items():
                dic[key] = player.to_dict()
            self._save_json(dic, save_path)
            return True
        else:
            return False

    def load_components(self):
        """self.componentsに，共通して使いそうな画像類を読み込む．
        """
        tmp_dic = self.dic.get("components")
        if tmp_dic:
            json_data = self._load_json(tmp_dic["path"])

            self.components = {
                name: self._load_surface_from_path_or_dir(dic["path"], do_transpalent=dic["do_transpalent"])
                for name, dic in json_data.items()
            }

    def _load_sound(self, path: str) -> pygame.mixer.Sound:
        """ファイルパスからSoundを読み込む
        """
        return pygame.mixer.Sound(path)
    
    def load_sounds(self):
        tmp_dic = self.dic.get("sounds")
        if tmp_dic:
            json_data = self._load_json(tmp_dic["path"])

            self.sounds = {
                name: self._load_sound(dic["path"])
                for name, dic in json_data.items()
            }


if __name__ == "__main__":
    game_config = GameConfig("./jsons/config.json")
    game_config.save_players()
    # print()
