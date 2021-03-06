# -*- coding: utf-8 -*-
# @Time    : 2020/6/8 22:47
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : CarBaseV1.py

import math
import pygame
import os
import numpy as np
import torch
from config.MapConfig import *

class CarInfo(object):

    def __init__(self, screen, pos, angle=0, speed = 0, AImode=False):
        self.startPos = [pos[0], pos[1]]
        self.startAngle = angle
        self.startSpeed = speed
        self.AImode = AImode
        self.screen = screen
        self.init()

    def init(self):
        # 位置信息
        self.floatPos = self.startPos.copy()  # 浮点型位置，记录真实位置（因为计算有小数位）
        self.intPos = self.startPos.copy()    # 整型数据，记录像素点位置（显示位置）

        # 运动信息
        self.speed = self.startSpeed  # 速度
        self.accSpeed = 0  # 加速度
        self.angle = self.startAngle  # 角度
        self.accAngle = 0  # 角速度
        self.movePos = [0, 0]  # 下一次更新需要移动的相对位置

        # 状态信息
        self.linearDistance = 0  # 直线距离
        self.leftDistance = 0  # 左边距离
        self.rightDistance = 0  # 右边距离
        self.leftAngleDistance = 0  # 左边斜向上距离
        self.rightAngleDistance = 0  # 右边斜向上距离
        self.centerDistance = 0      # 距离轨道中心距离（只有AI模式可见）

        # 游戏结束信息
        self.isDone = False

    # 移动信息更新
    def moveinfoUpdate(self):
        self.speed += self.accSpeed
        self.angle += self.accAngle

        if self.speed < 0:
            self.speed = 0
        elif self.speed >= MAXSPEED:
            self.speed = MAXSPEED

        if self.angle >= 360 or self.angle <= -360:
            self.angle = 0

        moveDistance = self.speed

        # 更新浮点型位置（真实位置）
        self.floatPos[0] += moveDistance * math.sin(2 * math.pi * (self.angle / 360))
        self.floatPos[1] += -moveDistance * math.cos(2 * math.pi * (self.angle / 360))

        # 更新下次需要移动的相对距离（整型）
        try:
            self.movePos[0] = int(self.floatPos[0] - self.intPos[0])
            self.movePos[1] = int(self.floatPos[1] - self.intPos[1])
        except:
            print(self.angle, moveDistance)

        # 更新当前在图片上的像素位置
        self.intPos[0] += self.movePos[0]
        self.intPos[1] += self.movePos[1]

    # 状态信息更新
    def statuesInfoUpdate(self, distanceLinesShow):
        if self.intPos[0] < 0 or self.intPos[1] < 0 or self.intPos[1] > MAPSIZE[1] \
                or self.intPos[0] > MAPSIZE[0]:
            self.isDone = True
            return

        posPix = list(self.screen.get_at(self.intPos))[0:3]

        if posPix == BACKGROUNDCOLOR:
            self.isDone = True
            return


        linearDistancePos, self.linearDistance = self.calcEdgeDistance(self.intPos, Angle=self.angle)
        leftDistancePos, self.leftDistance = self.calcEdgeDistance(self.intPos, Angle=self.angle - 90)
        rightDistancePos, self.rightDistance = self.calcEdgeDistance(self.intPos, Angle=self.angle + 90)
        leftAngleDistancePos, self.leftAngleDistance = self.calcEdgeDistance(self.intPos, Angle=self.angle - RGITHLINEANGLE)
        rightAngleDistancePos, self.rightAngleDistance = self.calcEdgeDistance(self.intPos, Angle=self.angle + RGITHLINEANGLE)

        if self.AImode:
            centerPos, self.centerDistance = self.calcCenterDistance(self.intPos)

        if distanceLinesShow:
            pygame.draw.line(self.screen, [100, 100, 0], linearDistancePos, self.intPos)
            pygame.draw.line(self.screen, [0, 100, 100], leftDistancePos, self.intPos)
            pygame.draw.line(self.screen, [0, 100, 100], rightDistancePos, self.intPos)
            pygame.draw.line(self.screen, [100, 0, 100], leftAngleDistancePos, self.intPos)
            pygame.draw.line(self.screen, [100, 0, 100], rightAngleDistancePos, self.intPos)

            if self.AImode:
                pygame.draw.line(self.screen, [0, 255, 255], centerPos, self.intPos)

    def calcCenterDistance(self, carPos):
        posPix = list(self.screen.get_at(carPos))[0:3]

        theta = np.linspace(0, 2 * np.pi, 360)
        x = np.cos(theta)
        y = np.sin(theta)

        for distance in range(30):
            for temp_x, temp_y in zip(x,y):
                tempPos = [int(carPos[0] + distance * temp_x), int(carPos[1] + distance * temp_y)]
                tempPix = list(self.screen.get_at(tempPos))[0:3]

                # 找到了中点，返回
                if tempPix == CENTERCOLOR:
                    return tempPos, distance

        # 没有找到则返回30
        return carPos, 30

    def calcEdgeDistance(self, carPos, Angle):
        """
        计算小车距离对应方向边界的距离
        :param carPos: 小车当前位置
        :param Angle:  小车方向
        :return: 边界点，距离值
        """
        posPix = list(self.screen.get_at(carPos))[0:3]
        tempPix = posPix.copy()
        tempPos = carPos.copy()
        distance = 0
        while tempPix != BACKGROUNDCOLOR:

            tempPos[0] = carPos[0] + distance * math.sin(2 * math.pi * (Angle / 360))
            tempPos[1] = carPos[1] - distance * math.cos(2 * math.pi * (Angle / 360))

            tempPix = list(self.screen.get_at([int(tempPos[0]), int(tempPos[1])]))[0:3]
            distance += 1

            if tempPos[0] > MAPSIZE[0] or tempPos[0] < 0:
                break

            if tempPos[1] > MAPSIZE[1] or tempPos[1] < 0:
                break

        return tempPos, distance

    def update(self, distanceLinesShow):
        """
        更新小车位置，更新小车距离边界的状态
        :param distanceLinesShow: 是否在界面上显示位置
        :return:
        """
        self.moveinfoUpdate()
        self.statuesInfoUpdate(distanceLinesShow)


