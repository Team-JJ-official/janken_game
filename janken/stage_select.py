from typing import Dict, List
from enum import Enum

import pygame

from stage import Stage


class Rect:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def inside(self, x: int, y: int):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

class Input(Enum):
    P1_LEFT = 0
    P1_RIGHT = 1
    P1_UP = 2
    P1_DOWN = 3
    P2_LEFT = 4
    P2_RIGHT = 5
    P2_UP = 6
    P2_DOWN = 7

class StageSelectScreen:
    def __init__(self, stages: Dict[str, Stage], gamesetting):
        self.display = pygame.display.get_surface()
        self.rect = self.display.get_rect()
        self.stages = list(stages.values())
        self.selected_stage = 0
        self.rect_width = 50
        self.rect_height = 50
        self.margin_lr = 10
        self.margin_top = 20
        self.stage_select_height = self.rect_height + 20
        self.select_rect = pygame.rect.Rect(
            self.margin_lr,
            self.margin_top,
            self.rect.width - self.margin_lr * 2,
            self.stage_select_height
        )
        self.cols = 5
        self.stock = 3
        self.gamesetting = gamesetting
    
    def get_inputs(self):
        inputs = []
        keys = pygame.key.get_pressed()
        # P1入力
        if keys[pygame.K_w]:
            inputs.append(Input.P1_UP)
        elif keys[pygame.K_s]:
            inputs.append(Input.P1_DOWN)
        if keys[pygame.K_a]:
            inputs.append(Input.P1_LEFT)
        elif keys[pygame.K_d]:
            inputs.append(Input.P1_RIGHT)
        # P2入力
        if keys[pygame.K_UP]:
            inputs.append(Input.P2_UP)
        elif keys[pygame.K_DOWN]:
            inputs.append(Input.P2_DOWN)
        if keys[pygame.K_LEFT]:
            inputs.append(Input.P2_LEFT)
        elif keys[pygame.K_RIGHT]:
            inputs.append(Input.P2_RIGHT)
        return inputs
    
    def hundle_inputs(self, inputs: List[Input]):
        for inp in inputs:
            inp

    
    def draw(self):
        self.display.fill((255, 255, 255))
        base = self.selected_stage
        h = self.cols // 2
        x = 0
        y = 10
        for i in range(self.cols):
            stage = self.stages[base - h + i]
            self.display.blit(stage.image, (x, y), stage.thumbnail_rect(self.rect_width, self.rect_height))
            x += self.rect_width
    
    def main(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False   
            inputs = self.get_inputs()
            print(inputs)
            self.draw()
            pygame.display.update()


def gen_sample_json():
    import os, json
    from PIL import Image
    import matplotlib.colors as mcolors


    color_items = mcolors.TABLEAU_COLORS.items()

    images_dir = "./images/"
    jsons_dir = "./jsons/"

    dic = {}

    for i, (name, color) in enumerate(color_items):
        file_path = os.path.join(images_dir, f"stage_{i}.png")
        img = Image.new("RGB", (500, 500), color)
        img.save(file_path)
        dic[i] = {
            "name": name.split(":")[1],
            "path": file_path,
        }
    
    with open(os.path.join(jsons_dir, "stage.json"), "w") as f:
        json.dump(dic, f, indent=4)

def get_sample_stages():
    import glob, json

    stages = {}

    json_path = "./jsons/stage.json"

    with open(json_path, "r") as f:
        json_data = json.load(f)
    
    stages = {key: Stage(key, dic["name"], pygame.image.load(dic["path"])) for key, dic in json_data.items()}

    return stages


if __name__ == "__main__":
    pygame.init()
    # gen_sample_json()
    stages = get_sample_stages()
    pygame.display.set_mode((500, 500))
    game = StageSelectScreen(stages=stages, gamesetting=None)
    game.main()