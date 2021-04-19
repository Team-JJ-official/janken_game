import pygame

class Character:
    def __init__(self, id_: int, name: str):
        self.id = id_
        self.name = name
        self.face_image = None
        self.arm_image = None
    
    def set_face_image(self, image: pygame.Surface):
        self.face_image = image
    
    def set_arm_image(self, image: pygame.Surface):
        self.arm_image = image

