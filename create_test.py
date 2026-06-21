import cv2
import numpy as np

img = np.ones((400, 400), dtype=np.uint8) * 200

cv2.rectangle(img, (150, 50), (250, 250), 80, -1)
cv2.rectangle(img, (100, 250), (300, 350), 40, -1)

cv2.imwrite("test.png", img)
print("テスト画像を作成しました")