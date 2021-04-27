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

class AlignSprite(Sprite):
    def __init__(self, x: int, y: int, image: Surface, align="left", vertical_align="top"):
        super().__init__()
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
        self.image = image


class OutlineSprite(Sprite):
    def __init__(self, rect: Rect, image: Surface):
        super().__init__()
        self.rect = rect
        self.image = image.subsurface((0, 0, rect.w, rect.h))
    
    def __repr__(self):
        return "<OutlineSprite rect:{}>".format(self.rect)

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
        self.interval = interval
        self.image_index = 0
    
    @property
    def image(self):
        return self.images[self.image_index]
    
    def update(self):
        self.counter += 1
        if self.counter > self.interval:
            self.counter = 0
            self.image_index = (self.image_index + 1) % len(self.images)

def load_animation_sprite(x: int, y: int, images_dir: str, interval: int=0, multiple:float=1.0, align:str="center", vertical_align:str="middle") -> AnimationSprite:
    images = [pygame.image.load(image_path).convert_alpha() for image_path in sorted(glob.glob(os.path.join(images_dir, "*")))]
    return make_animation_sprites(x=x, y=y, images=images, interval=interval, multiple=multiple, align=align, vertical_align=vertical_align)

def make_animation_sprites(x: int, y: int, images: List[Surface], interval: int=0, multiple:float=1.0, align:str="center", vertical_align:str="middle") -> AnimationSprite:
    if multiple != 1.0:
        images = [pygame.transform.scale(image, (int(image.get_rect().w * multiple), int(image.get_rect().h * multiple))) for image in images]

    rect = images[0].get_rect()
    
    if align == "left":
        rect.left = x
    elif align == "right":
        rect.right = x
    else:
        rect.centerx = x

    if vertical_align == "top":
        rect.top = y
    elif vertical_align == "bottom":
        rect.bottom = y
    else:
        rect.centery = y
    
    return AnimationSprite(rect=rect, images=images, interval=interval)


def adjust_rect(rect: Rect, x: int, y: int, align: str="center", vertical_align: str="middle") -> Rect:
    if align == "left":
        rect.left = x
    elif align == "right":
        rect.right = x
    else:
        rect.centerx = x
    
    if vertical_align == "top":
        rect.top = y
    elif vertical_align == "bottom":
        rect.bottom = y
    else:
        rect.centery = y
    return rect


class RichSprite(Sprite):
    def __init__(self, x: int, y: int, align: str="center", vertical_align: str="middle", \
        image: Surface=None, images: List[Surface]=None, multiple: float=1.0, interval: int=0, \
        enter_fnc: Optional[Callable]=None, \
        enter_fnc_args: Optional[tuple]=None, \
        exit_fnc: Optional[Callable]=None, \
        exit_fnc_args: Optional[tuple]=None, \
        press_fnc: Optional[Callable]=None, \
        press_fnc_args: Optional[tuple]=None):
        if image is None and images is None:
            raise(TypeError("'image', 'images' のどちらか一方は None でない必要があります."))
        super().__init__()
        
        if images is not None:
            self.images = images
        else:
            self.images = [image]
        
        rect = self.images[0].get_rect().copy()
        self.rect = adjust_rect(rect, x, y, align=align, vertical_align=vertical_align)

        self.image_index = 0
        self.counter = 0
        self.interval = interval

        # マウスホーバー
        self.enter_fnc = None
        self.exit_fnc = None
        self.change_enter_fnc(enter_fnc, enter_fnc_args)
        self.change_exit_fnc(exit_fnc, exit_fnc_args)

        # マウスクリック
        self.press_fnc = None
        self.change_press_fnc(press_fnc, press_fnc_args)
    
    @property
    def image(self):
        return self.images[self.image_index]
    
    def change_enter_fnc(self, enter_fnc: Optional[Callable], enter_fnc_args: Optional[tuple]=None):
        """self.enter_fnc, self.enter_fnc_args を更新
        """
        self.enter_fnc = enter_fnc
        self.enter_fnc_args = enter_fnc_args
        self.hover = False
        self.check_hover = self.enter_fnc is not None or self.exit_fnc is not None
    
    def change_exit_fnc(self, exit_fnc: Optional[Callable], exit_fnc_args: Optional[tuple]=None):
        """self.exit_fnc, self.exit_fnc_args を更新
        """
        self.exit_fnc = exit_fnc
        self.exit_fnc_args = exit_fnc_args
        self.hover = False
        self.check_hover = self.enter_fnc is not None or self.exit_fnc is not None
    
    def change_press_fnc(self, press_fnc: Optional[Callable], press_fnc_args: Optional[tuple]=None):
        """self.press_fnc, self.press_fnc_args を更新
        """
        self.press_fnc = press_fnc
        self.pressed = False
        self.check_press = self.press_fnc is not None
        self.press_fnc_args = press_fnc_args

    def update(self):
        """更新処理
        """
        # アニメーションの場合はカウントする
        if len(self.images) > 1:
            self.counter += 1
            if self.counter > self.interval:
                self.counter = 0
                self.image_index = (self.image_index + 1) % len(self.images)
        # マウスとの当たり判定を行う
        if self.check_hover or self.check_press:
            mouse_pos = pygame.mouse.get_pos()
            collide = self.rect.collidepoint(*mouse_pos)
            # マウスホーバーチェックを行う
            if self.check_hover:
                if collide:  # hoverている
                    if not self.hover:  # 元々hoverしていなかった
                        self.hover = True
                        if self.enter_fnc is not None:  # enter_fncを実行
                            if self.enter_fnc_args is None:
                                self.enter_fnc()
                            else:
                                self.enter_fnc(*self.enter_fnc_args)
                else:   # hoverしていない
                    if self.hover:  # 元々hoverしていた
                        self.hover = False
                        if self.exit_fnc is not None:   # exit_fncを実行
                            if self.exit_fnc_args is None:
                                self.exit_fnc()
                            else:
                                self.exit_fnc(*self.exit_fnc_args)
            # マウス押下チェックを行う
            if self.check_press:
                now_pressed = pygame.mouse.get_pressed()[0]
                if collide:
                    if now_pressed and not self.pressed:
                        self.pressed = True
                        if self.press_fnc_args is None:
                            self.press_fnc()
                        else:
                            self.press_fnc(*self.press_fnc_args)
                    elif not now_pressed and self.pressed:
                        self.pressed = False
                        

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


