# -*- coding: utf-8 -*-
# @Time    : 2020/6/8 22:17
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : CarGame.py

import pygame
import time
import threading
from config.MapConfig import *
from map.CarMap import CarMap
from car.CarBase import CarBase

class CarGame(threading.Thread):

    def __init__(self, screen):
        threading.Thread.__init__(self)
        self.screen = screen
        self.carMap = CarMap(screen)
        self.car = None

        self.start()

    def initGame(self):
        self.carMap.initMap()

    def run(self):
        while True:
            if self.car is not None:
                self.carMap.clear()
                self.car.Update()

                if self.car.isDone():
                    self.car.reStart()

                time.sleep(0.02)

    def manageEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_b, pygame.K_n):
                self.carMap.manageEvent(event)
                self.car = None

            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT):
                if self.car is not None:
                    self.car.manageEvent(event)

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT):
                if self.car is not None:
                    self.car.manageEvent(event)

        elif event.type == pygame.MOUSEBUTTONUP:

            # print(self.parent.screen.get_at(event.pos), RACECOLOR,self.parent.screen.get_at(event.pos) == RACECOLOR)
            if self.car is None and \
                    (list(self.screen.get_at(event.pos))[0:3] == RACECOLOR):
                self.car = CarBase(self.screen, event.pos)


