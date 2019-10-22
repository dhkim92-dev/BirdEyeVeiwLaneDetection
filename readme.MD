# BirdEyeViewLaneDetection
------------------------------
## what is this?
- This is lane detection using bird eye view.   
For Bird Eye View Lane Detection, I used Camera Calibration to reduce  
camera distortions and Perspective Transformation.  

The purpose of this source is my OpenCV study.  

- Test Result  
![test_bird_eye_view.png](https://github.com/elensar92/BirdEyeVeiwLaneDetection/blob/master/image/test_bird_eye_vidw.png)  

![test_final.png](https://github.com/elensar92/BirdEyeVeiwLaneDetection/blob/master/image/test_final.png)  


-Limitation
![hard_bird_eye_view.png](https://github.com/elensar92/BirdEyeVeiwLaneDetection/blob/master/image/hard_bird_eye_view.png?raw=true)

![hard_final.png](https://github.com/elensar92/BirdEyeVeiwLaneDetection/blob/master/image/hard_final.png)


## Limitation
-------------

* It is tested on just mild conditions.  
As you see pictures on the first phase, Bad condition lanes can not be detected well.  
especially narrow on original view and dim lanes on Bird Eye View.  


## Dependencies 
* Python 3
* OpenCV
* Numpy
