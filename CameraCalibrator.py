import glob
import cv2
import matplotlib.pyplot as plt
import numpy as np

""" 이 클래스는 카메라마다 있는 왜곡 현상을 줄이기 위한 카메라 칼리브레이션 변수들을 구하기 위한 클래스입니다. """
## 참조 https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html
## 

class Calibrator() :
	def __init__(self) :
		self.__mtx = None
		self.__dist = None
		self.__rvecs = None
		self.__tbecs = None

	def setVariables(self) :
		obj_pt = np.zeros((6*9,3), np.float32) ## 체스판의 내부 그리드를 각각 좌표로 매핑함. 좌측 하단 0,0,0 우측 1,0,0 이런 방식. (x,y,z) 순
		obj_pt[:,:2] = np.mgrid[0:9, 0:6].T.reshape(-1,2)
		obj_pts=[]#[i for i in obj_pt] # 실제 공간상의 좌표가 저장될 배열
		img_pts=[] # 이미지 상의 좌표의 좌표가 저장될 배열

		imgs = glob.glob('calib_img/calib*.jpg')

		for index,img in enumerate(imgs):
			ori_img= cv2.imread(img)
			gray_img= cv2.cvtColor(ori_img, cv2.COLOR_BGR2GRAY)

			ret, corners = cv2.findChessboardCorners(gray_img, (9,6), None) ## 체스보드 모서리 찾는 함수 반드시 체스판 전체가 보이는 사진을 넣어야함 아니면 체스판사이즈(9,6) 변경
			##corners == 체스판 내부의 각 모서리 점들 좌표가 담긴 배열

			if(ret==True):
				obj_pts.append(obj_pt)
				img_pts.append(corners)
				cv2.drawChessboardCorners(ori_img, (9,6), corners, ret)

		img = cv2.imread('calib_img/calib5.jpg')
		img_size = (img.shape[1], img.shape[0])
		ret, self.__mtx, self.__dist, self.__rvecs, self.__tvecs = cv2.calibrateCamera(obj_pts, img_pts, img_size,None,None)

		"""
		dst = self.getUndistortedImg(img)
		cv2.imshow('w',dst)
		cv2.waitKey()
		cv2.destroyAllWindows()
		"""
		

	def getUndistortedImg(self,img) :
		return cv2.undistort(img, self.__mtx, self.__dist, None, self.__mtx)
		
	@property
	def mtx(self) :
		return self.__mtx

	@property
	def dist(self) :
		return self.__dist

	@property
	def rvecs(self) :
		return self.__rvecs

	@property
	def  tvecs(self) :
		return self.__tvecs

if __name__ == '__main__' :
	c = Calibrator()
	c.setVariables()