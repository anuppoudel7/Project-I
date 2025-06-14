import os
import cv2
import imagePreprocessingUtils as ipu

CAPTURE_FLAG = False

def capture_images_for_letter(letter, base_dir='dataset'):
    path = os.path.join(base_dir, letter)
    os.makedirs(path, exist_ok=True)

    camera = cv2.VideoCapture(0)
    count = 0
    global CAPTURE_FLAG
    CAPTURE_FLAG = False

    print(f"Starting capture for letter '{letter}'. Press ENTER to start/stop capturing. Press ESC to exit.")

    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 1280, 720)

    while True:
        ret, frame = camera.read()
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # Draw capture rectangle
        cv2.rectangle(frame, ipu.START, ipu.END, (0, 255, 0), 2)

        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        color_white = (255, 255, 255)
        color_green = (0, 255, 0)
        thickness = 2

        # Instruction Text
        cv2.putText(frame, 'Press ENTER to start/stop | ESC to exit',
                    (int(w * 0.05), int(h * 0.08)), font,
                    font_scale, color_white, thickness, cv2.LINE_AA)

        # Letter & Count
        cv2.putText(frame, f"Letter: {letter} | Captured: {count}",
                    (int(w * 0.05), int(h * 0.15)), font,
                    font_scale, color_green, thickness, cv2.LINE_AA)

        if CAPTURE_FLAG and count < 1200:
            roi = frame[ipu.START[1]+5:ipu.END[1], ipu.START[0]+5:ipu.END[0]]
            cv2.imshow("Gesture", roi)

            # Capturing Status
            cv2.putText(frame, 'Capturing...',
                        (int(w * 0.05), int(h * 0.22)), font,
                        font_scale + 0.2, color_green, thickness, cv2.LINE_AA)

            roi = cv2.resize(roi, (ipu.IMG_SIZE, ipu.IMG_SIZE))
            cv2.imwrite(f"{path}/{count}.jpg", roi)
            count += 1
            print(f"{letter}: Captured image {count}")

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        elif key == 13:  # ENTER
            CAPTURE_FLAG = not CAPTURE_FLAG

        cv2.imshow('image', frame)

    camera.release()
    cv2.destroyAllWindows()
    print(f"Capture for letter '{letter}' completed!")
