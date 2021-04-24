from typing import Dict, List, Callable, Tuple
from enum import Enum
import math
import random

import pygame
from pygame.locals import Rect
from pygame.sprite import Sprite

from stage import Stage
from screen import Screen, BaseScreen
from sprites import HoverRect, PressRect, SimpleSprite, TextSprite, make_outline_splites, load_animation_sprite
from component import CounterBtn
from game_config import GameConfig


class StageSelectScreen(BaseScreen):
    def __init__(self, game_config: GameConfig, gamesetting):
        super().__init__()
        # game_configから必要な情報を取り出す
        self.stages = game_config.stages
        self.gamesetting = gamesetting
        self.load_images(game_config)
        self.load_sounds(game_config)

        pygame.display.set_caption("ステージセレクト")

        self.hover_rects = {}
        self.press_rects = {}
        self.selected_stage = None
        self.stock = 3
        self.font_size_stage_title = 50
        self.font_stage_title = pygame.font.SysFont(None, self.font_size_stage_title)
        self.font_size_stock = 80
        self.font_stock = pygame.font.SysFont(None, self.font_size_stock)
        self.font_size = 40
        self.font = pygame.font.SysFont(None, self.font_size)
        self.stock_counter = None

        self.init()
    
    def _split_area(self):
        """ 表示領域を決定し，Rectとして保持する．
        """
        rect = self.display.get_rect()
        # 領域分割
        self.stage_view_rect = Rect(
            rect.x,
            rect.y,
            int(rect.width * 0.4),
            int(rect.height * 0.75)
        )
        self.stage_select_rect = Rect(
            self.stage_view_rect.right,
            self.stage_view_rect.y,
            rect.width - self.stage_view_rect.width,
            self.stage_view_rect.height
        )
        self.stock_rect = Rect(
            self.stage_view_rect.x,
            self.stage_view_rect.bottom,
            rect.width,
            rect.height - self.stage_view_rect.height
        )
        self.area = [self.stage_view_rect, self.stage_select_rect, self.stock_rect]

    def _set_stage_thumbnail_sprites(self):
        """ サムネイルを正方形のタイルにしてself.stage_select_rect上に並べる
        """
        cols = 3
        rows = math.ceil(len(self.stages) / cols)
        padding = 10
        tile_margin = 10
        rect = self.stage_select_rect
        rect = Rect(rect.x + padding, rect.y + padding, rect.w - padding * 2, rect.h - padding * 2)
        tile_width = min((rect.w - (cols - 1) * tile_margin) // cols, (rect.h - (rows - 1) * tile_margin) // rows)
        tile_height = tile_width
        
        left = rect.x + (rect.w - (tile_width * cols + tile_margin * (cols - 1))) // 2
        top = rect.y + (rect.h - (tile_height * rows + tile_margin * (rows - 1))) // 2
        thumbnail_sprites = []
        stages = list(self.stages.values())
        for i in range(rows):
            for j in range(cols):
                tmp = i * rows + j
                if tmp >= len(stages):
                    break
                stage = stages[tmp]
                x = left + j * (tile_width + tile_margin)
                y = top + i * (tile_height + tile_margin)
                
                thumbnail_rect = stage.thumbnail_rect(width=tile_width, height=tile_height)
                image = stage.image.subsurface(thumbnail_rect)

                sprite = SimpleSprite(Rect(x, y, tile_width, tile_height), image)
                self._add_hover_rect(sprite, self._visible_outlines, self._invisible_outlines)
                self._add_press_rect(sprite, self._select_stage, stage)
                thumbnail_sprites.append(sprite)
        self.thumbnail_sprites = thumbnail_sprites
        self.front_sprites.add(self.thumbnail_sprites)

    def _set_stock_counter(self):
        """ストックのカウンターを設置
        """
        counter_btn = CounterBtn(
            x=self.stock_rect.centerx,
            y=self.stock_rect.centery,
            min_=1,
            max_=5,
            font=self.font_stock,
            front_group=self.front_sprites,
            back_group=self.middle_sprites,
            color=(0, 0, 0),
            bgcolor=None,
            sound=self.click_sound,
        )
        self.stock_counter = counter_btn
        rect = counter_btn.rect
        stock_label = TextSprite(
            x=rect.right + 5,
            y=rect.top,
            text="stock",
            font=self.font_stock,
            color=(0, 0, 0),
            align="left",
            vertical_align="top",
        )
        self.middle_sprites.add(stock_label)

    def _set_back_btn(self):
        """戻るボタン設置
        """
        rect = self.display.get_rect()
        back_btn = TextSprite(
            x=rect.x + 5,
            y=rect.y + 5,
            text="<back",
            font=self.font,
            color=(0, 0, 0),
            align="left",
            vertical_align="top",
        )
        self.front_sprites.add(back_btn)
        
        self._add_hover_rect(back_btn, self._visible_outlines, self._invisible_outlines)
        self._add_press_rect(back_btn, self._go_back_character_select, None)
    
    def _set_next_btn(self):
        """進むボタン設置
        """
        rect = self.display.get_rect()
        next_btn = TextSprite(
            x=rect.right - 5,
            y=rect.y + 5,
            text="next>",
            font=self.font,
            color=(0, 0, 0),
            align="right",
            vertical_align="top",
        )
        self.front_sprites.add(next_btn)
        
        self._add_hover_rect(next_btn, self._visible_outlines, self._invisible_outlines)
        self._add_press_rect(next_btn, self._go_to_game, None)

    def _get_stage_big_thumbnails(self):
        """ self.stage_view_rect に合わせた表示のための画像の辞書を作成する
        """
        padding = 10
        rect = self.stage_view_rect
        w = rect
        image_rect = Rect(rect.x + padding, rect.y + padding, rect.w - padding * 2, rect.h - padding * 2)
        text_rect = Rect(
            image_rect.x,
            image_rect.bottom - self.font_size_stage_title - 5,
            image_rect.w,
            self.font_size_stage_title + 5,
        )
        self.stage_view_sprites = {}
        self.stage_name_sprites = {}
        for id_, stage in self.stages.items():
            thumbnail_rect = stage.thumbnail_rect(width=image_rect.w, height=image_rect.h)
            image = stage.image.subsurface(thumbnail_rect)
            stage_view_sprite = SimpleSprite(image_rect, image)
            stage_name_sprite = TextSprite(
                x=text_rect.centerx,
                y=text_rect.centery,
                text=stage.name,
                font=self.font_stage_title,
                color=(0, 0, 0),
                bgcolor=(255, 255, 255),
                align="center",
                vertical_align="middle"
            )
            self.stage_view_sprites[stage] = stage_view_sprite
            self.stage_name_sprites[stage] = stage_name_sprite
        # デフォルトのステージ(先頭)を選択しておく
        self._update_stage(list(self.stages.values())[0])

    def _load_background(self):
        """背景画像を読み込む (self.background_sprites に追加する)
        """
        bg_image = self.bg_image
        bg_sprite = SimpleSprite(bg_image.get_rect(), bg_image)
        self.background_sprites.add(bg_sprite) 

    def load_sounds(self, game_config: GameConfig):
        """サウンドを読み込む
        """
        self.bgm_sound = game_config.sounds["menu"]
        self.click_sound = game_config.sounds["click"]
        self.bgm_sound.set_volume(0.3)
        self.stage_sounds = {}
    
    def load_images(self, game_config: GameConfig):
        """Surfaceを読み込む
        """
        self.outline_image = game_config.components["outline"]
        self.bg_image = game_config.components["background"]

    def init(self):
        """初期化関数． 描画するスプライトグループを空にしてからいろいろ配置する
        """
        self.empty_all_sprites()
        self._split_area()
        self._set_stage_thumbnail_sprites()
        self._set_stock_counter()
        self._set_back_btn()
        self._set_next_btn()
        self._get_stage_big_thumbnails()
        self._load_background()

    def _add_hover_rect(self, sprite: Sprite, enter_fnc: Callable, exit_fnc: Callable):
        rect = sprite.rect
        hover_rect = HoverRect(rect, enter_fnc, exit_fnc)
        outline_sprites = make_outline_splites(rect, self.outline_image, border_width=3)
        self.hover_rects[hover_rect] = outline_sprites
    
    def _visible_outlines(self, hover_rect: HoverRect):
        """ hover_rect に対応した OutlineSprite を見えるようにする (self.middle_spritesに追加)
        """
        outline_sprites = self.hover_rects[hover_rect]
        self.middle_sprites.add(outline_sprites)
     
    def _invisible_outlines(self, hover_rect: HoverRect):
        """ hover_rect に対応した OutlineSprite を見えないようにする (self.middle_spritesから削除)
        """
        outline_sprites = self.hover_rects[hover_rect]
        self.middle_sprites.remove(outline_sprites)
    
    def _go_to_game(self, *args):
        """ゲーム画面に進む
        """
        print("go to game screen")
        print("stage: {}, stock: {}".format(self.selected_stage.name, self.stock))
        self.next_screen = Screen.GAME
        self.run = False

    def _go_back_character_select(self, *args):
        """キャラクター選択画面に戻る
        """
        print("go back to character select screen")
        self.next_screen = Screen.CHARACTER_SELECT
        self.run = False

    def _add_press_rect(self, sprite: Sprite, fnc: Callable, value):
        """ press_rect を self.press_rects に登録する
        """
        rect = sprite.rect
        press_rect = PressRect(rect, fnc)
        self.press_rects[press_rect] = value
    
    def _update_stage(self, new_stage: Stage):
        """ self.selected_stage を new_stage に置き換える
        """
        if new_stage is not self.selected_stage:
            if self.selected_stage is not None:
                # 前の選択ステージを解除
                stage_name_sprite = self.stage_name_sprites[self.selected_stage]
                if self.front_sprites.has(stage_name_sprite):
                    self.front_sprites.remove(stage_name_sprite)
                stage_view_sprite = self.stage_view_sprites[self.selected_stage]
                if self.middle_sprites.has(stage_view_sprite):
                    self.middle_sprites.remove(stage_view_sprite)
            # 選択ステージに更新
            self.selected_stage = new_stage
            stage_name_sprite = self.stage_name_sprites[self.selected_stage]
            if not self.front_sprites.has(stage_name_sprite):
                self.front_sprites.add(stage_name_sprite)
            stage_view_sprite = self.stage_view_sprites[self.selected_stage]
            if not self.middle_sprites.has(stage_view_sprite):
                self.middle_sprites.add(stage_view_sprite)

    def _select_stage(self, press_rect: PressRect):
        """ press_rect が呼び出す関数．self.selected_stage を更新する
        """
        self.click_sound.play()
        stage = self.press_rects[press_rect]
        self._update_stage(stage)       

    def main(self):
        self.bgm_sound.play(loops=-1)
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.next_screen = Screen.QUIT
                    self.run = False
            # hover_rectの更新
            for hover_rect in self.hover_rects:
                hover_rect.update()
            # press_rectの更新
            for press_rect in self.press_rects:
                press_rect.update()
            # componentsの更新
            self.stock_counter.update()
            self.stock = self.stock_counter.count
            
            self.update()
            self.draw()
            
            # # press_rect の領域表示
            # for press_rect in self.press_rects:
            #     pygame.draw.rect(self.display, (0, 0, 255), press_rect.rect, width=2)

            pygame.display.update()
        self.bgm_sound.stop()
        self.click_sound.stop()

def get_sample_stages(json_path="./jsons/stage.json"):
    """ json stages の サンプルを読み込む
    """
    import glob, json

    stages = {}

    with open(json_path, "r") as f:
        json_data = json.load(f)
    
    stages = {key: Stage(key, dic["name"], pygame.image.load(dic["path"])) for key, dic in json_data.items()}

    return stages

if __name__ == "__main__":

    pygame.init()
    pygame.display.set_mode((500, 500))

    game_config = GameConfig("./jsons/config.json")
    # exit()

    # stages = get_sample_stages(json_path="./jsons/stages2.json")
    gamesetting = None

    stage_select_screen = StageSelectScreen(game_config, gamesetting)
    stage_select_screen.main()