def layout_rects(base_rect: Rect, cols: Optional[int]=None, rows: Optional[int]=None, item_width: Optional[int]=None, item_height: Optional[int]=None, padding: Optional[int]=None, padding_top: int=0, padding_bottom: int=0, padding_left: int=0, padding_right: int=0, margin_horizontal: int=0, margin_vertical: int=0) -> List[Rect]:
    """base_rectを均等に分割する．いろいろ指定可能性．

    Args:
        base_rect (Rect): [description]
        cols (Optional[int], optional): [description]. Defaults to None.
        rows (Optional[int], optional): [description]. Defaults to None.
        item_width (Optional[int], optional): [description]. Defaults to None.
        item_height (Optional[int], optional): [description]. Defaults to None.
        padding (Optional[int], optional): これを指定した場合，全てのpaddingの値をこれに統一する. Defaults to None.
        padding_top (int, optional): [description]. Defaults to 0.
        padding_bottom (int, optional): [description]. Defaults to 0.
        padding_left (int, optional): [description]. Defaults to 0.
        padding_right (int, optional): [description]. Defaults to 0.
        margin_horizontal (int, optional): [description]. Defaults to 0.
        margin_vertical (int, optional): [description]. Defaults to 0.

    Returns:
        List[Rect]: 分割したRectのリスト
    """
    if (cols is None and item_width is None):
        raise(TypeError("'cols' か 'item_width' のどちらか一方はNoneでない必要があります．"))
    if (rows is None and item_height is None):
        raise(TypeError("'rows' か 'item_height' のどちらか一方はNoneでない必要があります．"))
    
    if padding is not None:
        padding_top = padding_bottom = padding_left = padding_right = padding
    
    W = base_rect.w - padding_left - padding_right
    H = base_rect.h - padding_top - padding_bottom

    # 水平方向の処理
    if cols is not None and item_width is None: # colsのみ指定 -> item_width を計算
        item_width = (W - margin_horizontal * (cols - 1)) // cols
    elif cols is None and item_width is not None:  # item_widthのみの指定 -> cols を計算
        cols = (W + margin_horizontal) // (item_width + margin_horizontal)
    
    w = item_width * cols + margin_horizontal * (cols - 1)
    if w > W:
        raise(ValueError("指定された値では横幅がオーバーします．cols, item_width, padding_left, padding_rightの値を修正してください．"))
    base_x = base_rect.left + padding_left + (W - w) // 2
    if base_x < base_rect.left:
        raise(ValueError("水平方向エラーです．cols, item_width, padding_left, padding_rightの値を修正してください．"))

    # 垂直方向の処理
    if rows is not None and item_height is None: # rowsのみ指定 -> item_height を計算
        item_height = (H - margin_vertical * (rows - 1)) // rows
    elif rows is None and item_height is not None:  # item_heightのみの指定 -> rows を計算
        rows = (H + margin_vertical) // (item_height + margin_vertical)
    
    h = item_height * rows + margin_vertical * (rows - 1)
    if h > H:
        raise(ValueError("指定された値では横幅がオーバーします．rows, item_height, padding_top, padding_bottomの値を修正してください．"))
    base_y = base_rect.top + padding_top + (H - h) // 2
    if base_y < base_rect.top:
        raise(ValueError("水平方向エラーです．rows, item_height, padding_top, padding_bottomの値を修正してください．"))
    
    rects = []
    for i in range(rows):
        for j in range(cols):
            x = base_x + (item_width + margin_horizontal) * j
            y = base_y + (item_height + margin_vertical) * i
            rects.append(Rect(x, y, item_width, item_height))
    return rects


if __name__ == "__main__":
    rich_sprite = RichSprite(0, 0, image=0, images=None)
    pass