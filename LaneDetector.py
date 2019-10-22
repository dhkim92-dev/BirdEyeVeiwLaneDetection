import numpy as np
import cv2
from BirdEyeView import BirdEyeView 
import matplotlib.pyplot as plt

class LaneDetector() :
	def __init__(self,bev) :
		self.__bev = bev
		pass

	def slidingWindows(self, binary_img, draw = True) :
		## sliding windows 방식으로 좌 우 차선의 영역을 탐지함.
		histogram = self.__bev.histogram(binary_img)
		#print('histogram shape : ',histogram.shape)
		#print(binary_img.shape)
		#print(np.argmax(histogram))
		#print(np.argmax(binary_img))
		out_img = np.dstack((binary_img, binary_img, binary_img))#*255  ## binary 이미지를 3가지 색상 채널로 변경, 0-1사이로 노멀라이즈 되어있으므로 255를 곱함

		width_mid_pt = np.int(histogram.shape[0]/2) ## 이미지의 width의 중점
		left_x_base = np.argmax(histogram[:width_mid_pt]) ## 히스토그램을 반으로 나눠서 히스토그램의 값이 첫번째로 높아지는 구간을 좌측 레인 탐지의 베이스로 잡는다.
		right_x_base = np.argmax(histogram[width_mid_pt:]) + width_mid_pt ## 히스토그램을 반으로 나눠서 우측 영역에서 히스토그램이 높이자는 구간을 우측 레인 탐지의 베이스로 잡는다.

		"""
		print("---------------------------")
		print('width-mp : ',width_mid_pt)
		print('left_x_base : ',left_x_base)
		print('right_x_base : ',right_x_base)
		"""

		n_win = 13 ## 좌,우 차선별 탐지 윈도우의 개수, 적어지면 샘플링이 적어지는 샘이라서 급커브 같은데서 영역을 정확히 못잡아냄
		window_height = np.int(binary_img.shape[0]/n_win) ## 윈도우 높이
		non_zero = binary_img.nonzero() ## binary_img에서 값이 0 이 아닌 픽셀들의 좌표를 x 좌표 y 좌표로 각각 인덱싱해서 배출. 예를들어 0,0의 픽셀값이 0이 아니라면 array([array[0], array[0]]) 형태 
		non_zero_y = np.array(non_zero[0]) ## 0이아닌 y좌표 
		non_zero_x = np.array(non_zero[1]) ## 0이아닌 x좌표

		left_x_current = left_x_base 
		right_x_current = right_x_base 

		margin = 100 ## 윈도우 margin
		min_pix = 50 

		left_lane_indices = []
		right_lane_indices = []

		for window in range(n_win):
			## 각 윈도우는 버드아이뷰 상단점을 기준으로 y 윈도우들의 좌표값을 구한다 .
			## win_y_low는 이미지 최상단 y좌표 (height)에서 window+1 에 heght를 곱하면 그만큼 아래쪽이며
			## win_y_high 는 그 low 좌표와 짝을 이루는 위쪽 좌표이므로 window 에 height를 곱한다.
			win_y_low = binary_img.shape[0] - (window+1)*window_height
			win_y_high = binary_img.shape[0] - window*window_height


			## 좌측차선의 윈도우 위 아래 x좌표 
			win_x_left_low = left_x_current - margin
			win_x_left_high = left_x_current + margin

			## 우측 차선의 윈도우 위 아래 x 좌표 
			win_x_right_low = right_x_current - margin
			win_x_right_high = right_x_current + margin

			"""
			다음 아래 두 식은 다음과 같은 연산을 진행함.
			non_zero_y 의 모든 좌표 중 현재 window의 y 최소값, 최대값 보다 큰값에 대한 판별을 진행한 TF 테이블을 만들고
			x에 대해서도 같은 방식을 진행하여 TF 테이블을 만든다. 이 값들이 모두 T인 지점들은 1이 나오므로
			해당 점들을 non_zero 로 뽑아내고 x축 값만을 취함
			"""

			good_left_indices = ((non_zero_y >= win_y_low) & (non_zero_y < win_y_high) & 
			(non_zero_x >= win_x_left_low) &  (non_zero_x < win_x_left_high)).nonzero()[0]
			good_right_indices = ((non_zero_y >= win_y_low) & (non_zero_y < win_y_high) & 
			(non_zero_x >= win_x_right_low) &  (non_zero_x < win_x_right_high)).nonzero()[0]


			##위에서 추려낸 값을 append
			left_lane_indices.append(good_left_indices)
			right_lane_indices.append(good_right_indices)

			## 다음 윈도우 위치 업데이트
			if len(good_left_indices) > min_pix:
				left_x_current = np.int(np.mean(non_zero_x[good_left_indices]))

			if len(good_right_indices) > min_pix:        
				right_x_current = np.int(np.mean(non_zero_x[good_right_indices]))

		## 배열 합치기
		## 이 부분은 디텍팅 된 차선의 픽셀의 좌표 집합임.
		left_lane_indices = np.concatenate(left_lane_indices)
		right_lane_indices = np.concatenate(right_lane_indices)

		# 좌 우측 라인의 픽셀 위치들을 추출
		left_x = non_zero_x[left_lane_indices]
		left_y = non_zero_y[left_lane_indices] 
		right_x = non_zero_x[right_lane_indices]
		right_y = non_zero_y[right_lane_indices] 

		## 다항식으로 피팅한 좌표들을 2차다항식으로 피팅
		left_fit = np.polyfit(left_y, left_x, 2)
		right_fit = np.polyfit(right_y, right_x, 2)

		return left_fit,right_fit

	def drawFitLane(self, frame, binary_warped_frame, left_fit, right_fit) :
		height,width = binary_warped_frame.shape

		M = cv2.getPerspectiveTransform(self.__bev.dst,self.__bev.src) ## 시점변환용 메트릭스. 
		##Bird Eye View 에서는 src -> dst 로의 시점 전환을 수행하였으므로
		##원본 좌표로 복구를 위해서 dst->src 로 변환을 해야함

		plot_y = np.linspace(0,binary_warped_frame.shape[0]-1, binary_warped_frame.shape[0])

		#print(plot_y)

		left_fit_x = left_fit[0] * plot_y**2 + left_fit[1] * plot_y +left_fit[2]
		right_fit_x = right_fit[0] * plot_y**2 + right_fit[1] * plot_y + right_fit[2]

		##print("bwf shape : ",binary_warped_frame.shape)

		warp_zero = np.zeros_like(binary_warped_frame).astype(np.uint8) 
		color_warp = np.dstack((warp_zero, warp_zero, warp_zero)) 
		## np.dstack => 양쪽 행렬의 element wise 로 값을 짝지어 열벡터를 만든다.
		## 예 a= [[1,2],[3,4]] ,b = [[-2,-3],[-4,-5]]
		## np.dstack(a,b) = [[1,-2],
		##					 [2,-3], ...]
		##color_warp = 720 * 1280 * 3


		plot_y = np.linspace(0,height-1,height) ## 0,height-1 사이 범위에 height 수 만큼의 샘플 생성

		lefts = np.array([np.transpose(np.vstack([left_fit_x, plot_y]))])
		## np.vstack => a = [1,2,3;4,5,6;7,8,9] b = [-1,-2,-3;...;--7,-8,-9] => np.vstack([a,b])
		## 1 2 3
		## 4 5 6
		## 7 8 9
		## -1 -2 -3
		## ...
		## -7,-8,-9
		rights = np.array([np.flipud(np.transpose(np.vstack([right_fit_x, plot_y])))]) 
		## np.flidud을 row기준으로 위아래 순서를 뒤바꿔버림. 

		points = np.hstack((lefts,rights))

		cv2.fillPoly(color_warp, np.int_([points]),(0,0,255))
		cv2.polylines(color_warp, np.int32([lefts]), isClosed=False, color = (255,255,0),thickness = 10)
		cv2.polylines(color_warp, np.int32([rights]), isClosed=False, color = (255,0,255),thickness = 10)

		new = cv2.warpPerspective(color_warp, M, (width, height))
		output = cv2.addWeighted(frame,1,new,0.5,0)

		return output







