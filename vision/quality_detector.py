from dataclasses import dataclass
import cv2
import numpy as np
from models.quality import Quality
from vision.inventory_card_regions import CardRegion

@dataclass(frozen=True)
class QualityResult:
    quality:Quality; confidence:float; ratios:dict[str,float]

class QualityDetector:
    MIN_COLORED_RATIO=0.006
    def detect(self,image,name_region:CardRegion):
        h,w=image.shape[:2]; crop=image[max(0,name_region.y):min(h,name_region.y+name_region.height),max(0,name_region.x):min(w,name_region.x+name_region.width)].copy()
        if crop.size==0:return QualityResult(Quality.UNKNOWN,0.0,{})
        hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
        ranges={Quality.SUPERIOR:((35,80,80),(85,255,255)),Quality.FLAWLESS:((80,80,80),(105,255,255)),Quality.EPIC:((125,70,70),(165,255,255)),Quality.LEGENDARY:((15,90,100),(35,255,255))}
        masks={q:cv2.inRange(hsv,np.array(lo,dtype=np.uint8),np.array(hi,dtype=np.uint8)) for q,(lo,hi) in ranges.items()}
        pixels=max(1,crop.shape[0]*crop.shape[1]); ratios={q.value:float(np.count_nonzero(m))/pixels for q,m in masks.items()}; best=max(masks,key=lambda q:np.count_nonzero(masks[q])); ratio=ratios[best.value]
        if ratio<self.MIN_COLORED_RATIO:return QualityResult(Quality.NORMAL,1.0-min(1.0,ratio*20),ratios)
        return QualityResult(best,min(1.0,ratio/0.06),ratios)
