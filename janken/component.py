from typing import Tuple, NewType, Optional, Dict, Callable, Any, Union, List

import pygame
import pygame.gfxdraw
from pygame.locals import Rect
from pygame.surface import Surface
from pygame.sprite import Sprite

from sprites import TextSprite, PressRect
from sprites import RichSprite, SimpleSprite, adjust_rect
from group import Group
from transform import surface_fit_to_rect

Color = NewType("Color", Tuple[int, int, int])

class CounterBtn:
    def __init__(self, x: int, y: int, min_: int, max_: int,
            font: pygame.font.Font,
            front_group: pygame.sprite.Group,
            back_group: pygame.sprite.Group,
            color: Color=(0, 0, 0),
            bgcolor: Optional[Color]=None,
            sound: Optional[pygame.mixer.Sound]=None
        ):
        """(x, y)を中心に，カウンターを設置する． カウント範囲は[min_, max_]．
        """
        self.min = min_
        self.max = max_
        self.count = min_
        self.front_group = front_group
        self.back_group = back_group
        self.sound = sound
        self.press_rects = []

        # カウンター表示のためのスプライトの生成
        left = x
        right = x
        top = y
        self.sprites = []
        for i in range(min_, max_+1):
            num_sprite = TextSprite(
                x=x,
                y=y,
                text=str(i),
                font=font,
                color=color,
                bgcolor=bgcolor,
                align="center",
                vertical_align="middle",
            )
            self.sprites.append(num_sprite)
            left = min(left, num_sprite.rect.left)
            right = max(right, num_sprite.rect.right)
            top = min(top, num_sprite.rect.top)
        # 現在のスプライトを追加
        self.front_group.add(self._get_sprite())
        # 操作ボタン(左)の追加
        self.left_btn_sprite = TextSprite(
            x=left,
            y=top,
            text="<",
            font=font,
            color=color,
            bgcolor=bgcolor,
            align="right",
            vertical_align="top",
        )
        self.front_group.add(self.left_btn_sprite)
        self.press_rects.append(PressRect(self.left_btn_sprite.rect, self._count_down))
        # 操作ボタン(右)の追加
        self.right_btn_sprite = TextSprite(
            x=right,
            y=top,
            text=">",
            font=font,
            color=color,
            bgcolor=bgcolor,
            align="left",
            vertical_align="top",
        )
        self.front_group.add(self.right_btn_sprite)
        self.press_rects.append(PressRect(self.right_btn_sprite.rect, self._count_up))

        self.rect = Rect(
            self.left_btn_sprite.rect.left,
            self.left_btn_sprite.rect.top,
            self.right_btn_sprite.rect.right - self.left_btn_sprite.rect.left,
            self.left_btn_sprite.rect.height,
        )
    
    def _get_sprite(self):
        return self.sprites[self.count - self.min]

    def _update_count_sprite(self, new_count: int):
        self.front_group.remove(self._get_sprite())
        self.count = new_count
        self.front_group.add(self._get_sprite())

    def _count_up(self, *args):
        if self.count < self.max:
            if self.sound is not None:
                self.sound.play()
            self._update_count_sprite(self.count + 1)
    
    def _count_down(self, *args):
        if self.count > self.min:
            if self.sound is not None:
                self.sound.play()
            self._update_count_sprite(self.count - 1)
    
    def update(self):
        for press_rect in self.press_rects:
            press_rect.update()

class CounterSprite(Sprite):
    def __init__(self, x: int, y: int, font: pygame.font.Font, align: str="center", vertical_align: str="middle", min_: int=1, max_: int=5, color: Color=(0, 0, 0)):
        super().__init__()
        self.min = min_
        self.max = max_
        self.images = [font.render(str(i), True, color) for i in range(min_, max_+1)]
        self.rects = [adjust_rect(image.get_rect(), x, y, align, vertical_align) for image in self.images]
        left = right = x
        top = bottom = y
        for rect in self.rects:
            left = min(left, rect.left)
            right = max(right, rect.right)
            top = min(top, rect.top)
            bottom = max(bottom, rect.bottom)
        self.base_rect = Rect(left, top, right - left, bottom - top)
        self.count = min_
    
    def _count_up(self):
        if self.count < self.max:
            self.count += 1
    
    def _count_down(self):
        if self.count > self.min:
            self.count -= 1
    
    def get_count(self):
        return self.count
    
    @property
    def rect(self):
        return self.rects[self.count - self.min]
    
    @property
    def image(self):
        return self.images[self.count - self.min]


