#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime  # , date, time, timedelta
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
from numpy import sqrt, radians, sin, cos, pi, vstack, array
import csv


class Star:
    def __init__(self, object_name, m, color=(1, 1, 0, 1)):
        self.name = object_name
        self.M = m  # масса
        self.x = 0
        self.y = 0
        self.z = 0
        pos = gl.GLScatterPlotItem(pos=array([0, 0, 0]), color=color, size=10)
        pos.setGLOptions('translucent')
        plot_wid.addItem(pos)


class Object(object):
    def __init__(self, object_name, m, a, e, i, w, O, M, JD=2451545.0, color=(.5, .5, .5, 1)):
        """
        :param str object_name: название
        :param tuple color: цвет точки
        :param JD: юлианская дата 2451545.0
        :param m: масса
        :param a: большая полуось КМ
        :param e: ексцентриситет ε e=c/a
        :param i: отклонение°
        :param w: аргумент перицентра° ω
        :param O: долгота восходящего узла° Ω N
        :param M: средняя аномалия° M=E-e*sin(E)
        ∂ φ
        """
        self.name = object_name
        self.color = color
        self.m = m
        self.pos = None
        self.orb = None
        self.way = None
        k = G * (SUN.M + m)  # µ гравитационный параметр
        n = sqrt(k / a ** 3)  # среднее движение
        self.T = 2 * pi / n  # период обращения sqrt(((4 * pi**2)/(G * (SUN.M + m))) * a**3) Кеплер 3
        x, y, z = [], [], []
        E = radians(M)
        for count in range(int(999 / 365 * (datetime.now() - get_g_d(JD)).days)):
            while abs((M + e * sin(E)) - E) > 0.00001:  # последовательные приближения для эксцентрической аномалии
                E = M + e * sin(E)
            M += n * 1  # M = n(t−t0)+M0
            r = a * (1 - e * cos(E))  # радиус-вектор
            sin_v = (sqrt(1 - e ** 2) * sin(E)) / (1 - e * cos(E))
            cos_v = (cos(E) - e) / (1 - e * cos(E))
            sin_u = sin(radians(w)) * cos_v + cos(radians(w)) * sin_v
            cos_u = cos(radians(w)) * cos_v - sin(radians(w)) * sin_v
            x.append(r * (cos_u * cos(radians(O)) - sin_u * sin(radians(O)) * cos(radians(i))))
            y.append(r * (cos_u * sin(radians(O)) + sin_u * cos(radians(O)) * cos(radians(i))))
            z.append(r * (sin_u * sin(radians(i))))
            # V1 = sqrt(r / p) * e * sinv
            # V2 = sqrt(r / p) * (1 + e * cosv)
        self.X = x
        self.Y = y
        self.Z = z
        # F = G * SUN.M * self.m / r ** 2  # сила гравитационного притяжения
        # p = a * (1 - e ** 2)  # фокальный параметр
        # b = sqrt(a * p)  # малая полуось
        # Rper = (1 - e) * a  # радиус перегелия
        # Rafe = (1 + e) * a  # радиус афелия
        # φ = (24 * pi**3 * a**2) / (T**2 * C**2 * (1 - e**2))
        # φ = (6 * pi * G * SUN.M) / (C**2 * a * (1 - e**2))

    def star(self):
        pass

    def planet(self, orbit=True):
        return self.paint(orbit=orbit, size=1)

    def satellite(self, major):
        pass

    def asteroid(self, orbit=True):
        return self.paint(orbit=orbit, size=.5)

    def paint(self, orbit=True, size=1.0):
        self.pos = gl.GLScatterPlotItem(pos=array([self.X[-1], self.Y[-1], self.Z[-1]]), size=s_s(self.m),
                                        color=self.color)
        self.pos.setGLOptions('translucent')
        plot_wid.addItem(self.pos)
        pts_way = vstack([(self.X[-1], self.X[-1]), (self.Y[-1], self.Y[-1]), (self.Z[-1], 0)]).transpose()
        self.way = gl.GLLinePlotItem(pos=pts_way, width=0.1, color=(0, 0, 0, .5), antialias=True)
        plot_wid.addItem(self.way)
        pts_orb = vstack([self.X, self.Y, self.Z]).transpose()
        self.orb = gl.GLLinePlotItem(pos=pts_orb, width=size, color=(0, 0, 0, 1), antialias=True)
        plot_wid.addItem(self.orb) if orbit else None
        return self.pos, self.orb, self.way


