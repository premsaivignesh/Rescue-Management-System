import sys
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parents[2]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


class VideoAnalyzer:

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

    def analyze_video(self, video_path, sample_rate=15):

        video_path = str(video_path).strip().strip('"')

        capture = cv2.VideoCapture(video_path)

        if not capture.isOpened():
            raise ValueError("Unable to open video file.")

        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = capture.get(cv2.CAP_PROP_FPS)

        if fps <= 0:
            fps = 30

        duration = total_frames / fps if total_frames > 0 else 0

        people = []
        motorcycles = []
        vehicles = []

        confidences = []
        blur_scores = []
        brightness_values = []

        processed_frames = 0

        frame_index = 0

        while True:

            success, frame = capture.read()

            if not success:
                break

            if frame_index % sample_rate != 0:
                frame_index += 1
                continue

            processed_frames += 1

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            blur_score = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            brightness = float(np.mean(gray))

            blur_scores.append(float(blur_score))
            brightness_values.append(brightness)

            results = self.model(
                frame,
                conf=0.15,
                verbose=False
            )

            frame_people = 0
            frame_motorcycles = 0
            frame_vehicles = 0

            for result in results:

                if result.boxes is None:
                    continue

                for box in result.boxes:

                    confidence = float(
                        box.conf[0]
                    )

                    class_id = int(
                        box.cls[0]
                    )

                    label = self.model.names[class_id]

                    threshold = self.thresholds.get(
                        label,
                        0.25
                    )

                    if confidence < threshold:
                        continue

                    confidences.append(confidence)

                    if label == "person":
                        frame_people += 1

                    elif label == "motorcycle":
                        frame_motorcycles += 1
                        frame_vehicles += 1

                    elif label in {
                        "bicycle",
                        "car",
                        "bus",
                        "truck",
                        "train"
                    }:
                        frame_vehicles += 1

            people.append(frame_people)
            motorcycles.append(frame_motorcycles)
            vehicles.append(frame_vehicles)

            frame_index += 1

        capture.release()

        if processed_frames == 0:
            raise ValueError("No video frames could be processed.")

        max_people = max(people)
        max_motorcycles = max(motorcycles)
        max_vehicles = max(vehicles)

        average_confidence = (
            float(np.mean(confidences))
            if confidences
            else 0.0
        )

        average_blur = float(
            np.mean(blur_scores)
        )

        average_brightness = float(
            np.mean(brightness_values)
        )

        image_quality = self._quality(
            average_blur,
            average_brightness
        )

        reliability = self._reliability(
            average_confidence,
            image_quality,
            processed_frames
        )

        scene = self._scene_assessment(
            max_people,
            max_motorcycles,
            max_vehicles
        )

        recommendation = self._recommendation(
            scene,
            max_people
        )

        return {
            "video": {
                "total_frames": total_frames,
                "processed_frames": processed_frames,
                "fps": round(fps, 2),
                "duration_seconds": round(duration, 2)
            },

            "people_detected": max_people,

            "motorcycles_detected": max_motorcycles,

            "vehicles_detected": max_vehicles,

            "image_quality": image_quality,

            "average_ai_confidence": round(
                average_confidence * 100,
                2
            ),

            "ai_reliability": reliability,

            "scene_assessment": scene,

            "recommendation": recommendation
        }

    def _quality(self, blur, brightness):

        if blur < 50:
            return "Low"

        if brightness < 40 or brightness > 220:
            return "Medium"

        if blur >= 150:
            return "High"

        return "Medium"

    def _reliability(
        self,
        confidence,
        quality,
        processed_frames
    ):

        # Reliability is a heuristic quality indicator, not a probability of truth.
        quality_score = {"High": 1.0, "Medium": 0.65, "Low": 0.30}.get(quality, 0.5)
        frame_score = min(1.0, processed_frames / 20.0)
        score = (0.70 * confidence) + (0.20 * quality_score) + (0.10 * frame_score)

        if score >= 0.75:
            return "High"
        if score >= 0.50:
            return "Medium"
        return "Low"

    def _scene_assessment(
        self,
        people,
        motorcycles,
        vehicles
    ):

        if motorcycles > 0 and people > 0:
            return "Possible Road Accident"

        if vehicles > 0 and people > 0:
            return "Possible Road Incident"

        if people >= 3:
            return "Multiple People Detected"

        if people > 0:
            return "People Detected"

        return "No Major Rescue Scene Detected"

    def _recommendation(
        self,
        scene,
        people
    ):

        if scene == "Possible Road Accident":
            return "Medical and police assistance may be required"

        if scene == "Possible Road Incident":
            return "Police and medical assistance may be required"

        if people >= 3:
            return "Multiple people detected; further assessment recommended"

        if people > 0:
            return "Further incident assessment recommended"

        return "No immediate resource recommendation"


if __name__ == "__main__":

    print("\n========== RESCUE AI VIDEO ANALYSIS ==========\n")

    video_path = input(
        "Enter video path: "
    ).strip().strip('"')

    try:

        analyzer = VideoAnalyzer()

        result = analyzer.analyze_video(
            video_path
        )

        print(
            f"Total Frames: "
            f"{result['video']['total_frames']}"
        )

        print(
            f"Processed Frames: "
            f"{result['video']['processed_frames']}"
        )

        print(
            f"Duration: "
            f"{result['video']['duration_seconds']} seconds"
        )

        print(
            f"People Detected: "
            f"{result['people_detected']}"
        )

        print(
            f"Motorcycles Detected: "
            f"{result['motorcycles_detected']}"
        )

        print(
            f"Vehicles Detected: "
            f"{result['vehicles_detected']}"
        )

        print(
            f"Video Quality: "
            f"{result['image_quality']}"
        )

        print(
            f"Average AI Confidence: "
            f"{result['average_ai_confidence']:.2f}%"
        )

        print(
            f"AI Reliability: "
            f"{result['ai_reliability']}"
        )

        print(
            f"Scene Assessment: "
            f"{result['scene_assessment']}"
        )

        print(
            f"Recommendation: "
            f"{result['recommendation']}"
        )

        print("\n=============================================\n")

    except Exception as e:

        print(f"\nError: {e}")