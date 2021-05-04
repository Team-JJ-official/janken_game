from enum import Enum

import pygame
from pygame.rect import Rect

from screen import Screen, BaseScreen
from sprites import RichSprite, SimpleSprite, layout_rects, TextSprite
from component import PlayerStockIcon, KeyHandler, Checker, TimerGroup
from transform import surface_fit_to_rect
from game_config import GameConfig
from group import Group

class GameScreen(BaseScreen):
    class Hand(Enum):
        ROCK = 0
        PAPER = 1
        SCISSORS = 2

    class Actor:
        def __init__(self, game_player):
            self.game_player = game_player
            self.hand = None
        
        def done(self) -> bool:
            return self.hand is not None
    
        def set_hand(self, hand):
            print(self, "set hand:", hand)
            self.hand = hand
        
        def reset(self):
            self.hand = None
        
        def decrease_stock(self):
            self.game_player.stock -= 1
            return self.game_player.stock
        
        def __repr__(self):
            return "<Actor: {}>".format(self.game_player)
        

    def __init__(self, game_player1, game_player2, game_setting):
        """ゲーム画面

        Args:
            game_player1 (GamePlayer): プレイヤー情報(Player, Character, stock(player's rest stock))
            game_player2 (GamePlayer): プレイヤー情報(Player, Character, stock(player's rest stock))
            game_setting (GameSetting): ゲーム情報(stage, stock(先取))
        """
        super().__init__()
        game_config = GameConfig("./jsons/config.json")

        if game_player1 is None:
            game_player1 = get_sample_game_player(game_config, name="sample1")
        else:
            game_player1 = game_player1
            if game_player1.character is None or game_player1.player is None:
                game_player1 = get_sample_game_player(game_config, name="sample1")
        if game_player2 is None:
            game_player2 = get_sample_game_player(game_config, name="sample2")
        else:
            game_player2 = game_player2
            if game_player2.character is None or game_player2.player is None:
                game_player2 = get_sample_game_player(game_config, name="sample2")
        if game_setting is None:
            self.game_setting = get_sample_game_setting(game_config, stock=5)
        else:
            self.game_setting = game_setting
        
        self.actor1 = self.Actor(game_player1)
        self.actor2 = self.Actor(game_player2)

        self.font = pygame.font.Font(None, 60)

        self.yattane = pygame.mixer.Sound("./sounds/yattane.mp3")
        self.uu = pygame.mixer.Sound("./sounds/uu.mp3")
        self.sokomade = pygame.mixer.Sound("./sounds/sokomade.mp3")

        self.init()
    
    def init(self):
        """初期化処理を行う
        """
        self._set_area()
        self._set_bg()
        self._init_game()
        self._set_player_icons()
        # self._set_random_btn()
        self._set_key_handler()
        self._set_checker()
        self._set_animation()

        self._reset()
    
    def _set_area(self):
        rect = self.display.get_rect()
        area_rects = layout_rects(rect, 2, 3)
        self.view_area = area_rects[0].union(area_rects[3])
        self.icon_area = area_rects[4].union(area_rects[5])

    
    def _set_bg(self):
        """背景画像の設置．game_setting.stageを参照．
        """
        print(self.game_setting.stage)
        rect = self.display.get_rect()
        bg_image = self.game_setting.stage.image
        bg_image = surface_fit_to_rect(bg_image, rect)
        self.bg_sprite = SimpleSprite(rect, bg_image)
        self.background_sprites.add(self.bg_sprite)

    def _init_game(self):
        """ゲームの初期化
        """
        self.actor1.game_player.stock = self.game_setting.stock
        self.actor2.game_player.stock = self.game_setting.stock

    def _set_player_icons(self):
        """プレイヤーアイコンの設置
        """
        rects = layout_rects(self.icon_area, 2, 1, padding=30)
        game_players = [self.actor1.game_player, self.actor2.game_player]
        for game_player, rect in zip(game_players, rects):
            player_icon_sprite = PlayerStockIcon(
                left=rect.left,
                top=rect.top,
                game_player=game_player,
                image_height=100
            )
            self.middle_sprites.add(player_icon_sprite)
    
    def _set_random_btn(self):
        """(デバッグ)ランダム勝敗ボタンの設置
        """
        rect = self.display.get_rect()
        surface = self.font.render("random result", True, (255, 255, 255), (0, 0, 0))
        random_result_btn = RichSprite(rect.w//2, rect.h // 3, image=surface, press_fnc=self._random_result)
        self.middle_sprites.add(random_result_btn)
    
    def _random_result(self):
        """ランダムに勝敗をつける関数
        """
        import random
        players = [self.actor1.game_player, self.actor2.game_player]
        win_i = random.randint(0, 1)
        players[win_i].stock = 1
        players[(win_i + 1) % 2].stock = 0

        print("player {} win.".format(players[win_i].player.name))

        self._go_to_result()

    def _set_key_handler(self):
        """プレイヤーの入力を処理するGroupの設置
        """
        self.key_handers = []
        for actor, keys in zip([self.actor1, self.actor2], [(pygame.K_1, pygame.K_2, pygame.K_3), (pygame.K_8, pygame.K_9, pygame.K_0)]):
            key_to_fnc_dic = {
                keys[0]: (self._set_hand, (actor, self.Hand.ROCK)),
                keys[1]: (self._set_hand, (actor, self.Hand.SCISSORS)),
                keys[2]: (self._set_hand, (actor, self.Hand.PAPER)),
            }
            key_hundler = KeyHandler(key_to_fnc_dic)
            self.middle_sprites.add(key_hundler)
            self.key_handers.append(key_hundler)
    
    def _set_checker(self):
        """チェッカーGroupの設置
        """
        self.checkers = []
        # プレイヤー1, 2が入力完了したかどうかを監視するもの
        key_done_checker = Checker([self.actor1.done, self.actor2.done], self._start_battle_before_animation, stop_when_call_fnc=True)
        self.middle_sprites.add(key_done_checker)
        self.checkers.append(key_done_checker)
    
    def _judge(self):
        """勝ち負け判定
        """
        win_actor = None
        rest = 1
        if self.actor1.hand == self.actor2.hand:
            pass    # あいこ
        elif (self.actor1.hand == self.Hand.ROCK and self.actor2.hand == self.Hand.SCISSORS) or \
            (self.actor1.hand == self.Hand.PAPER and self.actor2.hand == self.Hand.ROCK) or \
            (self.actor1.hand == self.Hand.SCISSORS and self.actor2.hand == self.Hand.PAPER):
            # actor1の勝ち
            rest = self.actor2.decrease_stock()
            win_actor = self.actor1
        else:
            # actor2の勝ち
            rest = self.actor1.decrease_stock()
            win_actor = self.actor2
        
        self._start_battle_after_animation(win_actor)
        # self._reset()
    
    def _set_animation(self):
        """アニメーションの設定
        """
        self.timer_group = TimerGroup()
        self.middle_sprites.add(self.timer_group)

        rects = layout_rects(self.view_area, 2, 1, padding=40, margin_vertical=40)
        self.hand_sprites = {
            self.actor1: {
                self.Hand.ROCK: SimpleSprite(rects[0], self.actor1.game_player.character.arm_image[0]),
                self.Hand.SCISSORS: SimpleSprite(rects[0], self.actor1.game_player.character.arm_image[1]),
                self.Hand.PAPER: SimpleSprite(rects[0], self.actor1.game_player.character.arm_image[2]),
            },
            self.actor2: {
                self.Hand.ROCK: SimpleSprite(rects[1], self.actor2.game_player.character.arm_image[0]),
                self.Hand.SCISSORS: SimpleSprite(rects[1], self.actor2.game_player.character.arm_image[1]),
                self.Hand.PAPER: SimpleSprite(rects[1], self.actor2.game_player.character.arm_image[2]),
            }
        }
        wait_surface = self.font.render("wait", True, (0, 0, 0), (255, 255, 255))
        ready_surface = self.font.render("ready", True, (0, 0, 0), (255, 255, 255))
        self.actor_state_sprites = {
            self.actor1: {
                True: SimpleSprite(rects[0], ready_surface),
                False: SimpleSprite(rects[0], wait_surface),
            },
            self.actor2: {
                True: SimpleSprite(rects[1], ready_surface),
                False: SimpleSprite(rects[1], wait_surface),
            }
        }
        self.actor_state_group = Group()
        self.middle_sprites.add(self.actor_state_group)
    
    def _start_battle_before_animation(self):
        """バトルアニメーションを開始
        """
        dummy = Group()
        self.timer_group.add_timer_sprite(dummy, timer=30, on_delete_fnc=self._start_battle_hand_animation)

    def _start_battle_hand_animation(self):
        """手を出すアニメーションを開始
        """
        self.actor_state_group.empty()
        group = Group()
        for actor in [self.actor1, self.actor2]:
            sprite = self.hand_sprites[actor][actor.hand]
            group.add(sprite)
        self.timer_group.add_timer_sprite(group, timer=60, on_delete_fnc=self._judge)
    
    def _start_battle_after_animation(self, actor):
        if actor == self.actor1:
            self.yattane.play()
        elif actor == self.actor2:
            self.uu.play()
        else:
            pass

        end = False
        for actor in [self.actor1, self.actor2]:
            if actor.game_player.stock == 0:
                end = True
                break
        
        dummy = Group()
        if end:
            self.timer_group.add_timer_sprite(dummy, timer=90, on_delete_fnc=self._start_battle_end_animation)
        else:
            self.timer_group.add_timer_sprite(dummy, timer=90, on_delete_fnc=self._reset)
    
    def _start_battle_end_animation(self):
        """Resultに移る前のアニメーション
        """
        self.sokomade.play()
        text_sprite = TextSprite(*self.view_area.center, align="center", vertical_align="middle", text="sokomade", font=self.font, color=(0, 0, 0), bgcolor=(255, 255, 255))
        self.timer_group.add_timer_sprite(text_sprite, timer=90, on_delete_fnc=self._go_to_result)
        
    def _set_hand(self, actor, hand):
        """actorのHandを更新する

        Args:
            actor (Actor): Actor
            hand (Hand): Hand
        """
        actor.set_hand(hand)
        self._update_actor_state_sprites()
    
    def _update_actor_state_sprites(self):
        """Actorの状態に応じて画像を変化させる
        """
        self.actor_state_group.empty()
        for actor in [self.actor1, self.actor2]:
            self.actor_state_group.add(self.actor_state_sprites[actor][actor.done()])

    def _go_to_result(self):
        """結果画面に進む
        """
        self.run = False
        self.next_screen = Screen.RESULT
    
    def _reset(self):
        """入力待ちに戻す
        """
        self.actor1.reset()
        self.actor2.reset()
        
        for key_hander in self.key_handers:
            key_hander.resume()
        
        for checker in self.checkers:
            checker.resume()

        self._update_actor_state_sprites()


def get_sample_game_player(game_config, name: str="sample", stock: int=0):
    """GamePlayerのサンプルを得る

    Args:
        game_config (GameConfig): ゲームの設定オブジェクト
        name (str, optional): GamePlayerの名前. Defaults to "sample".
        stock (int, optional): GamePlayerのストック数.これはGameScreen内でgame_settingのストック数で上書きされる. Defaults to 0.

    Returns:
        GamePlayer: ゲームプレイヤーオブジェクト
    """
    import random

    from player import Player


    player = Player(_id=random.randint(0, 10000), name=name, matches_num=1, win_num=1)

    game_config = GameConfig("./jsons/config.json")

    class GamePlayer:
        def __init__(self):
            self.player = None
            self.character = None
            self.stock = 0
        
        def __repr__(self):
            return self.player.name

    game_player = GamePlayer()
    game_player.character = game_config.characters["0"]
    game_player.player = player
    game_player.stock = stock

    return game_player

def get_sample_game_setting(game_config, stock: int=3):
    """GameSetting(ステージ，ストック数)のサンプルを得る

    Args:
        game_config (GameConfig): ゲームの設定オブジェクト
        stock (int, optional): ストック数. Defaults to 3.

    Returns:
        GameSetting: ステージ，ストック数をもつオブジェクト
    """
    import random

    class GameSetting:
        def __init__(self):
            self.stage = None
            self.stock = 0
        
    game_setting = GameSetting()
    game_setting.stage = random.choice(list(game_config.stages.values()))
    game_setting.stock = stock

    return game_setting


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((500, 500))

    from game_config import GameConfig
    game_config = GameConfig("./jsons/config.json")

    game_setting = get_sample_game_setting(game_config, stock=3)
    game_player1 = get_sample_game_player(game_config, name="sample1", stock=0)
    game_player2 = get_sample_game_player(game_config, name="sample2", stock=0)
    gs = GameScreen(game_player1, game_player2, game_setting)
    gs.main()