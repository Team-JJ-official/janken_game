from pygame import Surface

class Character:
    def __init__(self, id_: str, name: str, face: Surface, gu: Surface, choki: Surface, pa: Surface):
        self.id = id_
        self.name = name
        self.face_image = face
        self.arm_image = [gu, choki, pa]
    
    def set_face_image(self, image: Surface):
        self.face_image = image

