import os
import cv2
import numpy as np
import PIL
import math
import time
import sys

class  Capture(object):
  def  __init__(self, deviceID=0): # ID为0, 表示从默认的摄像头读取视频数据
    self.deviceID = deviceID
    self.capture = cv2.VideoCapture(self.deviceID) # 
  def  read(self):
    _, frame =  self.capture.read() # 调用默认摄像头捕获一帧图像
    frame = cv2.bilateralFilter(frame, 5, 50, 100) # 对捕获到的图像进行双边滤波
    image=frame
    # image = Image.fromarray(frame) # 转换图像数据格式
    return image


# 移除视频数据的背景噪声
def _remove_background(frame):
  fgbg = cv2.createBackgroundSubtractorMOG2() # 利用BackgroundSubtractorMOG2算法消除背景
  # fgmask = bgModel.apply(frame)
  fgmask = fgbg.apply(frame)
  # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
  # res = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
  kernel = np.ones((3, 3), np.uint8)
  fgmask = cv2.erode(fgmask, kernel, iterations=1)
  res = cv2.bitwise_and(frame, frame, mask=fgmask)
  return res
  # 视频数据的人体皮肤检测
def _bodyskin_detetc(frame):
  # 肤色检测: YCrCb之Cr分量 + OTSU二值化
  ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb) # 分解为YUV图像,得到CR分量
  (_, cr, _) = cv2.split(ycrcb)
  cr1 = cv2.GaussianBlur(cr, (5, 5), 0) # 高斯滤波
  _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # OTSU图像二值化
  return skin


# 检测图像中的凸点(手指)个数
def _get_contours(array):
    # 利用findContours检测图像中的轮廓, 其中返回值contours包含了图像中所有轮廓的坐标点
    contours, _ = cv2.findContours(array, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contours
# 根据图像中凹凸点中的 (开始点, 结束点, 远点)的坐标, 利用余弦定理计算两根手指之间的夹角, 其必为锐角, 根据锐角的个数判别手势.
def _get_eucledian_distance(beg,end):
  return math.sqrt((beg[0]-end[0])*(beg[0]-end[0])+(beg[1]-end[1])*(beg[1]-end[1]))
def _get_defects_count(array, contour, defects, verbose = False):
  ndefects = 0
  for i in range(defects.shape[0]):
    s,e,f,_ = defects[i,0]
    beg     = tuple(contour[s][0])
    end     = tuple(contour[e][0])
    far     = tuple(contour[f][0])
    a       = _get_eucledian_distance(beg, end)
    b       = _get_eucledian_distance(beg, far)
    c       = _get_eucledian_distance(end, far)
    angle   = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) # * 57
    if angle <= math.pi/2 :#90:
      ndefects = ndefects + 1
      if verbose:
        cv2.circle(array, far, 3, _COLOR_RED, -1)
    if verbose:
      cv2.line(array, beg, end, _COLOR_RED, 1)
  return array, ndefects
def grdetect(array, verbose = False):
  copy       = array.copy()
  array = _remove_background(array) # 移除背景, add by wnavy
  thresh = _bodyskin_detetc(array)
  #cv2.imshow('Just for demonstration',thresh)
  # thresh=array
  contours   = _get_contours(thresh) # 计算图像的轮廓

  largecont  = max(contours, key = lambda contour: cv2.contourArea(contour))
  hull           = cv2.convexHull(largecont, returnPoints = False) # 计算轮廓的凸点
  defects        = cv2.convexityDefects(largecont, hull) # 计算轮廓的凹点
  if defects is not None:
    # 利用凹陷点坐标, 根据余弦定理计算图像中锐角个数
    copy, ndefects = _get_defects_count(copy, largecont, defects, verbose = verbose)
    # 根据锐角个数判断手势, 会有一定的误差
    return ndefects

PIPE_BUFFER_SIZE=256
if os.path.exists('/tmp/magicAlbumFIFO'):
    fd=open('/tmp/magicAlbumFIFO','wb')
else:
    print("No Such FIFO")
    exit(-1);
    
cap=Capture(0)
while 1:
  frame=cap.read()
  res=grdetect(frame)
  if res is None:
      res=0
  else :
    res=res+1
  fd.write('{}\n'.format(res).encode())
  fd.flush()
  print ('send msg:', res)
  time.sleep(0.1)
  #cv2.waitKey(1000)

close(fd)
os.system("pause")
