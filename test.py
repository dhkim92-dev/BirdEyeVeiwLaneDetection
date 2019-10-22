import numpy as np
import cv2
import matplotlib.pyplot as plt
from BirdEyeView import BirdEyeView
from LaneDetector import LaneDetector
from CameraCalibrator import Calibrator

##초기화 단계, 차선 인지에 필요한 변수들을 계산함
bev = BirdEyeView() ## 버드아이뷰로 전환할 때 사용할 부분
cbrt = Calibrator() 
cbrt.setVariables() ## 카메라 칼리브레이션을 위한 메트릭스를 세팅함. 매 프레임 새로 구하면 너무 느려서 한번 구해놓고 쓰게 만듦
ldt = LaneDetector(bev) ## 차선인식 클래스

cap = cv2.VideoCapture('hard_video.mp4')

if not cap.isOpened() :
    print('cap is not opened')
    exit(-1)

while True :
    ret,frame = cap.read()
    #print(frame.shape)
    if not ret :
        continue
    u_frame = cbrt.getUndistortedImg(frame)
    roi_frame=  u_frame.copy()
    roi_frame=bev.setROI(roi_frame)
    warped_frame = bev.warpPerspect(u_frame)
    color_comb_frame = bev.combineAllColorChannel(warped_frame,[150,255],[20,100])
    left_fit,right_fit = ldt.slidingWindows(color_comb_frame)
    final_frame = ldt.drawFitLane(frame, color_comb_frame, left_fit,right_fit)

    #cv2.imshow('BirdEyeView', warped_frame)
    #cv2.imshow('color_comb', color_comb_frame*255)
    #cv2.imshow('roi', roi_frame)
    cv2.imshow('final', final_frame)

    if cv2.waitKey(16) == ord('q'):
        cv2.destroyAllWindows()
        break 