def get_g_d(j_d):
    a = int(j_d + 32044)
    b = int((4 * a + 3) / 146097)
    c = a - int((146097 * b) / 4)
    d = int((4 * c + 3) / 1461)
    e = c - int((1461 * d) / 4)
    m = int((5 * e + 2) / 153)
    day = e - int((153 * m + 2) / 5) + 1
    month = m + 3 - 12 * int((m / 10))
    year = 100 * b + d - 4800 + int((m / 10))
    return datetime(year, month, day)


def get_j_d(day, month, year):
    a = int((14 - month) / 12)
    b = year + 4800 - a
    c = month + 12 * a - 3
    return day + int((153 * c + 2) / 5) + 365 * b + int(b / 4) - int(b / 100) + int(b / 400) - 32045


def s_s(m):
    if m > 1e25:
        return 10
    elif m > 1e23:
        return 6
    elif m > 1e20:
        return 4
    elif m > 1e18:
        return 2
    else:
        return 2


G = 6.67408e-11  # граивтационная постоянная м3·с−2·кг−1 или Н·м2·кг−2
au = 149597870  # а.е. астрономическая единица
C = 299792458  # скорость света м/с

# настройки окна
app = QtGui.QApplication([])

plot_wid = gl.GLViewWidget()
plot_wid.setWindowTitle('Planet System beta')
plot_wid.setGeometry(200, 50, 1024, 768)
plot_wid.setBackgroundColor('w')
plot_wid.opts['distance'] = 50000000000
plot_wid.orbit(-90, 0)
plot_wid.show()

# ось эклиптики (сетка)
g = gl.GLGridItem(color=[0, 0, 1, .1])
g.setSize(x=50000000000, y=50000000000)
g.setSpacing(x=700000000, y=700000000)
plot_wid.addItem(g)

# точка овна
pts_ARIES = vstack([(0, 3e10), (0, 0), (0, 0)]).transpose()
ARIES_p = gl.GLLinePlotItem(pos=pts_ARIES, width=0.1, color=(1, 0, 0, 1), antialias=True)
plot_wid.addItem(ARIES_p)
# ARIES_t = ax.text(2e10, 0, 0, 'Aries', color='r', alpha=0.5)

SUN = Star('Sun', m=1.98892e30)  # J2000.0 JD2451545.0

MERCURY = Object('Mercury', color=(.5, .5, .5, 1), m=3.33022e23, a=57909227, e=0.20563593, i=7.00487, w=29.124279,
                 O=48.33167, M=174.795884)
VENUS = Object('Venus', color=(0.3, 0, 0, 1), m=4.8675e24, a=108209475, e=0.00677323, i=3.39471, w=54.85229,
               O=76.67069, M=50.115)
EARTH = Object('Earth', color=(0, 0, 1, 1), m=5.9726e24, a=149598262, e=0.01671022, i=0.00005, w=114.20783,
               O=348.73936, M=358.617)
MARS = Object('Mars', color=(1, 0, 0, 1), m=6.4185e23, a=227943824, e=0.09341233, i=1.85061, w=286.46230,
              O=49.57854, M=19.373)
JUPITER = Object('Jupiter', color=(.5, .5, 0, 1), m=1.8986e27, a=778340821, e=0.04839266, i=1.30530, w=275.066,
                 O=100.55615, M=20.020)
SATURN = Object('Saturn', color=(1, 1, 0, 1), m=5.6846e26, a=1433449370, e=0.055723219, i=2.485240, w=336.013862,
                O=113.71504, M=317.020)
URANUS = Object('Uranus', color=(0, 0.5, 0, 1), m=8.6832e25, a=2870658186, e=0.04716771, i=0.76986, w=96.541318,
                O=74.22988, M=142.238600)
NEPTUNE = Object('Neptune', color=(0, 0, .5, 1), m=1.0243e26, a=4498396441, e=0.00858587, i=1.76917, w=265.646853,
                 O=131.72169, M=256.228)

