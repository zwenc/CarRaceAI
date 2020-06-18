# -*- coding: utf-8 -*-
# @Time    : 2020/6/9 21:39
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : CarGameAI.py
"""
该代码用于强化学习采样数据学习专用代码，无法显示界面
"""

import pygame
import math
import cv2
from config.MapConfig import *
from car.CarAI import CarAI
from map.CarMap import CarMap
from tools.RacingTrack import RacingTrack

class CarGameAI(object):

    def __init__(self, mapIndex=0, initPosIndex=-1):
        """
        :param mapIndex:     地图编号
        :param initPosIndex: 初始位置选择，-1表示随机位置，如果是验证网络是否能够训练，建议使用初始位置0
        """
        # 入口参数保存
        self.mapIndex = mapIndex
        self.initPosIndex = initPosIndex

        # 参数记录
        self.tracking = []

        # 初始化环境
        self.init()

    def init(self):
        # 绘图界面初始化
        pygame.init()
        self.screen = pygame.display.set_mode(MAPSIZE)
        self.screen.fill(INITCOLOR)
        pygame.display.set_caption(WINDOWSNAME)

        # 初始化地图
        self.carMap = CarMap(self.screen, self.mapIndex)
        self.carMap.initMap()

        # 初始化记录
        self.tracking = []

        # 初始化小车
        self.record = RacingTrack(self.carMap.mapName())
        if self.record.hasRecord:

            # 提取初始坐标
            if self.initPosIndex == -1:
                carInfo = self.record.randomGetItem()[0]  # 随机选择 出生位置
            else:
                carInfo = self.record[self.initPosIndex]  # 指定出生位置

            self.car = CarAI(self.screen, [carInfo[0], carInfo[1]], carInfo[2], speed = 0,distanceLinesShow=True)

        else:
            exit("该地图无初始化点信息")

        # 小车状态
        self.mstate = [self.car.carInfo.linearDistance, self.car.carInfo.leftAngleDistance,
                self.car.carInfo.rightAngleDistance,
                self.car.carInfo.leftDistance, self.car.carInfo.rightDistance, self.car.carInfo.speed]

    def step(self, action):
        """
        :param accSpeed: 加速度
        :param accAngle: 角加速度
        :return: [直线距离，左斜距离，右斜距离，左距离，右距离，速度，角度]， 奖励, 是否结束游戏
        """
        speed = [action[0], action[1], action[2]]
        Angle = [action[3], action[4], action[5]]
        self.carMap.clear()  # 刷新地图
        # accSpeed = 0

        accItem = [-1, 0, 1]
        accAngle = accItem[Angle.index(max(Angle))]
        accSpeed = accItem[speed.index(max(speed))]

        self.car.Update(accSpeed * 0.1, accAngle * 5)  # 更新小车，并显示在地图上

        # 记录位置信息
        self.tracking.append([self.car.carInfo.intPos[0], self.car.carInfo.intPos[1]])

        # 生存奖励
        liveReward = -100 if self.car.carInfo.isDone == True else 2
        # liveReward = 0

        # 居中奖励
        # centerReward = 2.25 - self.car.carInfo.centerDistance * self.car.carInfo.centerDistance * 0.1
        centerReward = 0

        # 速度奖励
        # speedReward = self.car.carInfo.speed - 2
        speedReward = 0

        # 加速奖励
        accSpeedReward = 0
        if accSpeed == 1:
            accSpeedReward = 10

        # 总的奖励
        allReward = liveReward + centerReward + speedReward*10 + accSpeedReward

        return [self.car.carInfo.linearDistance, self.car.carInfo.leftAngleDistance,
                self.car.carInfo.rightAngleDistance,
                self.car.carInfo.leftDistance, self.car.carInfo.rightDistance, self.car.carInfo.speed], \
               allReward, self.car.carInfo.isDone

    def reset(self):
        self.car.reStart()
        self.tracking = []

        return [self.car.carInfo.linearDistance, self.car.carInfo.leftAngleDistance,
                self.car.carInfo.rightAngleDistance,
                self.car.carInfo.leftDistance, self.car.carInfo.rightDistance, self.car.carInfo.speed]

    def saveImage(self):
        filename = "AI/out/image/" + self.carMap.mapName()

        if len(self.tracking) >= 2:
            pygame.draw.lines(self.screen, [255, 0, 0], False, self.tracking, 1)

        image = pygame.surfarray.array3d(self.screen)
        cv2.imwrite(filename, image)


# 测试代码
if __name__ == "__main__":
    aaa = CarGameAI(0)

    while True:
        state, reward, isdone = aaa.step(2, 0)
        aaa.saveImage()

        print(state, reward, isdone)

        if isdone:
            break

