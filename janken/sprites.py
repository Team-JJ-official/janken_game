from typing import Callable, Optional, List, Tuple
import glob, os

import pygame
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.sprite import Sprite

"""
pygame.sprite.Sprite

必須属性
- self.rect: pygame.rect.Rect
- self.image: pygame.surface.Surface
"""

class SimpleSprite(Sprite):
    def __init__(self, rect: Rect, image: Surface):
        super().__init__()
        self.rect = rect
        self.image = image


class OutlineSprite(Sprite):
    def __init__(self, rect: Rect, image: Surface):
        super().__init__()
        self.rect = rect
        self.image = image.subsurface((0, 0, rect.w, rect.h))

def make_outline_splites(rect: Rect, image: Surface, border_width: int=5) -> List[OutlineSprite]:
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    b = border_width
    tmp_w = w + b * 2
    return [
        OutlineSprite(Rect(x-b, y-b, tmp_w, b), image), # 上
        OutlineSprite(Rect(x-b, y+h, tmp_w, b), image), # 下
        OutlineSprite(Rect(x-b, y, b, h), image),       # 左
        OutlineSprite(Rect(x+w, y, b, h), image),       # 右
    ]


class TextSprite(Sprite):
    def __init__(self, x: int, y: int, text: str, font: pygame.font.Font,
            color: Tuple[int, int, int]=(0, 0, 0), bgcolor: Optional[Tuple[int, int, int]]=None,
            align: str="left", vertical_align: str="top"):
        """テキストを描画するスプライト．(x, y)を基準に，align, vertical_alignで配置を決める．
        
               left    center    right
           top   .________.________.
                 |                 |
                 |                 |
                 |                 |
          middle .                 |
                 |                 |
                 |                 |
                 |                 |
          bottom .________ ________|
        """
        super().__init__()
        self.text = text
        self.font = font
        self.image = font.render(text, True, color, bgcolor)
        # rect計算
        rect = self.image.get_rect()
        # 水平方向配置
        if align == "right":
            x = x - rect.width
        elif align == "center":
            x = x - rect.width // 2
        else:   # left: default
            x = x
        # 鉛直方向配置
        if vertical_align == "bottom":
            y = y - rect.height
        elif vertical_align == "middle":
            y = y - rect.height // 2
        else:   # top: default
            y = y
        self.rect = Rect(x, y, rect.width, rect.height)


class AnimationSprite(Sprite):
    def __init__(self, rect: Rect, images: List[Surface], interval: int=0):
        super().__init__()
        self.rect = rect
        self.images = images
        self.counter = 0
        self.interval = 0
        self.image_index = 0
    
    @property
    def image(self):
        return self.images[self.image_index]
    
    def update(self):
        self.counter += 1
        if self.counter > self.interval:
            self.counter = 0
            self.image_index = (self.image_index + 1) % len(self.images)

def load_animation_sprite(images_dir: str, interval: int=0) -> AnimationSprite:
    for image_path in glob.glob(os.path.join(images_dir, "*")):
        print(image_path)


class HoverRect:
    def __init__(self, rect: Rect, enter_fnc: Callable, exit_fnc: Callable):
        """rectの範囲をマウスでhoverした時に，enter_fncを，hover解除した時にexit_fncを呼び出す
        """
        self.rect = rect
        self.hover = False
        self.enter_fnc = enter_fnc
        self.exit_fnc = exit_fnc
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(*mouse_pos):  # hoverしている
            if not self.hover:
                self.hover = True
                if self.enter_fnc is not None:
                    self.enter_fnc(self)
        else:   # hoverしていない
            if self.hover:
                self.hover = False
                if self.exit_fnc is not None:
                    self.exit_fnc(self)


class PressRect:
    def __init__(self, rect: Rect, fnc: Callable):
        """rectの範囲をマウスクリックした時にfncを呼び出す
        """
        self.rect = rect
        self.fnc = fnc
        self.pressed = False
    
    def update(self):
        pos = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]
        if self.rect.collidepoint(pos):
            if pressed and not self.pressed:
                self.pressed = True
                self.fnc(self)
            elif not pressed and self.pressed:
                self.pressed = False