import cv2
import torch
import pytesseract
import numpy as np
from ultralytics import YOLO


pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Initialize YOLOv8 Model
class NumberPlateDetector:
    def __init__(self, model_path="models/best.pt"):
        
        self.model = YOLO(model_path)

    def detect_plate(self, frame):

        results = self.model(frame)
        
        
        plates = results[0].boxes.xyxy.cpu().numpy()  # Get bounding boxes (xyxy format)
        
       
        rendered_frame = results[0].plot()  # This plots the boxes on the frame
        return plates, rendered_frame

    @staticmethod
    def extract_text(cropped_image):
        
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        return pytesseract.image_to_string(gray, config="--psm 7").strip()

def crop_plate(frame, bbox):

    x_min, y_min, x_max, y_max = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    return frame[y_min:y_max, x_min:x_max]

def draw_text(frame, text, position, color=(0, 255, 0), font_scale=1, thickness=2):
    
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

def main():
    # Load YOLOv8 model
    detector = NumberPlateDetector()

   
    cap = cv2.VideoCapture(0) 

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting real-time number plate detection and recognition. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Detect number plates in the frame
        plates, rendered_frame = detector.detect_plate(frame)

        # Process detected plates
        for plate in plates:
            # Crop the detected plate
            cropped_image = crop_plate(frame, plate)

            # Extract text from the cropped plate
            text = detector.extract_text(cropped_image)
            print(f"Detected Plate Text: {text}")

        
            x_min, y_min, x_max, y_max = int(plate[0]), int(plate[1]), int(plate[2]), int(plate[3])
            draw_text(rendered_frame, text, (x_min, y_min - 10), color=(255, 0, 0))

        
            cv2.rectangle(rendered_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        # Display the frame with detections and text
        cv2.imshow("Number Plate Detection and Recognition", rendered_frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

   
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
