# 移动绿灯识别 - OpenMV H7 Plus (曝光500μs，过曝兼容)

import sensor, image, time

# ========== 初始化摄像头 ==========
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_exposure(False, exposure_us=500)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

# ========== 联合阈值 ==========
# 第1组：绿色边缘（正常绿色）
# 第2组：过曝白色中心（高亮度，A/B接近0）
GREEN_THRESHOLD = [
    (30, 100, -80, -10, -30, 30),    # 绿色边缘
    (80, 100, -15, 15, -15, 15),     # 过曝白色中心
]

clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot()

    # 找色块
    blobs = img.find_blobs(GREEN_THRESHOLD,
                           pixels_threshold=30,      # 降低阈值，适应小目标
                           area_threshold=30,
                           merge=True,               # 合并绿色边缘和白色中心
                           margin=20)                # 增大合并距离

    for blob in blobs:
        # v5.0.0 兼容：属性/方法自动适配
        try:
            x, y, w, h = blob.x(), blob.y(), blob.w(), blob.h()
        except TypeError:
            x, y, w, h = blob.x, blob.y, blob.w, blob.h

        try:
            cx, cy = blob.cx(), blob.cy()
        except TypeError:
            cx, cy = blob.cx, blob.cy

        try:
            area = blob.area()
        except TypeError:
            area = blob.area

        try:
            circularity = blob.density()
        except TypeError:
            circularity = blob.density

        # 移动目标：适当放宽圆形度，避免漏检
        if circularity > 0.3:
            img.draw_rectangle((x, y, w, h), color=(255, 0, 0), thickness=2)
            img.draw_cross((cx, cy), color=(255, 0, 0), size=10)
            img.draw_string((x, y - 15), "Green!", color=(255, 255, 255), scale=2)

            print("Green: cx=%d cy=%d area=%d density=%.2f" % (cx, cy, area, circularity))

    img.draw_string((5, 5), "FPS:%.1f" % clock.fps(), color=(255, 255, 255), scale=1)
