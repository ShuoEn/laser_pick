import cv2
retry = 0
camera = cv2.VideoCapture(0)

camera.set(3,1024)
camera.set(4,768)
camera.set(5,30)

camera.set(15, -8)
rev,image=camera.read()
#cv2.imwrite('test.jpg', image)
cv2.imshow('ImageWindow', image)
cv2.waitKey()
camera.release()
