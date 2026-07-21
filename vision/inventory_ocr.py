import re
from dataclasses import dataclass
import cv2
from rapidocr_onnxruntime import RapidOCR
from vision.inventory_card_regions import CardRegion

@dataclass(frozen=True)
class OCRTextResult: text:str; confidence:float
@dataclass(frozen=True)
class InventoryOCRResult:
    name_raw:str; name_confidence:float; quantity_raw:str; quantity:int|None; quantity_confidence:float

class InventoryOCR:
    def __init__(self): print("正在載入 RapidOCR..."); self.engine=RapidOCR(); print("RapidOCR 載入完成")
    def read_card(self,image,name_region:CardRegion,quantity_region:CardRegion):
        nr=self._read_text(self._prepare_name_image(self._crop(image,name_region))); qr=self._read_text(self._prepare_quantity_image(self._crop(image,quantity_region)))
        return InventoryOCRResult(nr.text,nr.confidence,qr.text,self._parse_quantity(qr.text),qr.confidence)
    @staticmethod
    def _crop(image,region):
        h,w=image.shape[:2]; return image[max(0,region.y):min(h,region.y+region.height),max(0,region.x):min(w,region.x+region.width)].copy()
    @staticmethod
    def _prepare_name_image(image): return image if image.size==0 else cv2.resize(image,None,fx=3.0,fy=3.0,interpolation=cv2.INTER_CUBIC)
    @staticmethod
    def _prepare_quantity_image(image):
        if image.size==0:return image
        image=cv2.resize(image,None,fx=4.0,fy=4.0,interpolation=cv2.INTER_CUBIC); return cv2.equalizeHist(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY))
    def _read_text(self,image):
        if image is None or image.size==0:return OCRTextResult("",0.0)
        result,_=self.engine(image)
        if not result:return OCRTextResult("",0.0)
        texts=[]; conf=[]
        for item in result:
            if len(item)<3:continue
            text=str(item[1]).strip()
            if not text:continue
            try:c=float(item[2])
            except (TypeError,ValueError):c=0.0
            texts.append(text);conf.append(c)
        return OCRTextResult(" ".join(texts),sum(conf)/len(conf) if conf else 0.0) if texts else OCRTextResult("",0.0)
    @staticmethod
    def _parse_quantity(text):
        cleaned=text.replace("×","x").replace("X","x").replace(" ",""); m=re.search(r"x?(\d+)",cleaned); return int(m.group(1)) if m else None
