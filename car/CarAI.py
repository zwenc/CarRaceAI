# -*- coding: utf-8 -*-
# @Time    : 2020/6/9 21:25
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : CarAI.py

"""
该小车类只能由AI控制，但是由于只是重载了Updata，并没有重写，后期调试成功后，可以将该代码和Carbase代码合成一个。
"""

import pygame
from car.CarBase import *

class CarAI(CarBase):

    def __init__(self, screen, pos=[20.0, 20.0], angle=0, logoIndex=1, distanceLinesShow=False):
        super(CarAI, self).__init__(screen, pos, angle, logoIndex, distanceLinesShow)

    # 更新界面， 由AI直接控制，AI控制加速和角度两个参数
    def Update(self, accSpeed, accAngle):
        accSpeed = 0.1 if accSpeed >= 0.1 else accSpeed
        accSpeed = -0.1 if accSpeed <= -0.1 else accSpeed

        accAngle = 5 if accAngle >= 5 else accAngle
        accAngle = -5 if accAngle <= -5 else accAngle

        self.carInfo.accSpeed = accSpeed
        self.carInfo.accAngle = accAngle

        self.carInfo.update(self.distanceLinesShow)

        self.carRect.move_ip(self.carInfo.movePos)
        self.carlogoRotate(self.carInfo.angle)

        self.screen.blit(self.paintCarLoge, self.paintCarRect)