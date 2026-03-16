import cv2
import numpy as np
import os
import threading
from pygame import mixer

# --- إعداد المسارات ---
base_path = os.path.dirname(os.path.abspath(__file__))
ALARM_SOUND_FILE = os.path.join(base_path, "fire_alarm.mp3")

# --- إعداد الصوت ---
mixer.init()
if os.path.exists(ALARM_SOUND_FILE):
    mixer.music.load(ALARM_SOUND_FILE)
else:
    print(f"❌ الملف غير موجود في: {ALARM_SOUND_FILE}")

# متغير عالمي للتحكم في حالة التنبيه
alarm_on = False

def play_alarm_sound():
    """وظيفة تشغيل الصوت"""
    global alarm_on
    try:
        # تشغيل الصوت بتكرار لا نهائي (-1)
        mixer.music.play(-1)
        print("🔔 بدأ تشغيل التنبيه المستمر...")
    except Exception as e:
        print(f"❌ خطأ أثناء التشغيل: {e}")

def stop_alarm_sound():
    """وظيفة إيقاف الصوت"""
    global alarm_on
    mixer.music.stop()
    alarm_on = False
    print("🔕 تم إيقاف التنبيه.")

# --- بدء معالجة الفيديو ---
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # (هنا كود الكشف الخاص بك - مثال مبسط)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_fire = np.array([0, 120, 180])
    upper_fire = np.array([25, 255, 255])
    mask = cv2.inRange(hsv, lower_fire, upper_fire)
    fire_pixels = cv2.countNonZero(mask)

    # التحقق من وجود نار
    if fire_pixels > 800:
        # القفل (Lock): لا تشغل الصوت إذا كان يعمل بالفعل
        if not alarm_on:
            alarm_on = True  # نغير الحالة فوراً قبل تشغيل الخيط
            threading.Thread(target=play_alarm_sound, daemon=True).start()
        
        cv2.putText(frame, "FIRE DETECTED!", (70, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
    else:
        # إذا توقفت النار، أوقف الصوت وغير الحالة
        if alarm_on:
            stop_alarm_sound()

    cv2.imshow('System', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stop_alarm_sound()
cap.release()
cv2.destroyAllWindows()
