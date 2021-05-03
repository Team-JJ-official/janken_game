from enum import Enum

import pygame

from screen import Screen, BaseScreen
from sprites import RichSprite, SimpleSprite
from component import PlayerStockIcon, KeyHandler, Checker
from transform import surface_fit_to_rect
from game_config import GameConfig

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

        self.init()
    
    def init(self):
        """初期化処理を行う
        """
        self._set_bg()
        self._init_game()
        self._set_player_icons()
        # self._set_random_btn()
        self._set_key_handler()
        self._set_checker()
    
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
        rect = self.display.get_rect()
        self.players_rect = pygame.rect.Rect(0, rect.h * 3 // 4, rect.w, rect.h // 4)
        game_players = [self.actor1.game_player, self.actor2.game_player]
        for i, game_player in enumerate(game_players):
            player_icon_sprite = PlayerStockIcon(
                left=self.players_rect.left + self.players_rect.w // len(game_players) * i,
                top=self.players_rect.top,
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
                keys[0]: (actor.set_hand, self.Hand.ROCK),
                keys[1]: (actor.set_hand, self.Hand.SCISSORS),
                keys[2]: (actor.set_hand, self.Hand.PAPER),
            }
            key_hundler = KeyHandler(key_to_fnc_dic)
            self.middle_sprites.add(key_hundler)
            self.key_handers.append(key_hundler)
    
    def _set_checker(self):
        """チェッカーGroupの設置
        """
        self.checkers = []
        # プレイヤー1, 2が入力完了したかどうかを監視するもの
        key_done_checker = Checker([self.actor1.done, self.actor2.done], self._judge, stop_when_call_fnc=True)
        self.middle_sprites.add(key_done_checker)
        self.checkers.append(key_done_checker)
    
    def _judge(self):
        rest = 1
        if self.actor1.hand == self.actor2.hand:
            pass    # あいこ
        elif (self.actor1.hand == self.Hand.ROCK and self.actor2.hand == self.Hand.SCISSORS) or \
            (self.actor1.hand == self.Hand.PAPER and self.actor2.hand == self.Hand.ROCK) or \
            (self.actor1.hand == self.Hand.SCISSORS and self.actor2.hand == self.Hand.PAPER):
            rest = self.actor2.decrease_stock()
        else:
            rest = self.actor1.decrease_stock()
        
        if rest == 0:   # どちらかがストック0になったら終了
            self._go_to_result()
        
        self._reset()
    
    def _go_to_result(self):
        self.run = False
        self.next_screen = Screen.RESULT
    
    def _reset(self):
        self.actor1.reset()
        self.actor2.reset()
        
        for key_hander in self.key_handers:
            key_hander.resume()
        
        for checker in self.checkers:
            checker.resume()


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