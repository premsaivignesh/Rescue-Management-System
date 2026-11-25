"""Unified multimodal AI layer for Rescue Management System."""

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from ai_ml.predictions.text_predictor import predict_incident
from ai_ml.predictions.spam_predictor import predict_spam
from ai_ml.predictions.resource_predictor import predict_resources

from ai_ml.computer_vision.image_analyzer import ImageAnalyzer
from ai_ml.computer_vision.video_analyzer import VideoAnalyzer


class RescueAI:

    def __init__(self):
        self.image_analyzer = ImageAnalyzer()
        self.video_analyzer = VideoAnalyzer()

    @staticmethod
    def _normalise_type(label):
        mapping = {
            "Road Accident": "Accident",
            "Medical Emergency": "Medical",
            "Building Collapse": "Other",
        }

        return mapping.get(label, label)

    @staticmethod
    def _confidence(value):
        value = float(value)

        if value > 1:
            return value / 100

        return value

    @staticmethod
    def _priority(
        severity,
        people,
        resources,
        reliability=0.5
    ):

        base = {
            "Low": 25,
            "Medium": 50,
            "High": 75,
            "Critical": 95
        }.get(severity, 40)

        score = base

        score += min(
            15,
            max(0, people) * 2
        )

        score += min(
            8,
            sum(resources.values())
        )

        if reliability < 0.40:
            score -= 5

        return max(
            0,
            min(
                100,
                int(round(score))
            )
        )

    @staticmethod
    def _department(
        incident_type,
        resources
    ):

        if (
            resources.get("fire", 0) > 0
            or incident_type == "Fire"
        ):
            return "Fire"

        if (
            resources.get("ambulance", 0) > 0
            and incident_type == "Medical"
        ):
            return "Ambulance"

        return "Police"

    @staticmethod
    def _extract_people_from_text(
        description
    ):

        match = re.search(
            r"\b(\d+)\s+"
            r"(?:people|persons|victims|"
            r"injured|patients)\b",
            description.lower()
        )

        if match:
            return int(match.group(1))

        return 0

    def analyze_incident(
        self,
        description,
        incident_type_hint=None,
        image_path=None,
        video_path=None
    ):

        # ----------------------------------
        # TEXT ML
        # ----------------------------------

        text_result = predict_incident(
            description
        )

        spam_result = predict_spam(
            description
        )

        # ----------------------------------
        # COMPUTER VISION
        # ----------------------------------

        image_result = None
        video_result = None

        if image_path:

            image_result = self.image_analyzer.analyze(
                str(image_path).strip().strip('"')
            )

        if video_path:

            video_result = self.video_analyzer.analyze_video(
                str(video_path).strip().strip('"')
            )

        # ----------------------------------
        # EXTRACT VISUAL EVIDENCE
        # ----------------------------------

        people_candidates = []
        vehicle_candidates = []
        motorcycle_candidates = []

        reliability_values = [
            self._confidence(
                text_result["severity_confidence"]
            )
        ]

        # IMAGE

        if image_result:

            people_candidates.append(
                int(
                    image_result.get(
                        "people_count",
                        0
                    )
                )
            )

            vehicle_candidates.append(
                int(
                    image_result.get(
                        "vehicle_count",
                        0
                    )
                )
            )

            motorcycle_candidates.append(
                int(
                    image_result.get(
                        "motorcycle_count",
                        0
                    )
                )
            )

            image_confidence = float(
                image_result.get(
                    "average_confidence",
                    0
                )
            )

            reliability_values.append(
                self._confidence(
                    image_confidence
                )
            )

        # VIDEO

        if video_result:

            people_candidates.append(
                int(
                    video_result.get(
                        "people_detected",
                        0
                    )
                )
            )

            vehicle_candidates.append(
                int(
                    video_result.get(
                        "vehicles_detected",
                        0
                    )
                )
            )

            motorcycle_candidates.append(
                int(
                    video_result.get(
                        "motorcycles_detected",
                        0
                    )
                )
            )

            video_confidence = float(
                video_result.get(
                    "average_ai_confidence",
                    0
                )
            )

            reliability_values.append(
                self._confidence(
                    video_confidence
                )
            )

        people = max(
            people_candidates,
            default=0
        )

        vehicles = max(
            vehicle_candidates,
            default=0
        )

        motorcycles = max(
            motorcycle_candidates,
            default=0
        )

        # ----------------------------------
        # TEXT FALLBACK FOR PEOPLE COUNT
        # ----------------------------------

        if people == 0:

            people = (
                self._extract_people_from_text(
                    description
                )
            )

        # ----------------------------------
        # INCIDENT + SEVERITY
        # ----------------------------------

        incident_type = self._normalise_type(
            text_result["incident_type"]
        )

        severity = text_result["severity"]

        # ----------------------------------
        # RESOURCE ML
        # ----------------------------------

        resources = predict_resources(
            incident_type,
            severity,
            people,
            vehicles,
            motorcycles
        )

        resource_counts = {
            "ambulance": resources[
                "ambulance_required"
            ],

            "police": resources[
                "police_required"
            ],

            "fire": resources[
                "fire_engine_required"
            ]
        }

        # ----------------------------------
        # AI RELIABILITY
        # ----------------------------------

        overall_reliability = (
            sum(reliability_values)
            / len(reliability_values)
        )

        # ----------------------------------
        # PRIORITY
        # ----------------------------------

        priority = self._priority(
            severity,
            people,
            resource_counts,
            overall_reliability
        )

        # ----------------------------------
        # DEPARTMENT
        # ----------------------------------

        department = self._department(
            incident_type,
            resource_counts
        )

        # ----------------------------------
        # SPAM STATUS
        # ----------------------------------

        spam_label = str(
            spam_result["label"]
        )

        if spam_label.lower() == "genuine":

            status = "AI Reviewed - Genuine"

        else:

            status = (
                "AI Flagged - Possible Spam"
            )

        # ----------------------------------
        # FINAL RESULT
        # ----------------------------------

        return {

            "text": text_result,

            "spam": spam_result,

            "image": image_result,

            "video": video_result,

            "evidence": {

                "people_estimated": people,

                "vehicle_count": vehicles,

                "motorcycle_count": motorcycles,

                "overall_reliability":
                    round(
                        overall_reliability,
                        3
                    )
            },

            "resources": resource_counts,

            "department": department,

            "priority": priority,

            "status": status,

            "model_note":
                "Visual detections are object "
                "evidence; injury or medical "
                "diagnosis is not performed "
                "by YOLO."
        }


