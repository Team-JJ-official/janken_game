from __future__ import annotations
from typing import Union

import pygame

class Group(pygame.sprite.AbstractGroup):

    def __init__(self):
        super().__init__()
        self.groupdict = {}
        self.lostgroups = []
    
    def sprites(self):
        return list(self.spritedict)
    
    def groups(self):
        return list(self.groupdict)

    def add_internal(self, obj: Union[pygame.sprite.Sprite, Group]):
        """
        内部に[Sprite, Group]を追加する

        [Sprite, Group]のみを追加し，それ以外は無視
        """
        if isinstance(obj, Group):
            self.groupdict[obj] = 0
        elif isinstance(obj, pygame.sprite.Sprite):
            self.spritedict[obj] = 0

    def remove_internal(self, obj: Union[pygame.sprite.Sprite, Group]):
        """
        指定した[Sprite, Group]を削除する

        [Sprite, Group]以外は無視
        """
        if isinstance(obj, Group):
            lost_rect = self.groupdict[obj]
            if lost_rect:
                self.lostgroups.append(lost_rect)
            del self.groupdict[obj]
        elif isinstance(obj, pygame.sprite.Sprite):
            lost_rect = self.spritedict[obj]
            if lost_rect:
                self.lostsprites.append(lost_rect)
            del self.spritedict[obj]
            
    def has_internal(self, obj: Union[pygame.sprite.Sprite, Group]):
        """
        引数と同じ要素を持っているか返す
        
        [Sprite, Group]以外はFalse
        """
        if isinstance(obj, Group):
            return obj in self.groupdict
        if isinstance(obj, pygame.sprite.Sprite):
            return obj in self.spritedict
        return False

    def copy(self):
        """copy a group with all the same sprites

        Group.copy(): return Group

        Returns a copy of the group that is an instance of the same class
        and has the same sprites in it.

        よくわからん
        """
        return self.__class__(self.sprites()) # noqa pylint: disable=too-many-function-args; needed because copy() won't work on AbstractGroup

    def __iter__(self):
        """
        groupが持っているspriteのみのイテレータを返す

        groupsも参照できるようにしたい
        """
        return iter(self.sprites())

    def add(self, *objects, multi = False):
        """
        Groupに要素を追加する

        iterableなデータ構造も追加可能

        デフォルトでは追加する要素がメンバGroup内に存在する場合は追加しない
        """
        for obj in objects:
            if not self.has(obj) or multi:
                # [Sprite, Group]のみ追加
                if isinstance(obj, pygame.sprite.Sprite):
                    self.add_internal(obj)
                    obj.add_internal(self)
                elif isinstance(obj, Group):
                    self.add_internal(obj)
                else:
                    try:
                        # iterableなデータが渡された場合
                        self.add(*obj)
                    except:
                        # itarableではない場合
                        pass

    def remove(self, *objects):
        """
        Groupから要素を削除する

        iterableなデータ構造を渡す場合，含まれる要素全てを削除
        """
        for obj in objects:
            if self.has_internal(obj):
                if isinstance(obj, pygame.sprite.Sprite):
                    self.remove_internal(obj)
                    obj.remove_internal(self)
                elif isinstance(obj, Group):
                    self.remove_internal(obj)
            else:
                try:
                    self.remove(*obj)
                except:
                    pass

    def has(self, *objects):
        """
        要素がGroup内に存在しているかどうか求める

        渡す要素を全て含む場合のみTrue
        """
        if not objects:
            return False  # return False if no sprites passed in
        
        for obj in objects:
            if isinstance(obj, pygame.sprite.Sprite) or isinstance(obj, Group):
                if not self.has_internal(obj):
                    exist = False
                    for grp in self.groups():
                        if grp.has(obj):
                            exist = True
                            break
                    if not exist:
                        return False
            else:
                try:
                    if not self.has(*obj):
                        return False
                except:
                    return False
        return True


    def update(self, *args, **kwargs):
        """
        メンバ[Sprite, Group]のupdateを呼び出す

        (Spriteのupdateを先に実行)
        """
        for sprite in self.sprites():
            sprite.update(*args, **kwargs)
        for group in self.groups():
            group.update(*args, **kwargs)

    def draw(self, surface):
        super().draw(surface)
        for group in self.groups():
            group.draw(surface)
        self.lostgroups = []

    def clear(self, surface, bgd):
        """erase the previous position of all sprites

        Group.clear(surface, bgd): return None

        Clears the area under every drawn sprite in the group. The bgd
        argument should be Surface which is the same dimensions as the
        screen surface. The bgd could also be a function which accepts
        the given surface and the area to be cleared as arguments.

        これよくわからん

        """
        if callable(bgd):
            for lost_clear_rect in self.lostsprites:
                bgd(surface, lost_clear_rect)
            for clear_rect in self.spritedict.values():
                if clear_rect:
                    bgd(surface, clear_rect)
        else:
            surface_blit = surface.blit
            for lost_clear_rect in self.lostsprites:
                surface_blit(bgd, lost_clear_rect, lost_clear_rect)
            for clear_rect in self.spritedict.values():
                if clear_rect:
                    surface_blit(bgd, clear_rect, clear_rect)

    def empty(self):
        """remove all sprites, groups

        Group.empty(): return None

        Removes all the sprites, groups from the group.

        """
        self.remove(self.sprites())
        self.remove(self.groups())

    def __nonzero__(self):
        return truth(self.sprites())

    __bool__ = __nonzero__

    def __len__(self):
        return len(self.sprites()) + len(self.groups())

    def __repr__(self):
        return "<%s(%d sprites, %d groups)>" % (self.__class__.__name__, len(self.sprites()), len(self.groups()))

class GroupSingle(Group):
    def __init__(self, obj = None):
        super().__init__()
        self.add(obj)
    
    @property
    def sprite(self):
        return next(iter(self.spritedict))
    
    @property
    def group(self):
        return next(iter(self.groupdict))

    def add(self, obj):
        """
        Groupに要素を追加する

        共存できる要素は1つのみ
        """
        # [Sprite, Group]のみ追加
        if not self.has_internal(obj):
            if isinstance(obj, pygame.sprite.Sprite):
                self.empty()
                self.add_internal(obj)
                obj.add_internal(self)
            elif isinstance(obj, Group):
                self.empty()
                self.add_internal(obj)

if __name__ == '__main__':
    rootgroup = Group()
    group1 = Group()
    groupx = Group()
    group2 = GroupSingle()
    groups = [Group() for _ in range(5)]
    print(rootgroup)
    rootgroup.add(group1)
    rootgroup.add(groupx)
    print(rootgroup)
    rootgroup.add(group2)
    print(rootgroup)
    rootgroup.add(groups)
    print(rootgroup)
    rootgroup.empty()
    print(rootgroup)

    
    