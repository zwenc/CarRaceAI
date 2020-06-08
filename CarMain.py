# -*- coding: utf-8 -*-
# @Time    : 2020/6/6 22:45
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : CarRace.py

import pygame
from config.MapConfig import *
from paintMap import Painter
from map.CarMap import CarMap
from CarGame import CarGame

class mainwindow():
    def __init__(self):
        # super(mainwindow, self).__init__(self)
        self.mode = "normal"

        self.run()

    def initMap(self):
        pygame.init()
        self.screen = pygame.display.set_mode(MAPSIZE)
        self.screen.fill(INITCOLOR)
        pygame.display.set_caption(WINDOWSNAME)

        self.painter = Painter(self)
        self.carMap = CarMap(self)
        self.carGame = CarGame(self.screen)
        self.carGame.initGame()

        # self.carMap.initMap()

    def changeMode(self, mode):
        if self.mode != mode:
            if mode == "normal":
                self.carMap.initMap()
            elif mode == "painter":
                self.painter.initMap()
        self.mode = mode

    def run(self):
        self.initMap()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.mode != "normal":
                        print("normal mode")
                        self.changeMode("normal")
                        continue
                    elif event.key == pygame.K_p and self.mode != "painter":
                        print("painter mode")
                        self.changeMode("painter")
                        continue

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit("用户主动结束程序")

                if self.mode == "normal":
                    self.carGame.manageEvent(event)
                else:
                    self.painter.manageEvent(event)

            pygame.display.update()


mainwindow()

