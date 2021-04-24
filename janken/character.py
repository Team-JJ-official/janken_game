from pygame import Surface
from pygame.mixer import Sound

class Character:
    def __init__(self, id_: str, name: str, face: Surface, gu: Surface, choki: Surface, pa: Surface, select_voice: Sound):
        self.id = id_
        self.name = name
        self.face_image = face
        self.arm_image = [gu, choki, pa]
        self.select_voice = select_voice
    
    def set_face_image(self, image: Surface):
        self.face_image = image

