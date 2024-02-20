import math
import numpy as np

from scipy import signal
from sklearn.cluster import DBSCAN

from clusters import Clusters

# THIS FILE IS SLOWLY BECOMING BLACK MAGIC

def detect_edges(screen, display, point_on_screen, point_on_display):
    (s_x,s_y) = point_on_screen 
    (d_x,d_y) = point_on_display

    new_w = screen.width
    margin = 5
    # TODO: fix this to estimate w and h
    if(d_x <= 0 or d_x >= display.width):
        new_w = abs(screen.getCenter().x - s_x) * 1 + margin
        
        if screen.width < new_w:
            pass
        else:
            new_w = screen.width

    new_h = screen.width
    if(d_y <= 0 or d_y >= display.height):
        new_h = abs(screen.getCenter().y - s_y) * 1 + margin
        
        if screen.height < new_h:
            pass
        else:
            new_h = screen.width
    
    return (new_w,new_h) 


class ScreenProcessor:

    def __init__(self):
        self.eyeScreen = Screen()   

    # RUN FEATURE
    def process(self,point,buffor_length,roi,screen,display,heatmap):
        
        p_on_display = self.eyeScreen.screen2display(point,roi,display)
        
        if buffor_length > 20:
            new_screen_w,new_screen_h = detect_edges(display, point, p_on_display)
            screen.width = new_screen_w
            screen.height = new_screen_h
        
        p_on_display += (display.offset_x, display.offset_y)

        # return how close that is hist region
        (_,_,roi_w,roi_h) = heatmap.getBoundaries()
        closeness_percentage = (roi_w * roi_h)/(screen.width * screen.height)
        return (p_on_display,closeness_percentage)

    # CALIBRATION FEATURE
    def update(self, roi, screen, clusters, heatmap):

        (x,y) = heatmap.getCenter()
        # =====================================
        # ---------histogram obtained---------- 
        # =====================================

        screen.getCenter().x = x
        screen.getCenter().y = y
        # self.eyeScreen.setCenter(x,y) 
        self.__scale_up_to_cluster(roi, clusters)
        

    def __scale_up_to_cluster(self, roi, clusters):
        
        (_,_,cluster_w,cluster_h) = clusters.getMainCluster().getBoundaries()

        if(cluster_w > roi.width):
            self.eyeScreen.scaleByStep(roi,0.1,0.0)
        
        if(cluster_h > roi.height):
            self.eyeScreen.scaleByStep(roi,0.0,0.1)


class Screen:

    def __init__(self):
        pass

    def scale(self, roi, scale_w, scale_h, change = 0.5):
        
        scale_diff_w = abs(roi.scale_w - scale_w)
        scale_diff_h = abs(roi.scale_h - scale_h)
        
        if scale_diff_w > change: 
            roi.scale_w = scale_w
            roi.width = roi.width/roi.scale_w * scale_w
        
        if scale_diff_h > change: 
            roi.scale_h = scale_h
            roi.heigth = roi.heigth/roi.scale_h * scale_h
        
    def scaleByStep(self, roi, step_w=0.1, step_h=0.1):
        roi.scale_w = 1.0
        roi.scale_h = 1.0
        new_scale_w = float(roi.scale_w + step_w)
        new_scale_h = float(roi.scale_h + step_h)
        self.scale(roi, new_scale_w, new_scale_h, 0.0)

    def screen2display(self, screen_point, screen, display):
        s_x,s_y = screen_point[0],screen_point[1]

        d_x = int((s_x - screen.x)/screen.width * display.width)
        d_y = int((s_y - screen.y)/screen.height * display.height)

        d_x = max(d_x,0)
        d_y = max(d_y,0)
        d_x = min(d_x,display.width)
        d_y = min(d_y,display.height)

        return (d_x,d_y)


class ScreenManager:

    def __init__(self,):     
        self.screen_processor = ScreenProcessor()
   

    def process(self, buffor, roi, screen, display, heatmap, calibration):

        cluster = Clusters(buffor).getMainCluster()
        if cluster is not None:

            if calibration:
                self.screen_processor.update(roi, screen, cluster, heatmap)
   
            p, _ = self.screen_processor.process(
                buffor[len(buffor)-1],
                len(buffor),
                roi,
                screen,
                display,
                heatmap)
   
            return p
        return [0,0]
