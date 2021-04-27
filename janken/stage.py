from pygame.surface import Surface
from pygame.rect import Rect

class Stage:
    def __init__(self, id_: str, name: str, image: Surface):
        self.id = id_
        self.name = name
        self.image = image
    
    def thumbnail_image(self, width: int, height: int):
        return self.image.subsurface(self.thumbnail_rect(width, height))
    
    def thumbnail_rect(self, width: int, height: int):
        rect = self.image.get_rect()
        x = rect.centerx - width // 2
        y = rect.centery - height // 2
        return Rect(max(0, x), max(0, y), min(rect.w, width), min(rect.h, height))
