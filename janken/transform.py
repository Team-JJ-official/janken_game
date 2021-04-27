from math import ceil

import pygame

def surface_fit_to_rect(surface: pygame.surface.Surface, rect: pygame.rect.Rect) -> pygame.surface.Surface:
    """
    surfaceのアスペクト比を維持しつつrect内部を満たすsubsurfaceを返す\\
    surfaceとrectのcenterを揃え，rectからはみ出た部分が切り取られるようにsubsurfaceを返す
    """
    s_rect = surface.get_rect()
    amp = 1
    if s_rect.width < rect.width or s_rect.height < rect.height:
        if rect.width / s_rect.width < rect.height / s_rect.height:
            amp = rect.height / s_rect.height
        else:
            amp = rect.width / s_rect.width
    else:
        if rect.width / s_rect.width < rect.height / s_rect.height:
            amp = rect.width / s_rect.width
        else:
            amp = rect.height / s_rect.height
    if amp != 1:
        surface = pygame.transform.smoothscale(surface, (ceil(s_rect.width * amp), ceil(s_rect.height * amp)))
    tag_rect = rect.copy()
    s_rect = surface.get_rect()
    tag_rect.center = s_rect.center
    return surface.subsurface(tag_rect)