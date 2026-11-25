import cv2
import numpy as np
from ultralytics import YOLO


class ImageAnalyzer:

    def __init__(self):
        self.model = YOLO("yolo11s.pt")

        self.thresholds = {
            "person": 0.40,
            "motorcycle": 0.20,
            "bicycle": 0.20,
            "car": 0.20,
            "bus": 0.25,
            "truck": 0.30,
            "train": 0.30
        }

    def analyze(self, image_path):
        image = cv2.imdecode(
            np.fromfile(image_path, dtype=np.uint8),
            cv2.IMREAD_COLOR
        )

        if image is None:
            return {
                "success": False,
                "error": "Unable to read image."
            }

        height, width = image.shape[:2]

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blur_score = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        brightness = gray.mean()

        results = self.model(
            image,
            conf=0.15,
            verbose=False
        )

        detections = []
        confirmed_detections = []

        for result in results:
            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = self.model.names[class_id]

                detection = {
                    "object": class_name,
                    "confidence": round(confidence * 100, 2)
                }

                detections.append(detection)

                threshold = self.thresholds.get(
                    class_name,
                    0.40
                )

                if confidence >= threshold:
                    confirmed_detections.append(detection)

        people_count = sum(
            1 for item in confirmed_detections
            if item["object"] == "person"
        )

        motorcycle_count = sum(
            1 for item in confirmed_detections
            if item["object"] == "motorcycle"
        )

        vehicle_types = [
            "car",
            "motorcycle",
            "bus",
            "truck",
            "train"
        ]

        vehicle_count = sum(
            1 for item in confirmed_detections
            if item["object"] in vehicle_types
        )

        if blur_score < 50:
            image_quality = "Low"
        elif blur_score < 150:
            image_quality = "Medium"
        else:
            image_quality = "High"

        if confirmed_detections:
            average_confidence = sum(
                item["confidence"]
                for item in confirmed_detections
            ) / len(confirmed_detections)
        else:
            average_confidence = 0

        if average_confidence >= 70:
            reliability = "High"
        elif average_confidence >= 40:
            reliability = "Medium"
        else:
            reliability = "Low"

        scene_type = "No clear incident detected"
        recommendation = "Manual assessment recommended"

        if motorcycle_count > 0 and people_count > 0:
            scene_type = "Possible Road Accident"
            recommendation = (
                "Medical and police assistance may be required"
            )

        elif vehicle_count >= 2 and people_count > 0:
            scene_type = "Possible Vehicle Incident"
            recommendation = (
                "Police and medical assistance may be required"
            )

        elif people_count >= 2:
            scene_type = "Multiple People Scene"
            recommendation = (
                "Further incident assessment recommended"
            )

        return {
            "success": True,
            "image_width": width,
            "image_height": height,
            "people_count": people_count,
            "motorcycle_count": motorcycle_count,
            "vehicle_count": vehicle_count,
            "image_quality": image_quality,
            "blur_score": round(blur_score, 2),
            "brightness": round(float(brightness), 2),
            "average_confidence": round(average_confidence, 2),
            "ai_reliability": reliability,
            "scene_type": scene_type,
            "recommendation": recommendation,
            "detections": detections,
            "confirmed_detections": confirmed_detections
        }


if __name__ == "__main__":

    analyzer = ImageAnalyzer()

    image_path = input(
        "Enter image path: "
    ).strip().strip('"')

    result = analyzer.analyze(image_path)

    print("\n--- RESCUE AI IMAGE ANALYSIS ---")

    if not result["success"]:
        print("Error:", result["error"])

    else:

        print(
            "Image Size:",
            result["image_width"],
            "x",
            result["image_height"]
        )

        print(
            "People Detected:",
            result["people_count"]
        )

        print(
            "Motorcycles Detected:",
            result["motorcycle_count"]
        )

        print(
            "Vehicles Detected:",
            result["vehicle_count"]
        )

        print(
            "Image Quality:",
            result["image_quality"]
        )

        print(
            "Average AI Confidence:",
            str(result["average_confidence"]) + "%"
        )

        print(
            "AI Reliability:",
            result["ai_reliability"]
        )

        print(
            "Scene Assessment:",
            result["scene_type"]
        )

        print(
            "Recommendation:",
            result["recommendation"]
        )

        print("\nConfirmed Objects:")

        for item in result["confirmed_detections"]:
            print(
                f"- {item['object']}: "
                f"{item['confidence']}%"
            )

        print("\nRaw YOLO Detections:")

        for item in result["detections"]:
            print(
                f"- {item['object']}: "
                f"{item['confidence']}%"
            )