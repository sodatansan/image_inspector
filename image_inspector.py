import cv2
import numpy as np
import os

SETTINGS_FILE = "settings.txt"

settings = {
    "contrast": 1.0,
    "brightness": 0,
    "threshold": -1,
    "median": 1,
    "dilate": 0,
    "erode": 0,
    "edge_sensitivity": 50,
    "edge_filter": 3,
    "magnification": 0.1
}

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        for key, val in settings.items():
            f.write(f"{key}={val}\n")
    print("設定を保存しました。")

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return
    with open(SETTINGS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                key, val = line.split("=")
                if key in settings:
                    if "." in val:
                        settings[key] = float(val)
                    else:
                        settings[key] = int(val)

def apply_all(image):
    result = image.copy()
    if settings["contrast"] != 1.0 or settings["brightness"] != 0:
        result = cv2.convertScaleAbs(result, alpha=settings["contrast"], beta=settings["brightness"])
    m = settings["median"]
    if m > 1:
        if m % 2 == 0:
            m += 1
        result = cv2.medianBlur(result, m)
    if settings["dilate"] > 0:
        kernel = np.ones((settings["dilate"], settings["dilate"]), np.uint8)
        result = cv2.dilate(result, kernel, iterations=1)
    if settings["erode"] > 0:
        kernel = np.ones((settings["erode"], settings["erode"]), np.uint8)
        result = cv2.erode(result, kernel, iterations=1)
    if settings["threshold"] >= 0:
        _, result = cv2.threshold(result, settings["threshold"], 255, cv2.THRESH_BINARY)
    return result

def measure_and_show(image):
    sens = settings["edge_sensitivity"]
    filt = settings["edge_filter"]
    mag = settings["magnification"]

    edge_img = cv2.Canny(image, sens, sens * 2, apertureSize=filt)

    h, w = edge_img.shape
    center_y = h // 2
    row = edge_img[center_y, :]
    edges = np.where(row > 0)[0]

    result = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if len(edges) >= 2:
        left = edges[0]
        right = edges[-1]
        distance_px = right - left
        distance_mm = distance_px * mag

        cv2.line(result, (left, 0), (left, h), (0, 0, 255), 1)
        cv2.line(result, (right, 0), (right, h), (0, 0, 255), 1)
        cv2.line(result, (left, center_y), (right, center_y), (0, 255, 0), 1)

        print("\n========== 計測結果 ==========")
        print(f"  左エッジ：{left} px")
        print(f"  右エッジ：{right} px")
        print(f"  距離　　：{distance_px} px")
        print(f"  倍率　　：{mag}")
        print(f"  実寸法　：{distance_mm:.2f} mm")
        print("==============================")
    else:
        print("\n  エッジ未検出")

    cv2.imshow("Image", result)
    cv2.waitKey(1)

# 起動
load_settings()
img = cv2.imread("test.png", cv2.IMREAD_GRAYSCALE)
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

print("=== 画像検査ツール ===\n")

processed = apply_all(img)
measure_and_show(processed)

while True:
    print("\n--- 調整メニュー ---")
    print("1.コントラスト\n2.明るさ\n3.2値化\n4.メディアン\n5.膨張\n6.収縮\n7.エッジ感度\n8.フィルタ幅\n9.倍率\nr.リセット\nw.設定保存\n0.終了")

    select = input("選択：")

    if select == "1":
        settings["contrast"] = float(input("コントラスト(0.1~10.0)："))
    elif select == "2":
        settings["brightness"] = int(input("明るさ(-100~100)："))
    elif select == "3":
        settings["threshold"] = int(input("しきい値(0~255, -1=OFF)："))
    elif select == "4":
        settings["median"] = int(input("メディアン(1,3,5,7...)："))
    elif select == "5":
        settings["dilate"] = int(input("膨張(0~10)："))
    elif select == "6":
        settings["erode"] = int(input("収縮(0~10)："))
    elif select == "7":
        settings["edge_sensitivity"] = int(input("エッジ感度(1~100)："))
    elif select == "8":
        val = int(input("フィルタ幅(3,5,7)："))
        if val in [3, 5, 7]:
            settings["edge_filter"] = val
        else:
            print("3,5,7のみ")
            continue
    elif select == "9":
        settings["magnification"] = float(input("倍率(例:0.1)："))
    elif select == "r":
        settings = {"contrast":1.0,"brightness":0,"threshold":-1,"median":1,
                     "dilate":0,"erode":0,"edge_sensitivity":50,"edge_filter":3,"magnification":0.1}
        print("リセット")
    elif select == "w":
        save_settings()
        continue
    elif select == "0":
        save_settings()
        cv2.destroyAllWindows()
        print("終了")
        break
    else:
        print("正しい値を入力してください")
        continue

    processed = apply_all(img)
    measure_and_show(processed)