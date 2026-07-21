from dataclasses import dataclass
import cv2
import numpy as np

@dataclass(frozen=True)
class TierBadge:
    row:int; column:int; x:int; y:int; width:int; height:int; center_x:int; center_y:int

class TierBadgeDetector:
    COLUMN_COUNT=3; SEARCH_LEFT_OFFSET=4; SEARCH_RIGHT_OFFSET=58; MIN_RADIUS=13; MAX_RADIUS=24; MIN_CIRCLE_DISTANCE=100; ROW_Y_TOLERANCE=18
    def detect(self,image,content_left,content_top,content_right,content_bottom):
        content_width=content_right-content_left; column_width=content_width/self.COLUMN_COUNT; detected_by_column={}
        for column in range(self.COLUMN_COUNT):
            column_left=round(content_left+column_width*column); scan_left=max(content_left,column_left+self.SEARCH_LEFT_OFFSET); scan_right=min(content_right,column_left+self.SEARCH_RIGHT_OFFSET)
            roi=image[content_top:content_bottom,scan_left:scan_right]
            if roi.size==0: detected_by_column[column]=[]; continue
            gray=cv2.GaussianBlur(cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY),(7,7),1.5)
            circles=cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,dp=1.2,minDist=self.MIN_CIRCLE_DISTANCE,param1=100,param2=24,minRadius=self.MIN_RADIUS,maxRadius=self.MAX_RADIUS)
            candidates=[]
            if circles is not None:
                for cx,cy,r in np.round(circles[0]).astype(int): candidates.append((scan_left+cx,content_top+cy,r))
            candidates.sort(key=lambda c:c[1]); detected_by_column[column]=candidates
        return self._build_rows(detected_by_column)
    def _build_rows(self,detected_by_column):
        all_candidates=[]
        for column,circles in detected_by_column.items():
            for cx,cy,r in circles: all_candidates.append((column,cx,cy,r))
        all_candidates.sort(key=lambda i:i[2]); groups=[]
        for candidate in all_candidates:
            match=None
            for group in groups:
                avg=sum(i[2] for i in group)/len(group)
                if abs(candidate[2]-avg)<=self.ROW_Y_TOLERANCE: match=group; break
            (groups.append([candidate]) if match is None else match.append(candidate))
        valid=[g for g in groups if len({i[0] for i in g})>=2]; badges=[]
        for row_index,group in enumerate(valid):
            best={}
            for candidate in group: best.setdefault(candidate[0],candidate)
            for column,cx,cy,r in best.values(): badges.append(TierBadge(row_index,column,cx-r,cy-r,r*2,r*2,cx,cy))
        badges.sort(key=lambda b:(b.row,b.column)); return badges