def make_counter_btn(x: int, y: int, font: pygame.font.Font, align: str="center", vertical_align: str="middle", min_: int=1, max_: int=5, color: Color=(0, 0, 0)):
    group = pygame.sprite.Group()
    counter_sprite = CounterSprite(x, y, font, align, vertical_align, min_, max_, color)
    group.add(counter_sprite)
    rect = counter_sprite.base_rect
    w = h = rect.h
    w = w // 3
    points = [
        (0, h//2),
        (w-1, h*0.8-1),
        (w-1, h*0.2)
    ]
    x, y = rect.topleft
    left_image = Surface((w, h)).convert_alpha()
    left_image.fill((255, 255, 255))
    left_image.set_colorkey(left_image.get_at((0, 0)))
    pygame.gfxdraw.filled_polygon(left_image, points, color)
    # left_image = font.render("<", True, color)
    btn = RichSprite(x-5, y, align="right", vertical_align="top", image=left_image, press_fnc=counter_sprite._count_down)
    group.add(btn)
    x, y = rect.topright
    right_image = pygame.transform.flip(left_image, True, False)
    right_image.set_colorkey(right_image.get_at((0, 0)))
    btn = RichSprite(x+5, y, align="left", vertical_align="top", image=right_image, press_fnc=counter_sprite._count_up)
    group.add(btn)
    return group, counter_sprite.get_count


class PlayerStockIcon(Group):
    def __init__(self, left: int, top: int, game_player, image_height: int=50):
        super().__init__()

        self.game_player = game_player

        surface = game_player.character.face_image
        name = game_player.player.name
        stock = game_player.stock

        # キャラ画像
        image_width = image_height
        rect = Rect(left, top, image_width, image_height)
        image = surface_fit_to_rect(surface, rect)
        self.character_sprite = SimpleSprite(rect, image)
        self.add(self.character_sprite)

        # ストックの丸
        self.stock = stock
        self.stock_sprites = [Group() for i in range(stock)]
        x, y = self.character_sprite.rect.bottomright
        stock_radius = int(0.05 * image_height)
        left, top = x, y - stock_radius * 2
        for i in range(stock):
            surface = Surface((stock_radius * 2, stock_radius * 2)).convert_alpha()
            surface.fill((125, 125, 125))
            surface.set_colorkey(surface.get_at((0, 0)))
            pygame.gfxdraw.filled_circle(surface, stock_radius, stock_radius, stock_radius-1, (255, 255, 255))
            stock_sprite = SimpleSprite(Rect(left, top, stock_radius * 2, stock_radius * 2), surface)
            self.stock_sprites[i].add(stock_sprite)
            print(self.stock_sprites[i])
            left += stock_radius * 2

        # プレイヤーネーム
        font_size = int(0.2 * image_height)
        font = pygame.font.Font(None, font_size)
        left, bottom = self.character_sprite.rect.bottomright
        bottom -= stock_radius * 2
        self.player_name_sprite = TextSprite(
            x=left,
            y=bottom,
            align="left",
            vertical_align="bottom",
            text=name,
            font=font,
            color=(255, 255, 255)
        )
        self.add(self.player_name_sprite)

        # プレイヤーネームのbg
        width = self.character_sprite.rect.w + max(stock_radius * 2 * stock, self.player_name_sprite.rect.w) + 10
        height = self.character_sprite.rect.h
        self.base_rect = Rect(*self.character_sprite.rect.topleft, width, height)
        rect = self.base_rect
        bg_image = Surface(rect.size).convert_alpha()
        bg_image.fill((0, 0, 0))
        bg_image.set_alpha(225)
        bg_sprite = SimpleSprite(rect, bg_image)
        self.bg_group = Group()
        self.bg_group.add(bg_sprite)
    
    def change_stock_delta(delta: int):
        self.stock += delta
    
    def draw(self, surface: Surface):
        self.bg_group.draw(surface)
        super().draw(surface)
        for i in range(self.game_player.stock):
            group = self.stock_sprites[i]
            # print(group, end=", ")
            group.draw(surface)
        # print()


class KeyHandler(Group):
    def __init__(self, key_to_fnc_dic: Dict[int, Tuple[Callable, Any]]):
        """キー入力に関数を割り当てる部品

        Args:
            key_to_fnc_dic (dict): pygame.K_***がキー，関数，引数のタプルがバリューの辞書
        """
        super().__init__()
        self.key_to_fnc_dic = key_to_fnc_dic
        self.waiting_inputs = True
        self.pressed = {key: False for key in self.key_to_fnc_dic.keys()}
    
    def stop(self):
        self.waiting_inputs = False
    
    def resume(self):
        self.waiting_inputs = True
    
    def update(self):
        if self.waiting_inputs:
            key_pressed = pygame.key.get_pressed()
            for key, (fnc, args) in self.key_to_fnc_dic.items():
                if not self.pressed[key] and key_pressed[key]:  # 押した瞬間のみ
                    self.pressed[key] = True
                elif self.pressed[key] and not key_pressed[key]: # 離した瞬間のみ
                    self.pressed[key] = False
                    fnc(args)
                    self.stop()

class Checker(Group):
    def __init__(self, check_fncs: Union[Callable, List[Callable]], fnc: Callable, fnc_args: Any=None, stop_when_call_fnc=True):
        """チェック関数が全てTrueのときにfnc(fnc_args)を呼び出す部品

        Args:
            check_fncs (Union[Callable, List[Callable]]): チェックする関数(のリスト)
            fnc (Callable): チェックを通った場合に呼ばれる関数
            fnc_args (Any, optional): チェック通った場合に呼ばれる関数に渡される引数. Noneの場合は渡されない. Defaults to None.
            stop_when_call_fnc (bool, optional): fncを呼び出した後にチェックをやめるかどうか. Defaults to True.
        """
        super().__init__()

        self.do_check = True
        self.check_fncs = check_fncs if type(check_fncs) is list else [check_fncs]
        self.fnc = fnc
        self.fnc_args = fnc_args
        self.stop_when_call_fnc = stop_when_call_fnc
    
    def stop(self):
        self.do_check = False
    
    def resume(self):
        self.do_check = True
    
    def update(self):
        if self.do_check:
            if all(fnc() for fnc in self.check_fncs):
                # チェック作業を一旦停止する
                if self.stop_when_call_fnc:
                    self.stop()
                # 関数を呼び出す
                if self.fnc_args is not None:
                    self.fnc(self.fnc_args)
                else:
                    self.fnc()



if __name__ == "__main__":
    pygame.init()
    btn = CounterBtn(0, 0, pygame.font.SysFont(None, 10))
    btn.update()
    btn.draw(None)
        