CARES = Object('Ceres', color=(.5, .5, .5, 1), m=9.393e20, a=413767000, e=0.07934, i=10.585, w=2.825, O=80.399,
               M=27.448, JD=2455000.5)
PLUTO = Object('Pluto', color=(0.3, 0, 0, 1), m=1.303e22, a=5906440628, e=0.24880766, i=17.14175, w=113.76329,
               O=110.30347, M=14.53, JD=2451545.0)
HAUMEA = Object('Haumea', color=(.5, .5, .5, 1), m=4.006e21, a=42.98492 * au, e=0.1975233, i=28.201975,
                w=240.582838, O=121.900456, M=205.22317, JD=2456000.5)
MAKEMAKE = Object('Makemake', color=(0.3, 0, 0, 1), m=3e21, a=45.436301 * au, e=0.16254481, i=29.011819,
                  w=296.534594, O=79.305348, M=153.854714, JD=2456000.5)
ERIS = Object('Eris', color=(.5, .5, .5, 1), m=1.66e22, a=67.781 * au, e=0.44068, i=44.0445, w=150.977, O=35.9531,
              M=204.16, JD=2457000.5)
SEDNA = Object('Sedna', color=(1, 1, 1, 1), m=8.3e21, a=541.429506 * au, e=0.8590486, i=11.927945, w=310.920993,
               O=144.377238, M=358.190921, JD=2456000.5)

PLANETS = [MERCURY, VENUS, EARTH, MARS, JUPITER, SATURN, URANUS, NEPTUNE, CARES, PLUTO, HAUMEA, MAKEMAKE, ERIS, SEDNA]

for j in range(len(PLANETS)):
    PLANETS[j].planet()

TNOS = []
with open('TNOs.csv') as csvfile1, open('Atens.csv') as csvfile2:
    TNO1 = csv.reader(csvfile1)
    TNO2 = csv.reader(csvfile2)
    for row in TNO1:
        if row[6].isalpha():
            continue
        if row[0].split(' ')[-1].isalpha():
            name = row[0].split(' ')[-1]
        else:
            name = ''
        if name:
            date = get_j_d(int(row[5][6:8]), int(row[5][4:6]), int(row[5][0:4]))
            TNOS.append(Object(name, m=1e20, a=float(row[11]) * au, e=float(row[10]), i=float(row[9]),
                               w=float(row[7]), O=float(row[8]), M=float(row[6]), JD=date))
    for row in TNO2:
        if row[7].isalpha():
            continue
        if row[0].split(' ')[-1].isalpha():
            name = row[0].split(' ')[-1]
        else:
            name = ''
        if name:
            date = get_j_d(int(row[6][6:8]), int(row[6][4:6]), int(row[6][0:4]))
            TNOS.append(Object(name, m=1e15, a=float(row[12]) * au, e=float(row[11]), i=float(row[10]),
                               w=float(row[8]), O=float(row[9]), M=float(row[7]), JD=date))

for j in range(len(TNOS)):
    TNOS[j].asteroid()

# анимация
j = 0


def update():
    global j
    for l in range(len(PLANETS)):
        if j < len(PLANETS[l].X):
            PLANETS[l].pos.setData(pos=array([PLANETS[l].X[j], PLANETS[l].Y[j], PLANETS[l].Z[j]]))
            pts_way = vstack([(PLANETS[l].X[j], PLANETS[l].X[j]),
                              (PLANETS[l].Y[j], PLANETS[l].Y[j]),
                              (PLANETS[l].Z[j], 0)]).transpose()
            PLANETS[l].way.setData(pos=pts_way, width=0.1, color=(0, 0, 0, .5), antialias=True)
    for l in range(len(TNOS)):
        if j < len(TNOS[l].X):
            TNOS[l].pos.setData(pos=array([TNOS[l].X[j], TNOS[l].Y[j], TNOS[l].Z[j]]))
            pts_way = vstack([(TNOS[l].X[j], TNOS[l].X[j]),
                              (TNOS[l].Y[j], TNOS[l].Y[j]),
                              (TNOS[l].Z[j], 0)]).transpose()
            TNOS[l].way.setData(pos=pts_way, width=0.1, color=(0, 0, 0, .5), antialias=True)
    j += 1
    timer.timeout.disconnect(update) if j >= len(MERCURY.X) else None


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1)


if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
