import cv2

def find_template(image, template, threshold: float = 0.90):
    if image is None or template is None: return None
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, max_score, _, max_location = cv2.minMaxLoc(result)
    return None if max_score < threshold else (max_location, float(max_score))
