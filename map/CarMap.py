# -*- coding: utf-8 -*-
# @Time    : 2020/6/6 22:45
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : CarMap.py

import pygame
import os
import cv2
import numpy as np
from config.MapConfig import *

class CarMap():
    MapSize = [int(MAPSIZE[0]), MAPSIZE[1]]
    Color = BACKGROUNDCOLOR

    def __init__(self, screen, mapIndex = 0):
        self.screen = screen

        self.mapIndex = mapIndex
        self.mapList = os.listdir("config/map")

    # 初始化地图
    def initMap(self):
        initMap = np.zeros((self.MapSize[0], self.MapSize[1], 3), dtype="uint8")
        initMap[:, :] = BACKGROUNDCOLOR

        imageMap = cv2.imread("config/map/" + self.mapList[self.mapIndex])
        initMap[imageMap[:, :, 0] == 0, 0] = RACECOLOR[0]
        initMap[imageMap[:, :, 1] == 0, 1] = RACECOLOR[1]
        initMap[imageMap[:, :, 2] == 0, 2] = RACECOLOR[2]

        initMap[imageMap[:, :, 0] == 100, 0] = CENTERCOLOR[0]
        initMap[imageMap[:, :, 1] == 100, 1] = CENTERCOLOR[1]
        initMap[imageMap[:, :, 2] == 100, 2] = CENTERCOLOR[2]

        pygame.surfarray.blit_array(self.screen, initMap)
        self.mScreen = self.screen.copy()

    def mapName(self):
        return self.mapList[self.mapIndex]

    # 重新刷新地图， 比initMap速度要快
    def clear(self):
        self.screen.blit(self.mScreen, dest=(0, 0))

    def manageEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                self.mapIndex += 1
                if self.mapIndex >= len(self.mapList):
                    self.mapIndex = 0
                self.initMap()

            elif event.key == pygame.K_b:
                self.mapIndex -= 1
                if self.mapIndex < 0:
                    self.mapIndex = len(self.mapList) - 1
                self.initMap()
