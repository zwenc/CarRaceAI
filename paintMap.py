# -*- coding: utf-8 -*-
# @Time    : 2020/6/6 23:18
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : InitMap.py
import pygame
import cv2
import time
from config.MapConfig import *

class Painter(object):
    painterMapSize = [int(MAPSIZE[0]), MAPSIZE[1]]
    painterColor = [255, 255, 255]

    def __init__(self, parent):
        # super(Painter, self).__init__(parent, mapSize=self.painterMapSize, initColor=self.painterColor)
        self.parent = parent
        self.initMap()

        # 是否绘制中轴线，默认绘制
        self.centralAxis = True
        self.race = []

        self.moveState = False

    def initMap(self):
        painterRact = pygame.Rect(0, 0, self.painterMapSize[0], self.painterMapSize[1])
        pygame.draw.rect(self.parent.screen, self.painterColor, painterRact, 0)
        self.race = []

    def paint(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.lineBuff = []
            self.moveState = True
            self.start_x, self.start_y = event.pos
            self.paintPos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            self.moveState = False
        elif event.type == pygame.MOUSEMOTION:
            if self.moveState:
                self.paintPos = event.pos
        else:
            print("无效指令")

        self.drawMap()

    def manageEvent(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            self.paint(event)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.saveRace()
            elif event.key == pygame.K_c:
                self.clear()
            elif event.key == pygame.K_g:
                self.generateRace()
            elif event.key == pygame.K_f:
                if self.centralAxis == False:
                    self.centralAxis = True
                else:
                    self.centralAxis = False


    def drawMap(self):
        if self.moveState:
            pygame.draw.circle(self.parent.screen, [0, 0, 0], (self.start_x, self.start_y), 25)
            self.start_x, self.start_y = self.paintPos
            if self.centralAxis:
                self.race.append([self.start_x, self.start_y])

    def clear(self):
        self.initMap()

    def generateRace(self):
        pygame.draw.lines(self.parent.screen, [100, 100, 100], True, self.race, 2)
        image = pygame.surfarray.array3d(self.parent.screen)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        opening = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        # self.parent.screen.get_view("0").write(opening.tostring())
        pygame.surfarray.blit_array(self.parent.screen, opening)

    def saveRace(self):
        timestruct = time.localtime(time.time())
        filename = "config/map/{year}-{mon}-{day}-{hour}-{min}-{sec}.png".format(
            year=timestruct.tm_year, mon=timestruct.tm_mon, day=timestruct.tm_mday,
            hour=timestruct.tm_hour, min=timestruct.tm_min, sec=timestruct.tm_sec
        )
        image = pygame.surfarray.array3d(self.parent.screen)

        cv2.imwrite(filename, image)
