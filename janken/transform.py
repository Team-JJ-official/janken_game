from math import ceil

import pygame

from sprites import make_outline_splites

def surface_fit_to_rect(surface: pygame.surface.Surface, rect: pygame.rect.Rect) -> pygame.surface.Surface:
    """
    surfaceのアスペクト比を維持しつつrect内部を満たすsubsurfaceを返す\\
    surfaceとrectのcenterを揃え，rectからはみ出た部分が切り取られるようにsubsurfaceを返す
    """
    s_rect = surface.get_rect()
    amp = max(rect.width / s_rect.width, rect.height / s_rect.height)
    if amp != 1:
        tmpsurface = pygame.transform.smoothscale(surface, (ceil(s_rect.width * amp), ceil(s_rect.height * amp)))
    else:
        tmpsurface = surface.copy()
    tag_rect = rect.copy()
    s_rect = tmpsurface.get_rect()
    tag_rect.center = s_rect.center
    return tmpsurface.subsurface(tag_rect)

def to_hoverable(rich_sprite, outline_image, group=None, border_width: int=5):
    if group is None:
        return
    outlines = make_outline_splites(rich_sprite.rect, outline_image, border_width=border_width)
    rich_sprite.change_enter_fnc(group.add, (outlines,))
    rich_sprite.change_exit_fnc(group.remove, (outlines,))
    return outlines

if __name__ == '__main__':
    w = 100
    h = 100
    surface = pygame.Surface((w, h))
    for dx in [-10, 0, 10]:
        for dy in [-10, 0, 10]:
            rect = pygame.rect.Rect(0, 0, w + dx, h + dy)
            s = surface_fit_to_rect(surface, rect)
            print(s.get_rect(), rect)