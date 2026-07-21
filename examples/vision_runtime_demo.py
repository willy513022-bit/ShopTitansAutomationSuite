import cv2
import numpy as np

from vision.screen_detector import ScreenDetector
from vision.template_matcher import TemplateMatcher
from vision.vision_engine import VisionEngine


def build_template():
    template = np.zeros((24, 36, 3), dtype=np.uint8)
    cv2.rectangle(template, (3, 3), (32, 20), (255, 255, 255), -1)
    cv2.line(template, (3, 20), (32, 3), (0, 0, 0), 2)
    return template


template = build_template()
screen = np.zeros((140, 200, 3), dtype=np.uint8)
screen[60:84, 90:126] = template

detector = ScreenDetector(
    matcher=TemplateMatcher(threshold=0.90),
    templates={"disconnected": template},
)
engine = VisionEngine(detector=detector)
result = engine.analyze(screen)

print("Vision Runtime Demo")
print("screen_state =", result.screen_state.name)
print("confidence =", round(result.confidence, 4))
print("location =", result.detection.match.location if result.detection else None)
