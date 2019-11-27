# Bird Eye View Lane Detection
------------------------------
## 1. 이게 무엇인가요?
- 곡선을 포함한 차선 영역을 탐지하기 위해 만들었던 알고리즘입니다.  
학부생 당시 차선 인식을 해보았으나, 테스트 환경에서는 어느정도 추출이 잘 이루어졌으나 거친 환경에서 안정적인 추출이 되지 않았고  
이에 시점을 변환하는 효과인 버드아이뷰를 이용하여 조금 더 정밀하게 차선을 측정할 수 있지 않을까 하여 시작하게 되었습니다.  

결과물은 다음과 같습니다.  

- Test Result  
![test_bird_eye_view.png](https://github.com/elensar92/BirdEyeVeiwLaneDetection/blob/master/image/test_bird_eye_vidw.png)  

![test_final.png](https://github.com/elensar92/BirdEyeVeiwLaneDetection/blob/master/image/test_final.png)  


-Limitation
![hard_bird_eye_view.png](https://github.com/elensar92/BirdEyeVeiwLaneDetection/blob/master/image/hard_bird_eye_view.png?raw=true)

![hard_final.png](https://github.com/elensar92/BirdEyeVeiwLaneDetection/blob/master/image/hard_final.png)

## 2. 알고리즘 및 파이프라인
-----------------------
  우선 영상에 있는 카메라 왜곡을 제거하기 위해 OpenCV에서 제공하는 체스보드 카메라보정을 이용하여 영상의 왜곡을 보정했습니다.  
  이후 ROI 영역을 설정하고, 해당 ROI 영역을 Bird Eye View로 전환하기 위해 WarpPerspective 함수를 사용하여 시점 변환 Matrix를 얻어오고  
  ROI 영역을 버드아이뷰로 전환 한 뒤 아래의 과정을 따라 차선을 추출하였습니다.
  
  1. warped roi 이미지에서 소벨 엣지 마스크를 구한다.  
  2. warped roi 이미지의 색상 공간을 HLS로 변경하여 threshold 를 적용하고 L, S 채널 마스크를 구한다.  
  3. warped roi 이미지의 색상 공간을 YUV로 변경하여 threshold 를 적용하고 Y 채널 마스크를 구한다.  
  4. 1-3 과정에서 구한 마스크를 합친 이미지를 구한다. (binary_img)
  
  위 과정은 환경 변화에 좀 더 Robust 하게 차선을 추출하기 위하여 거친 과정입니다.  
  
  5. 4에서 구한 이미지의 이미지의 height의 밑에서부터 절반까지의 영역만을 잘라낸다.
  6. 5에서 구한 이미지를 y축으로 누적하여 히스토그램을 구한다.
  
  위 두 과정은 슬라이딩 윈도우 탐색을 위한 x축 기준점을 설정하기 위함입니다. 차선이 있는 곳은 누적값이 크게 나타날 것이므로  
  히스토그램을 통해 탐색 시작점을 설정 할 수 있습니다. 5에서 이미지를 절반으로 자른 것은 버드 아이 뷰로 전환한 이미지가 위로 갈 수록  
  늘어지는 현상이 있어 해당 영역을 포함 시키면 x 좌표 시작 지점을 정확하게 설정하는데 어려움이 있었습니다.  
  
  7. 6에서 구한 히스토그램을 통해 슬라이딩 윈도우 x 시작점을 설정합니다. 차선은 양쪽에 나누어져 있으므로 left_x, right_x 를 구해야합니다.  
  히스토그램에서는 값이 급격히 상승하여 높은 값을 갖는 구간이 두군데 밖에 존재하지 않으므로 히스토그램의 x축 중심점을 기준으로 반으로 나누어  
  threshold를 지정하여 좌우 차선의 중심점이 될 x값을 추출합니다.  
  
  8. 4에서 구한 binary_img에 7에서 구한 left_x, right_x 지점부터 슬라이딩 윈도우로 탐색을 시작합니다.  
  1의 값을 갖는 픽셀들의 x,y 좌표를 모두 읽어들이고, 평균을 내어 해당 탐색 영역의 중심점을 지정하여 저장합니다.
  
  9. 다음 y축 영역을 더해 탐색을 계속합니다.(지정한 window_size 만큼)
  
  10. 8-9 과정에서 구한 좌측 차선의 window 탐색에 따른 중심점 값들을 2차식으로 커브피팅하여 차선을 추출합니다.
  
  11. 10에서 구한 2차식 계수들로 영역을 계산하여 차선 영역을 **warped_img**에 그려줍니다.
  
  12. warped_img 를 다시 원본 roi 영역에 매핑시켜 시점 변환을 시켜줍니다.
  

## 3. 한계
-------------
버드 아이 뷰와 색상 공간 별로 추출한 threshold 마스크를 합쳐 좀 더 환경에 강인한 알고리즘을 만들어보려고 했지만,  
역시 실제 환경에서는 고려할 변수들이 너무 많아 차선 영역이 꼬이는 문제가 한번씩 발생하였습니다.  
더 많은 색상 공간을 조합하여 문제를 해결할 수 있었으나 프레임이 너무 떨어지는 문제가 있었습니다.  

## Enviroment
* Linux Ubuntu
* Mac OS

## Dependencies 
* Python 3
* PyOpenCV
* OpenCV
* Numpy
