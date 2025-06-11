import math
import numpy as np

from scipy import signal
from sklearn.cluster import DBSCAN

import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.screenTracker.clusters import Clusters
from eyeGestures.screenTracker.heatmap import Heatmap

# THIS FILE IS SLOWLY BECOMING BLACK MAGIC

def detect_if_inside(point,rect):
    px = point[0]
    py = point[1]
    x,y,width,height = rect.getBoundaries() 

    x_in = x < px and px < x + width
    y_in = y < py and py < y + height
    
    return x_in and y_in

def detect_edges(roi, display, point_on_screen, point_on_display):
    """Function performing edge detection based on point, screen and display sizes"""
    (s_x,s_y) = point_on_screen 
    (d_x,d_y) = point_on_display

    x,y,width,height = roi.getBoundaries() 
    new_roi = dp.ScreenROI(x,y,width,height)

    # new_w = screen.width
    # margin = 5
    # TODO: fix this to estimate w and h
    if d_x <= 0 :
        new_roi.width = new_roi.width + abs(new_roi.x - s_x)
        new_roi.x = s_x

    if d_x >= display.width :
        new_roi.width = abs(new_roi.x - s_x)

    if d_y <= 0 :
        new_roi.height = new_roi.height + abs(new_roi.y - s_y)
        new_roi.y = s_y

    if d_y >= display.height :
        new_roi.height = abs(new_roi.y - s_y)

    return new_roi

def rescale_h(roi, scale_h, change = 0.5):
    """change size on height"""
    scale_diff_h = abs(1.0 - scale_h)

    ret_heigth  = roi.height

    if scale_diff_h > change: 
        ret_heigth = roi.height/1.0 * scale_h

    return ret_heigth

def rescale_w(roi, scale_w, change = 0.5):
    """change size on width"""
    scale_diff_w = abs(1.0 - scale_w)

    ret_width   = roi.width

    if scale_diff_w > change: 
        ret_width = roi.width/1.0 * scale_w

    return ret_width


def scaleDown(roi, edge, scale):
    """Function scalling down one roi till edges are met"""

    (_,_,cluster_w,cluster_h) = edge.getBoundaries()

    new_roi = dp.ScreenROI(roi.x,roi.y,roi.width,roi.height)
    if cluster_w < roi.width :
        new_scale_w = 1.0 + scale
        new_w = rescale_w(roi,new_scale_w,scale)
        new_roi.width = new_w

    if cluster_h < roi.height :
        new_scale_h = 1.0 + scale
        new_h = rescale_h(roi,new_scale_h,scale)
        new_roi.height = new_h

    return new_roi

def scaleUp(roi, roi2, scale):
    """Function scalling up one roi into another roi, second roi is for limiting scaling operation and scale is telling how much you can scale"""

    (_,_,roi2_w,roi2_h) = roi2.getBoundaries()

    new_roi = dp.ScreenROI(roi.x,roi.y,roi.width,roi.height)

    if roi2_w > roi.width :
        new_scale_w = 1.0 + scale
        new_w = rescale_w(roi,new_scale_w,scale)
        new_roi.width = new_w

    if roi2_h > roi.height :
        new_scale_h = 1.0 + scale
        new_h = rescale_h(roi,new_scale_h,scale)
        new_roi.height = new_h

    return new_roi


class ScreenProcessor:
    """Class for doing tracking and converting screen to display and display to screen"""

    def __init__(self):
        pass

    # RUN FEATURE
    def process(self,point,point_offset,buffor_length,roi,edges,screen,display,heatmap):
        """Function performing main processing for screen processor. Tons of parameters doing brrrr"""

        s_point_offset = self.display2screen(point_offset,screen,display)
        p_on_display = self.screen2display([point[0] + s_point_offset[0],point[1] + s_point_offset[1]],roi,display)
        # p_on_display = self.screen2display(point,roi,display)

        if buffor_length > 20:
            new_edges = detect_edges(roi, display, point, p_on_display)
            edges.x      = new_edges.x
            edges.y      = new_edges.y
            edges.width  = new_edges.width
            edges.height = new_edges.height

        p_on_display = (p_on_display[0] + display.offset_x, p_on_display[1] + display.offset_y)

        # return how close that is hist region
        (_,_,roi_w,roi_h) = heatmap.getBoundaries()
        closeness_percentage = (roi_w * roi_h)/(screen.width * screen.height)
        return (p_on_display,closeness_percentage)

    # CALIBRATION FEATURE
    # it should not affect objects but produce new ones
    def update(self, roi, edges, cluster, heatmap):
        """Function to update screen processor with new clusters and heatmaps"""

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
        """Function converting screen points to display points"""

        s_x,s_y = screen_point[0],screen_point[1]

        d_x = int((s_x - screen.x)/screen.width * display.width)
        d_y = int((s_y - screen.y)/screen.height * display.height)

        d_x = max(d_x,0)
        d_y = max(d_y,0)
        d_x = min(d_x,display.width)
        d_y = min(d_y,display.height)

        return (d_x,d_y)

    def display2screen(self, display_point, screen, display):
        """Function converting display points to screen points"""

        d_x,d_y = display_point[0],display_point[1]

        s_x = int((d_x)/display.width  * screen.width)
        s_y = int((d_y)/display.height * screen.height)


        return (s_x,s_y)

class ScreenManager:
    """Class performing most of tracking after estimating position of gaze"""

    def __init__(self,):
        self.screen_processor = ScreenProcessor()


    def process(self, buffor, roi, edges, screen, display, calibration, offset):
        """Function doing processing and tracking and calibration of tracker"""

        heatmap = Heatmap(screen.width,screen.height,buffor.getBuffor())
        cluster = Clusters(buffor.getBuffor()).getMainCluster()

        if cluster is not None:


            if calibration:
                roi = self.screen_processor.update(roi, edges, cluster, heatmap)

            p, percentage = self.screen_processor.process(
                buffor.getAvg(20),
                (offset[0],offset[1]),
                len(buffor.getBuffor()),
                roi,
                edges,
                screen,
                display,
                heatmap)

            return (p, roi, cluster)
        return ([0,0], roi, cluster)