def print_result(result):

    text = result["text"]

    evidence = result["evidence"]

    resources = result["resources"]

    print(
        "\n========== RESCUE AI RESULT ==========\n"
    )

    # TEXT

    print("TEXT ML")

    print(
        f"Incident Type: "
        f"{text['incident_type']} "
        f"({text['incident_type_confidence']:.2%}, "
        f"{text['incident_type_confidence_level']})"
    )

    print(
        f"Severity: "
        f"{text['severity']} "
        f"({text['severity_confidence']:.2%}, "
        f"{text['severity_confidence_level']})"
    )

    # SPAM

    print("\nSPAM DETECTION")

    print(
        f"Result: "
        f"{result['spam']['label']} "
        f"({result['spam']['confidence']:.2%}, "
        f"{result['spam']['confidence_level']})"
    )

    # IMAGE

    if result["image"]:

        image = result["image"]

        print(
            "\nCOMPUTER VISION - IMAGE"
        )

        print(
            f"People: "
            f"{image.get('people_count', 0)}"
        )

        print(
            f"Motorcycles: "
            f"{image.get('motorcycle_count', 0)}"
        )

        print(
            f"Vehicles: "
            f"{image.get('vehicle_count', 0)}"
        )

        print(
            f"Scene: "
            f"{image.get('scene_type', 'Unknown')}"
        )

        print(
            f"Quality: "
            f"{image.get('image_quality', 'Unknown')}"
        )

        print(
            f"Reliability: "
            f"{image.get('ai_reliability', 'Unknown')}"
        )

    # VIDEO

    if result["video"]:

        video = result["video"]

        print(
            "\nCOMPUTER VISION - VIDEO"
        )

        print(
            f"Frames: "
            f"{video['video']['processed_frames']}"
        )

        print(
            f"Duration: "
            f"{video['video']['duration_seconds']}s"
        )

        print(
            f"People: "
            f"{video.get('people_detected', 0)}"
        )

        print(
            f"Motorcycles: "
            f"{video.get('motorcycles_detected', 0)}"
        )

        print(
            f"Vehicles: "
            f"{video.get('vehicles_detected', 0)}"
        )

        print(
            f"Scene: "
            f"{video.get('scene_assessment', 'Unknown')}"
        )

        print(
            f"Quality: "
            f"{video.get('image_quality', 'Unknown')}"
        )

        print(
            f"Reliability: "
            f"{video.get('ai_reliability', 'Unknown')}"
        )

    # FUSION

    print("\nAI FUSION")

    print(
        f"People Estimated: "
        f"{evidence['people_estimated']}"
    )

    print(
        f"Vehicles: "
        f"{evidence['vehicle_count']}"
    )

    print(
        f"Motorcycles: "
        f"{evidence['motorcycle_count']}"
    )

    print(
        f"Overall Reliability: "
        f"{evidence['overall_reliability']:.0%}"
    )

    # RESOURCES

    print("\nRESOURCE PREDICTION")

    print(
        f"Ambulances: "
        f"{resources['ambulance']}"
    )

    print(
        f"Police Units: "
        f"{resources['police']}"
    )

    print(
        f"Fire Engines: "
        f"{resources['fire']}"
    )

    print(
        f"\nPriority Score: "
        f"{result['priority']}/100"
    )

    print(
        f"Primary Department: "
        f"{result['department']}"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    print(
        "\n======================================\n"
    )


if __name__ == "__main__":

    description = input(
        "Enter incident description: "
    ).strip()

    image_path = input(
        "Enter image path "
        "(press Enter to skip): "
    ).strip().strip('"') or None

    video_path = input(
        "Enter video path "
        "(press Enter to skip): "
    ).strip().strip('"') or None

    try:

        result = RescueAI().analyze_incident(
            description=description,
            image_path=image_path,
            video_path=video_path
        )

        print_result(result)

    except Exception as exc:

        print(
            f"\nAI analysis error: {exc}"
        )