# 按键状态
class KeyState(object):
    def __init__(self):
        self.up = False
        self.down = False
        self.right = False
        self.left = False

class CarBase(object):

    # 初始化画板、小车位置、小车图标
    def __init__(self, screen, pos=[20.0, 20.0], angle=0, speed = 0,logoIndex=0, distanceLinesShow=False, AImode = False):
        self.initPos = [pos[0], pos[1]]
        self.initAngle = angle
        self.initSpeed = speed
        self.pos = [pos[0], pos[1]]
        self.logoIndex = logoIndex
        self.screen = screen
        self.AImode = AImode
        self.distanceLinesShow = distanceLinesShow

        # 小车信息
        self.carInfo = CarInfo(self.screen, [pos[0], pos[1]], self.initAngle, self.initSpeed, self.AImode)

        # 初始化小车图片，以及状态
        self.logeFileList = os.listdir("config/png/")
        self.logo = self.logeFileList[self.logoIndex]

        self.carLogo = pygame.image.load("config/png/" + self.logo).convert_alpha()

        self.initCar()

    # 初始化小车信息
    def initCar(self):

        width, high = self.carLogo.get_width(), self.carLogo.get_height()
        self.carRect = self.carLogo.get_rect()
        self.carRect = self.carRect.move((self.initPos[0] - int(width / 2), self.initPos[1] - int(high / 2)))

        self.paintCarLoge = self.carLogo.copy()
        self.paintCarRect = self.carRect.copy()

        self.carlogoRotate(self.initAngle)

        # 状态信息初始化
        self.carInfo.init()
        self.carInfo.update(self.distanceLinesShow)
        self.key = KeyState()

    def setDistanceShowChange(self):

        if self.distanceLinesShow == False:
            self.distanceLinesShow = True
        else:
            self.distanceLinesShow = False

    # 更新界面
    def Update(self):
        if self.key.up:
            self.carInfo.accSpeed = MAXSPEEDACC

        if self.key.down:
            self.carInfo.accSpeed = -MAXSPEEDACC

        if self.key.left:
            self.carInfo.accAngle = -MAXANGLESPEED

        if self.key.right:
            self.carInfo.accAngle = MAXANGLESPEED

        if self.key.right == False and self.key.left == False:
            self.carInfo.accAngle = 0

        if self.key.up == False and self.key.down == False:
            self.carInfo.accSpeed = 0

        self.carInfo.update(self.distanceLinesShow)

        self.carRect.move_ip(self.carInfo.movePos)
        self.carlogoRotate(self.carInfo.angle)

        self.screen.blit(self.paintCarLoge, self.paintCarRect)

    # 小车旋转
    def carlogoRotate(self, angle):
        self.paintCarLoge = pygame.transform.rotate(self.carLogo, -angle)
        self.paintCarRect = self.paintCarLoge.get_rect(center=self.carRect.center)

    # 是否结束游戏
    def isDone(self):
        return self.carInfo.isDone

    # 重新开始游戏
    def reStart(self):
        self.initCar()

    # 事件管理
    def manageEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.key.up = True
                self.key.down = False

            elif event.key == pygame.K_DOWN:
                self.key.down = True
                self.key.up = False

            elif event.key == pygame.K_RIGHT:
                self.key.right = True
                self.key.left = False

            elif event.key == pygame.K_LEFT:
                self.key.left = True
                self.key.right = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.key.up = False

            elif event.key == pygame.K_DOWN:
                self.key.down = False

            elif event.key == pygame.K_RIGHT:
                self.key.right = False

            elif event.key == pygame.K_LEFT:
                self.key.left = False
