from typing import Dict, List
from enum import Enum

import pygame

from stage import Stage
from screen import Screen

class Input(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    END = 4


##############
# 保留ここから #
#############
class Button:
    def __init__(self, rect: pygame.rect.Rect):
        self.rect = rect
        self.hover = False
        self.fnc = None
    
    def collidepoint(self, x: int, y: int) -> bool:
        self.rect.collidepoint(x, y)

class Choice:
    def __init__(self, value):
        self.value = value

class Select:
    def __init__(self, next_cmd, prev_cmd, choices: list):
        self.next_cmd = next_cmd
        self.prev_cmd = prev_cmd
        self.choices = [Choice(t) for t in choices]
        self.start_x
        self.start_y
        self.choice_width
        self.choice_height
        self.dx
        self.dy
        self.i = -1
    
    def decide(self):
        if self.i >= 0:
            return self.choices[self.i]
        else:
            return None
##############
# 保留ここまで #
##############


class StageSelectScreen:
    def __init__(self, stages: Dict[str, Stage], gamesetting):
        self.display = pygame.display.get_surface()
        self.rect = self.display.get_rect()
        self.stages = list(stages.values())
        self.selected_stage = 0
        self.margin_lr = 10
        self.margin_top = 50
        self.cols = 5
        self.rect_width = (self.rect.width - self.margin_lr * 2) // self.cols
        self.rect_height = self.rect_width
        self.stage_select_height = self.rect_height + 20
        self.select_rect = pygame.rect.Rect(
            self.margin_lr,
            self.margin_top,
            self.rect.width - self.margin_lr * 2,
            self.stage_select_height
        )
        self.stock = 3
        self.gamesetting = gamesetting
        self.stage_name_font = pygame.font.SysFont(None, 30)
        self.cooltime = 0.1
        self.nowtime = 0
        self.result = Screen.START
        self.run = True
    
    def get_inputs(self):
        inputs = []
        keys = pygame.key.get_pressed()
        # キー入力をInputに変換
        if keys[pygame.K_RETURN]:
            inputs.append(Input.END)
            return inputs
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            inputs.append(Input.UP)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            inputs.append(Input.DOWN)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            inputs.append(Input.LEFT)
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            inputs.append(Input.RIGHT)
        return inputs
    
    def hundle_inputs(self, inputs: List[Input]):
        if self.nowtime < 0:
            self.nowtime = self.cooltime
            for inp in inputs:
                if inp == Input.LEFT:
                    self.selected_stage = (self.selected_stage - 1) % len(self.stages)
                elif inp == Input.RIGHT:
                    self.selected_stage = (self.selected_stage + 1) % len(self.stages)
                elif inp == Input.END:
                    self.run = False
    
    def highlight(self, rect: pygame.rect.Rect, multiple: float):
        width = int(rect.width * multiple)
        height = int(rect.height * multiple)
        dx = (rect.width - width) // 2
        dy = (rect.height - height) // 2
        return pygame.rect.Rect(rect.x + dx, rect.y + dy, width, height), dx, dy
        
    def draw(self):
        self.display.fill((255, 255, 255))
        base = self.selected_stage
        
        h = self.cols // 2
        y = self.select_rect.y
        for i in range(self.cols):
            # 0, 1, 2, ..., self.cols
            i += 1
            if i > h:
                i -= self.cols
            # 1, 2, ..., h, -h, -h+1, ..., -1, 0

            stage_i = (self.selected_stage + i) % len(self.stages)
            
            x = self.select_rect.x + self.rect_width * (i + h)
            stage = self.stages[stage_i]
            rect = stage.thumbnail_rect(self.rect_width, self.rect_height)
            dx, dy = 0, 0
            if i == 0:
                rect, dx, dy = self.highlight(rect, multiple=1.5)
            self.display.blit(stage.image, (x+dx, y+dy), rect)
            font_x = x
            font_y = y + rect.height
            text = self.stage_name_font.render(stage.name, True, (0, 0, 0))
            d_x = (self.rect_width - text.get_rect().width) // 2
            self.display.blit(text, (font_x + d_x, font_y))
        
    def update(self, deltatime: float):
        self.nowtime -= deltatime
    
    def main(self):
        clock = pygame.time.Clock()
        self.run = True
        fps = 60
        deltatime = 1 / fps
        clock.tick(3)
        while self.run:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    self.result = Screen.QUIT
            inputs = self.get_inputs()
            # print(inputs)
            self.hundle_inputs(inputs)
            self.update(deltatime)
            self.draw()
            pygame.display.update()


class StartScreen:
    def __init__(self):
        self.display = pygame.display.get_surface()
        self.run = True
        self.result = Screen.STAGE_SELECT
    
    def draw(self):
        self.display.fill((255, 255, 255))
        pygame.display.update()
    
    def get_inputs(self):
        inputs = []
        keys = pygame.key.get_pressed()
        # キー入力をInputに変換
        if keys[pygame.K_RETURN]:
            inputs.append(Input.END)
        return inputs
    
    def hundle_inputs(self, inputs: List[Input]):
        if inputs:
            self.run = False
            self.result = Screen.STAGE_SELECT


    def main(self):
        clock = pygame.time.Clock()
        run = True
        fps = 60
        deltatime = 1 / fps
        clock.tick(3)
        while self.run:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    self.result = Screen.QUIT
            inputs = self.get_inputs()
            # print(inputs)
            self.hundle_inputs(inputs)
            self.draw()

def gen_sample_json():
    import os, json
    from PIL import Image, ImageDraw
    import matplotlib.colors as mcolors


    color_items = mcolors.TABLEAU_COLORS.items()

    images_dir = "./images/"
    jsons_dir = "./jsons/"

    dic = {}

    for i, (name, color) in enumerate(color_items):
        file_path = os.path.join(images_dir, f"stage_{i}.png")
        # 画像生成
        width = 500
        height=  500
        img = Image.new("RGB", (width, height), color)
        draw = ImageDraw.Draw(img)
        center = (width//2, height//2)
        topleft = (center[0] - 10, center[1] - 10)
        bottomright = (center[0] + 10, center[1] + 10)
        draw.ellipse((topleft, bottomright), "white")

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
    pygame.display.set_caption("画面遷移のテスト(Enterで切り替え)")
    stage_select_screen = StageSelectScreen
    start_screen = StartScreen
    # 最初の初期化がとても時間がかかるからいったん初期化しておく...なぜ?
    stage_select_screen(stages, None)
    start_screen()
    ########
    now = start_screen()
    while True:
        now.main()
        result = now.result
        if result == Screen.START:
            print("start screen")
            now = start_screen()
        elif result == Screen.STAGE_SELECT:
            print("stage select screen")
            now = stage_select_screen(stages, None)
        elif result == Screen.QUIT:
            print("end game")
            break