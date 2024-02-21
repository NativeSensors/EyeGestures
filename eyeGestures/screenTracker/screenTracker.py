import math
import numpy as np

from scipy import signal
from sklearn.cluster import DBSCAN

import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.screenTracker.clusters import Clusters
from eyeGestures.screenTracker.heatmap import Heatmap

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

    new_h = screen.height
    if(d_y <= 0 or d_y >= display.height):
        new_h = abs(screen.getCenter().y - s_y) * 1 + margin
        
        if screen.height < new_h:
            pass
        else:
            new_h = screen.height
    
    return (new_w,new_h) 

def rescale_h(roi, scale_h, change = 0.5):
    scale_diff_h = abs(1.0 - scale_h)
    
    ret_heigth  = roi.height
    
    if scale_diff_h > change: 
        ret_heigth = roi.height/1.0 * scale_h

    return ret_heigth
    
def rescale_w(roi, scale_w, change = 0.5):
    scale_diff_w = abs(1.0 - scale_w)
    
    ret_width   = roi.width

    if scale_diff_w > change: 
        ret_width = roi.width/1.0 * scale_w

    return ret_width


def scaleDown(roi, edge, scale):
    
    (_,_,cluster_w,cluster_h) = edge.getBoundaries()

    new_roi = dp.ScreenROI(roi.x,roi.y,roi.width,roi.height)
    if(cluster_w < roi.width):
        new_scale_w = 1.0 + scale
        new_w = rescale_w(roi,new_scale_w,scale)
        new_roi.width = new_w
    
    if(cluster_h < roi.height):
        new_scale_h = 1.0 + scale
        new_h = rescale_h(roi,new_scale_h,scale)
        new_roi.height = new_h

    return new_roi

def scaleUp(roi, roi2, scale):
    
    (_,_,roi2_w,roi2_h) = roi2.getBoundaries()

    new_roi = dp.ScreenROI(roi.x,roi.y,roi.width,roi.height)

    if(roi2_w > roi.width):
        new_scale_w = 1.0 + scale
        new_w = rescale_w(roi,new_scale_w,scale)
        new_roi.width = new_w
       
    if(roi2_h > roi.height):
        new_scale_h = 1.0 + scale
        new_h = rescale_h(roi,new_scale_h,scale)
        new_roi.height = new_h

    return new_roi


class ScreenProcessor:

    def __init__(self):
        pass

    # RUN FEATURE
    def process(self,point,buffor_length,roi,edges,screen,display,heatmap):
        
        p_on_display = self.screen2display(point,roi,display)
        
        if buffor_length > 20:
            new_screen_w,new_screen_h = detect_edges(roi, display, point, p_on_display)
            edges.width = new_screen_w
            edges.height = new_screen_h
        
        p_on_display = (p_on_display[0] + display.offset_x, p_on_display[1] + display.offset_y)
        
        # return how close that is hist region
        (_,_,roi_w,roi_h) = heatmap.getBoundaries()
        closeness_percentage = (roi_w * roi_h)/(screen.width * screen.height)
        return (p_on_display,closeness_percentage)

    # CALIBRATION FEATURE
    # it should not affect objects but produce new ones
    def update(self, roi, edges, cluster, heatmap):

        (x,y) = heatmap.getCenter()
        # =====================================
        # ---------histogram obtained---------- 
        # =====================================
        new_roi = dp.ScreenROI(roi.x,roi.y,roi.width,roi.height)
        new_roi.setCenter(x,y)
        edges.setCenter(x,y)
        # self.eyeScreen.setCenter(x,y) 
        new_roi = scaleUp(new_roi, edges, scale = 0.1)

        # =====================================
        # if screen is bigger than edges make it smaller
        # =====================================
        new_roi = scaleDown(new_roi, cluster, scale = -0.1)
        return new_roi
        
    
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
   

    def process(self, buffor, roi, edges, screen, display, calibration):

        heatmap = Heatmap(screen.width,screen.height,buffor.getBuffor())
        cluster = Clusters(buffor.getBuffor()).getMainCluster()

        if cluster is not None:

            if calibration:
                roi = self.screen_processor.update(roi, edges, cluster, heatmap)
   
            p, percentage = self.screen_processor.process(
                buffor.getAvg(20),
                len(buffor.getBuffor()),
                roi,
                edges,
                screen,
                display,
                heatmap)
               
            print(p,percentage)
            return (p, roi, cluster)
        return ([0,0], roi, cluster)
