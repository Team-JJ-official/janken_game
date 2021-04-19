from typing import Tuple, NewType, Optional

import pygame
from pygame.locals import Rect
from pygame.surface import Surface

from sprites import TextSprite, PressRect

Color = NewType("Color", Tuple[int, int, int])

class CounterBtn:
    def __init__(self, x: int, y: int, min_: int, max_: int,
            font: pygame.font.Font,
            front_group: pygame.sprite.Group,
            back_group: pygame.sprite.Group,
            color: Color=(0, 0, 0),
            bgcolor: Optional[Color]=None,):
        """(x, y)を中心に，カウンターを設置する． カウント範囲は[min_, max_]．
        """
        self.min = min_
        self.max = max_
        self.count = min_
        self.front_group = front_group
        self.back_group = back_group
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
            self._update_count_sprite(self.count + 1)
    
    def _count_down(self, *args):
        if self.count > self.min:
            self._update_count_sprite(self.count - 1)
    
    def update(self):
        for press_rect in self.press_rects:
            press_rect.update()
