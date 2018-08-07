import unicornhat as uh
import threading
import time
import geocoder
from weather import Weather, Unit
from random import randint
from multiprocessing import Process

try:
  import numpy
except ImportError:
  exit("This script requires numpy module")

# location = geocoder.ip('me')
# weather = Weather(unit=Unit.CELSIUS)

uh.rotation(180)
uh.brightness(0.5)
uh.set_layout(uh.AUTO)
uhW,uhH=uh.get_shape()

WEATHER_STATUS = {
  0: "tornado",
  1: "tropical storm",
  2: "hurricane",
  3: "severe thunderstorms",
  4: "thunderstorms",
  5: "mixed rain and snow",
  6: "mixed rain and sleet",
  7: "mixed snow and sleet",
  8: "freexing drizzle",
  9: "drizzle",
  10: "freezing rain",
  11: "showers",
  12: "showers",
  13: "snow flurries",
  14: "light snow showers",
  15: "blowing snow",
  16: "snow",
  17: "hail",
  18: "sleet",
  19: "dust",
  20: "foggy",
  21: "haze",
  22: "smoky",
  23: "blustery",
  24: "windy",
  25: "cold",
  26: "cloudy",
  27: "mostly cloudy (night)",
  28: "mostly cloudy (day)",
  29: "partly cloudy (night)",
  30: "partly cloudy (day)",
  31: "clear (night)",
  32: "sunny",
  33: "fair (night)",
  34: "fair (day)",
  35: "mixed rain and hail",
  36: "hot",
  37: "isolated thunderstorms",
  38: "scattered thunderstorms",
  39: "scattered thunderstorms",
  40: "scattered showers",
  41: "heavy snow",
  42: "scattered snow showers",
  43: "heavy snow",
  44: "partly cloudy",
  45: "thundershowers",
  46: "snow showers",
  47: "isolated thundershowers",
  3200: "not available"
}

# print(location.latlng)

# lookup = weather.lookup_by_latlng(location.latlng[0], location.latlng[1])
# condition = lookup.condition
# print(condition.text)

# print(lookup.title)
animationFlag = False
c = threading.Condition()

class Frame:
  def __init__(self, h, w):
    self.height = h
    self.width = w
    self.clear()

  def clear(self):
    self.grid = []
    for i in range(self.height):
      self.grid.append([(0, 0, 0)] * self.width)

  def setFrame(self, frame):
    self.grid = frame

  def setRow(self, rowIndex, row):
    self.grid[rowIndex] = row

  def setPixel(self, x, y, rgb):
    self.grid[x][y] = rgb

  def setAllPixels(self, rgb):
    for i in range(self.height):
      for j in range(self.width):
        self.grid[i][j] = rgb

  def getGrid(self):
    return self.grid

  def getDimensions(self):
    return self.height, self.width

class FrameAnimation:
  def __init__(self, animation=[], pauses=[], height=0, width=0):
    self.animation = animation
    self.pauses = pauses
    self.height = height
    self.width = width
    self.running = False
    self.generateAnimation()
    self.thread = threading.Thread(target=self.__updateDisplay, args=())
    self.thread.daemon = True

  # this function should be overriden in child classes with
  # specific animation logic
  # should set self.animation and self.pauses
  def generateAnimation(self):
    # for this template class we will just animate a falling line
    # since we are scrolling down, we will generate self.height frames
    # and self.height-1 pauses of 1/self.height for 1s per loop
    for i in range(self.height):
      frame = Frame(self.height, self.width)
      frame.setAllPixels((255, 255, 255))
      frame.setRow(i, [(0,0,0)] * self.width)
      print(frame.getGrid())
      self.animation.append(frame)
    self.pauses = [0.5 / self.height] * self.height

  def __updateDisplay(self):
    global animationFlag
    global c
    c.acquire()
    animationFlag = True
    c.notify_all()
    count = 0
    while(animationFlag):
      print(count, self.pauses[count])
      frame = self.animation[count]
      uh.set_pixels(frame.getGrid())
      time.sleep(self.pauses[count])
      uh.show()
      if count < len(self.animation) - 1:
        count += 1
      else:
        count = 0
      print(animationFlag)
      if animationFlag == False:
        c.release()
        break
      else:
        c.wait()

  def run(self):
    self.thread.start()

  def stop(self):
    self.running = False

# base = FrameAnimation(height=uhH, width=uhW)
# def stopBase():
#   time.sleep(5)
#   base.stop()
# runInParallel(base.run, stopBase)

# grid = clearGrid()
# updateDisplay(grid)
# while True:
#   step()
#   time.sleep(0.25)
#   updateDisplay(grid)

class FlashAnimation(FrameAnimation):
  # 4 flashes per second
  def generateAnimation(self):
    for i in range(4):
      frame = Frame(self.height, self.width)
      frame.setAllPixels((0, 0, 0)) if i % 2 == 1 else frame.setAllPixels((255, 255, 255))
      self.animation.append(frame)
    self.pauses = [0.25] * 4

# flash = FlashAnimation(height=uhH, width=uhW)
# def stopFlash():
#   time.sleep(5)
#   flash.stop()
# runInParallel(flash.run, stopFlash)

class RainAnimation(FrameAnimation):
  # 10s animation - 8 fps
  def generateAnimation(self):
    # dropColumn
    # dropLength
    # for i in range(80):
    #   frame = Frame(self.height, self.width)
    #   frame.setAllPixels((63, 63, 126))
    row = 0
    for i in range(self.height * 8):
      frame = Frame(self.height, self.width)
      frame.setAllPixels((126,126,126))
      if row == self.height - 1:
        row = 0
      else:
        row += 1
      frame.setRow(row, [(63, 63, 126)] * self.width)
      print(frame.getGrid())
      if i == 20:
        uh.set_all((63, 63, 63))
      self.animation.append(frame)
    self.pauses = [10 / self.height * 8] * self.height

rain = RainAnimation(height=uhH, width=uhW)
rain.run()