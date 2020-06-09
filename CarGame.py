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
from tools.RacingTrack import RacingTrack

class CarGame(threading.Thread):

    def __init__(self, screen):
        threading.Thread.__init__(self)
        self.__flag = threading.Event()

        # 手动放置小车标志位
        self.placeCar = False

        # 测距线显示开关
        self.distanceLinesShow = True

        # 游戏轨迹记录
        self.Recording = False

        self.screen = screen
        self.carMap = CarMap(screen)
        self.car = None

        self.start()
        self.__flag.set()

    def run(self):
        self.carMap.initMap()
        self.record = RacingTrack(self.carMap.mapName())

        if self.record.hasRecord:
            carInfo = self.record.randomGetItem()[0]
            self.car = CarBase(self.screen, [carInfo[0], carInfo[1]], carInfo[2])

        while True:
            self.__flag.wait()
            self.carMap.clear()
            if self.car is not None:
                if self.car.isDone():
                    self.car.reStart()

                if self.Recording:
                    self.record.append(self.car.carInfo.intPos, self.car.carInfo.angle, self.car.carInfo.speed)

                self.car.Update()

                time.sleep(0.02)


    def manageEvent(self, event):
        # 按键按下信息
        if event.type == pygame.KEYDOWN:
            # 地图操作
            if event.key in (pygame.K_b, pygame.K_n):
                self.carMap.manageEvent(event)

                self.record = RacingTrack(self.carMap.mapName())
                self.car = None

                # 如果该地图有记录，则自动放置小车
                if self.record.hasRecord:
                    carInfo = self.record.randomGetItem()[0]
                    self.car = CarBase(self.screen, [carInfo[0], carInfo[1]], carInfo[2])

            # 小车方向操作
            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT):
                if self.car is not None:
                    self.car.manageEvent(event)

            # 轨迹记录操作
            elif event.key == pygame.K_r:
                if self.car is not None:
                    if self.Recording == False:
                        print("记录模式打开")
                        self.Recording = True
                        self.record.clear()
                    else:
                        print("记录模式关闭")
                        self.Recording = False
            # 记录写入文件中
            elif event.key == pygame.K_s:
                if self.car is not None:
                    self.record.write()

            # 清除当前小车
            elif event.key == pygame.K_c:
                self.car = None
                self.placeCar = True

            # 是否显示测距信息
            elif event.key == pygame.K_l:
                if self.car is not None:
                    self.car.setDistanceShowChange()

        # 按键松开信息
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT):
                if self.car is not None:
                    self.car.manageEvent(event)

        # 手动放置小车
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.car is None and\
                    (list(self.screen.get_at(event.pos))[0:3] == RACECOLOR):
                self.car = CarBase(self.screen, event.pos, angle=0)
                self.placeCar = False

    # 暂停线程
    def pause(self):
        self.__flag.clear()

    # 开始线程
    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞


