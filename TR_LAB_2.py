import cv2
import mediapipe as mp
import time
import webbrowser
import numpy as np

# Инициализация компонентов
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)  # Увеличиваем до 2 рук
mp_draw = mp.solutions.drawing_utils

# Захват видео с веб-камеры
cap = cv2.VideoCapture(0)

# Флаг для предотвращения многократного открытия браузера
last_gesture_time = 0
cooldown = 2  # Задержка в секундах между жестами
gesture_start_time = None  # Время начала жеста
hold_duration = 0.5  # Время удержания жеста в секундах


def detect_five_fingers(hand_landmarks):
    """Проверяет, подняты ли все 5 пальцев (ладонь вверх)"""
    thumb_tip = hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y
    index_tip = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    middle_tip = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    ring_tip = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
    pinky_tip = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y
    return thumb_tip and index_tip and middle_tip and ring_tip and pinky_tip


def detect_inverted_two_fingers(hand_landmarks):
    """Проверяет перевёрнутый '2' (указательный и средний вниз, остальные прижаты)"""
    thumb_down = hand_landmarks.landmark[4].y > hand_landmarks.landmark[3].y
    index_down = hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y
    middle_down = hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y
    ring_up = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
    pinky_up = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y
    return thumb_down and index_down and middle_down and ring_up and pinky_up


def detect_gesture_52(hand_landmarks_list):
    """Проверяет жест '52' для двух рук: '5' и перевёрнутый '2'"""
    if len(hand_landmarks_list) != 2:  # Нужны ровно 2 руки
        return False

    hand1, hand2 = hand_landmarks_list[0], hand_landmarks_list[1]

    # Проверяем, какая рука показывает "5", а какая перевёрнутый "2"
    hand1_five = detect_five_fingers(hand1)
    hand1_two = detect_inverted_two_fingers(hand1)
    hand2_five = detect_five_fingers(hand2)
    hand2_two = detect_inverted_two_fingers(hand2)

    # Жест "52" выполнен, если одна рука показывает "5", а другая перевёрнутый "2"
    return (hand1_five and hand2_two) or (hand1_two and hand2_five)


while True:
    success, frame = cap.read()
    if not success:
        break

    # Преобразование изображения в RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Отрисовка и обработка жестов
    if results.multi_hand_landmarks:
        # Рисуем ключевые точки для всех обнаруженных рук
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Проверяем жест "52" для двух рук
        if detect_gesture_52(results.multi_hand_landmarks):
            current_time = time.time()

            # Если жест только начался, фиксируем время начала
            if gesture_start_time is None:
                gesture_start_time = current_time

            # Проверяем, удерживается ли жест 0.5 секунды
            if current_time - gesture_start_time >= hold_duration:
                # Проверяем кулдаун между выполнениями команды
                if current_time - last_gesture_time > cooldown:
                    webbrowser.open("https://youtu.be/YAdL4iobqwE?si=F8NXVqys0wYXyNuc&t=14")
                    last_gesture_time = current_time
                    gesture_start_time = None  # Сбрасываем время начала после срабатывания
        else:
            # Если жест прервался, сбрасываем время начала
            gesture_start_time = None

    # Отображаем кадр
    cv2.imshow("Hand Gesture Control", frame)

    # Выход по нажатию 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()