import math
import numpy as np

from eyeGestures.utils import Buffor

from scipy import signal
from sklearn.cluster import DBSCAN

class Cluster:

    def __init__(self, label, points):
        
        self.label    = label
        self.points   = np.array(points)
        self.weight   = len(self.points)
        self.centroid = self.centroid(points)

        x,y,w,h = self.boundaries(points)

        self.x =  x
        self.y =  y
        self.w =  w
        self.h =  h
        pass

    def centroid(self,points):
        x,y,w,h = self.boundaries(points)

        c_x, c_y = (x+w/2,y+h/2)

        x,y = sum(points)/len(points)

        c_x, c_y = (c_x + x)/2, (c_y + y)/2
        return (c_x, c_y)


    def boundaries(self,points):

        x = np.min(points[:,0]) 
        width = abs(np.max(points[:,0]) - x) 

        y = np.min(points[:,1]) 
        height = abs(np.max(points[:,1]) - y) 

        return (x,y,width,height)
    
    def getPoints(self):
        return self.points

    def getBoundaries(self):
        return (self.x,self.y,self.w,self.h)
    
    def getCenter(self):
        return (self.centroid)
    
class ScreenClusters:

    def __init__(self):

        self.filled = 0
        self.head = 0
        self.size = 500
        self.points = np.zeros((self.size,2), dtype=np.uint32)
        self.Dbscan = DBSCAN(eps=12, min_samples=4)
        self.main_cluster = None
        # self.clusters = dict()
        pass

    def addPoint(self,point):
        self.clusters = []
        
        index = self.head 
        self.points[index] = point
        
        self.head = (self.head + 1) % self.size
        self.filled += 1
        self.filled = min(self.filled,self.size)

        clustering  = self.Dbscan.fit(self.points[:self.filled])

        labels = clustering.labels_
        unique_labels = set(labels) - {-1}

        for u_label in unique_labels:

            cluster_points = self.points[:self.filled][clustering.core_sample_indices_][labels[clustering.core_sample_indices_] == u_label]
            self.clusters.append(Cluster(u_label,cluster_points))

        # return sorted(self.clusters, key=lambda cluster: cluster.weight)[-1]
        self.main_cluster = self.clusters[labels[index]]
        return self.clusters[labels[index]]
    
    def clearPoints(self):
        self.head = 0

    def getClusters(self):
        return self.clusters
    
    def getMainCluster(self):
        return self.main_cluster

class ScreenHist:

    def __init__(self,width,height,step):
        self.inc_step = 10

        self.step = step
        self.width = width
        self.height = height

        bars_x = int(self.width/self.step)
        bars_y = int(self.height/self.step)

        self.axis_x = np.zeros((bars_x))
        self.axis_y = np.zeros((bars_y))

        self.confidence_limit   = 1000
        self.total_points       = 0

        self.fading = 1

    def __getParam(self,param,last : bool = False):
        ret = 0
        retArray = np.where(param)
        
        if len(retArray[0]) > 0:
            ret = retArray[0][- int(last)] * self.step

            if not ret == np.NAN:
                ret = int(ret)
        
        return ret
        
    def addPoint(self,point):
        self.total_points += 1
        
        self.axis_x[self.axis_x > 0] -= self.fading
        self.axis_y[self.axis_y > 0] -= self.fading
        self.axis_x[self.axis_x < 0] = 0
        self.axis_y[self.axis_y < 0] = 0
        
        (x,y) = point
        pos_x = int(x/self.step)
        pos_y = int(y/self.step)
        
        self.axis_x[pos_x] += self.inc_step
        self.axis_y[pos_y] += self.inc_step

        self.min_x = self.__getParam((self.axis_x > self.inc_step*4),last=False)
        self.max_x = self.__getParam((self.axis_x > self.inc_step*4),last=True)
        self.min_y = self.__getParam((self.axis_y > self.inc_step*4),last=False)
        self.max_y = self.__getParam((self.axis_y > self.inc_step*4),last=True)

    def setFading(self,fading : int):
        self.fading = fading

    def getBoundaries(self):
        x = self.min_x
        y = self.min_y
        w = self.max_x - self.min_x
        h = self.max_y - self.min_y 
        return (x,y,w,h)

    def getCenter(self):
        self.center_x = int((self.max_x - self.min_x)/2 + self.min_x)
        self.center_y = int((self.max_y - self.min_y)/2 + self.min_y)
        return (self.center_x,self.center_y)
    
    def getPeak(self):
        x = int(np.argmax(self.axis_x)*self.inc_step)
        y = int(np.argmax(self.axis_y)*self.inc_step)
        return (x,y)

    def confident(self):
        return self.total_points > self.confidence_limit

    def getHist(self):
        return (self.axis_x/self.inc_step,self.axis_y/self.inc_step)

class Screen:

    def __init__(self, screen_width = 0, screen_height = 0, x = 0, y = 0, width = 0, height = 0):
        self.old_scale_w = 1.0
        self.old_scale_h = 1.0

        self.screen_buffor = Buffor(15)
        self.setWH(width,height)
        self.setCenter(x,y)

        self.screen_width  = screen_width
        self.screen_height = screen_height
        pass

    def getCenter(self):
        return (self.x,self.y)

    def setWH(self, width, height):
        self.width  = width
        self.height = height

    def getWH(self):
        return (int(self.width),int(self.height))

    def setCenter(self, x, y):
        self.x = x - int(self.width/2)
        self.y = y - int(self.height/2)

    def scale(self,scale_w,scale_h, change = 0.5):
        
        diff_w = abs(self.old_scale_w - scale_w)
        diff_h = abs(self.old_scale_h - scale_h)
        
        if diff_w > change: 
            new_width  = self.width/self.old_scale_w * scale_w
            self.old_scale_w = scale_w
            self.setWH(new_width,self.height)
        
        if diff_h > change: 
            new_height = self.height/self.old_scale_h * scale_h
            self.old_scale_h = scale_h
            self.setWH(self.width,new_height)    

    def poinstInScreen(self,points):

        filling = 0.0
        for point in points:
            isX = False
            isY = False

            half_width = self.width/2
            half_height = self.height/2

            if (self.x - half_width) <= point[0] and point[0] <= (self.x + half_width):
                isX = True

            if (self.y - half_height) <= point[1] and point[1] <= (self.y + half_height):
                isY = True

            if isX * isY: 
                filling += 1

        print(filling, len(points))
        return filling/len(points)

    def scaleByStep(self,step_w=0.1,step_h=0.1):
        self.old_scale_w = 1.0
        self.old_scale_h = 1.0
        new_scale_w = float(self.old_scale_w + step_w)
        new_scale_h = float(self.old_scale_h + step_h)
        self.scale(new_scale_w,new_scale_h,0)

    def convertToScreen(self, point):
        x = (point[0] - self.x) * ((point[0] - self.x) > 0)
        x = int((x/self.width) * self.screen_width)

        y = (point[1] - self.y) * ((point[1] - self.y) > 0)
        y = int((y/self.height) * self.screen_height)

        x = max(x,0)
        y = max(y,0)
        x = min(x,self.screen_width)
        y = min(y,self.screen_height)

        self.screen_buffor.add((x,y))
        return self.screen_buffor.getAvg()
    
    def limitToScreen(self, point):
        margin = 10
        x = max(int(self.x - margin),int(point[0]))
        y = max(int(self.y - margin),int(point[1]))
        
        x = min(int(self.x + self.width  + margin),x)
        y = min(int(self.y + self.height + margin),y)

        return (x,y)

    def getRect(self):
        return (int(self.x),int(self.y),int(self.width),int(self.height))

class EdgeDetector:

    def __init__(self,width,height, x = 0,y = 0,w = 50,h = 50):

        self.width  = width
        self.height = height
        
        self.w = w
        self.h = h
        self.center_x = x + w/2
        self.center_y = y + h/2

        self.edge_max_x = int(self.center_x + w/2)
        self.edge_min_x = int(self.center_x - w/2)
        self.edge_max_y = int(self.center_y + h/2)
        self.edge_min_y = int(self.center_y - h/2)

        self.locked = False

    def setCenter(self,x,y):
        self.center_x = x 
        self.center_y = y

    def setLim(self,lim_min_x, lim_max_x, lim_min_y, lim_max_y):

        self.lim_max_x = lim_max_x
        self.lim_min_x = lim_min_x 
        self.lim_max_y = lim_max_y
        self.lim_min_y = lim_min_y 

    # BUG: for some reason looking left side of screen is shrinking screen but right side is enlarging it
    # Need investigation 
    def check(self, point_tracker, point_screen):
        (x_t,y_t) = point_tracker 
        (x_s,y_s) = point_screen

        # TODO: fix this to estimate w and h
        if(x_s <= 0 or x_s >= self.width):
            new_w = abs(self.center_x - x_t)           
            self.w = new_w
                

        if(y_s <= 0 or y_s >= self.height):
            new_h = abs(self.center_y - y_t)
            self.h = new_h
            
    def getBoundingBox(self):
        x = int(self.center_x - self.w/2)
        y = int(self.center_y - self.h/2)
        
        return (x,y,int(self.w),int(self.h))

    def getCenter(self):    
        return (self.center_x, self.center_y)

class ScreenProcessor:

    def __init__(self,eye_screen_w,eye_screen_h,
                 monitor_width,monitor_height,
                 x = 250, y = 250,
                 w = 50, h = 50,
                 monitor_offset_x = 0,
                 monitor_offset_y = 0):
        
        self.init_w = w 
        self.init_h = h
        
        self.monitor_width    = monitor_width
        self.monitor_height   = monitor_height
        self.monitor_offset_x = monitor_offset_x
        self.monitor_offset_y = monitor_offset_y

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h
        self.eyeScreen    = Screen(self.monitor_width,
                                   self.monitor_height,
                                   x,y,
                                   w,h)

        self.edgeDetector = EdgeDetector(self.monitor_width,
                                         self.monitor_height,
                                         x,y,
                                         w,h)
        self.pointsBuffor  = Buffor(50)
        self.limsWHBuffor  = Buffor(20)
        self.edgesWHBuffor = Buffor(20)
        
        self.scaling = True

    def process(self,point,getBoundaries):
        (roi_x,roi_y,roi_w,roi_h) = getBoundaries()
        w_screen,h_screen = self.eyeScreen.getWH()


        point = self.eyeScreen.limitToScreen(point)
        p = self.eyeScreen.convertToScreen(point)
        
        self.pointsBuffor.add(point)
        if self.pointsBuffor.getLen() > 20:
            self.edgeDetector.check(point,p)

        p += (self.monitor_offset_x, self.monitor_offset_y)

        # return how close that is hist region
        # closeness_percentage = (roi_w * roi_h)/(w_screen * h_screen)
        # return (p,closeness_percentage)
        return p
    
    def poinstInScreen(self,points):
        return self.eyeScreen.poinstInScreen(points)

    def update(self,center,getBoundaries):

        (x,y) = center
        (roi_x,roi_y,roi_w,roi_h) = getBoundaries()

        # =====================================
        # ---------histogram obtained---------- 
        # =====================================

        self.eyeScreen.setCenter(x,y) 
        w_screen,h_screen = self.eyeScreen.getWH()
        self.__scale_up_to_hist(w_screen, h_screen, getBoundaries)

        # =====================================
        # if screen is bigger than edges make it smaller
        # =====================================
        
        self.edgeDetector.setCenter(x,y)
        self.__scale_down_to_edge(w_screen,h_screen)
        self.edgeDetector.setLim(x,y,x + roi_w,y + roi_h)

    def __scale_up_to_hist(self, width, height, boundaries):
        (_,_,cluster_w,cluster_h) = boundaries()

        self.limsWHBuffor.add((cluster_w,cluster_h))
        (cluster_w,cluster_h) = self.limsWHBuffor.getAvg()
        self.eyeScreen.getWH()

        if(cluster_w > width):
            self.eyeScreen.scaleByStep(0.1,0.0)
        
        if(cluster_h > height):
            self.eyeScreen.scaleByStep(0.0,0.1)


    def __scale_down_to_edge(self,width,height):
        print
        _,_,w,h = self.edgeDetector.getBoundingBox()
        
        self.edgesWHBuffor.add((w,h))
        (w,h) = self.edgesWHBuffor.getAvg()

        if (w < width):
            self.eyeScreen.scaleByStep(-0.1,0.0)
        
        if (h < height):
            self.eyeScreen.scaleByStep(0.0,-0.1)

    def getScreen(self):
        return self.eyeScreen

    def getPointsHistory(self):
        return self.pointsBuffor.getBuffor()

    def getEdgeDetector(self):
        return self.edgeDetector


class ScreenManager:

    def __init__(self,monitor_width,monitor_height,
                 eye_screen_w,eye_screen_h,
                 monitor_offset_x = 0,
                 monitor_offset_y = 0):

        self.offset_x = 0
        self.offset_y = 0

        self.frame_counter = 0
        self.starting_frame = 20

        self.monitor_width  = monitor_width
        self.monitor_height = monitor_height
        self.monitor_offset_x = monitor_offset_x
        self.monitor_offset_y = monitor_offset_y

        self.eye_screen_w = eye_screen_w
        self.eye_screen_h = eye_screen_h
        self.step         = 10 

        self.eyeClusters = ScreenClusters()
        self.eyeHist     = ScreenHist(self.eye_screen_w,
                                      self.eye_screen_h,
                                      self.step)
        
        self.screen_processor = ScreenProcessor(
                                        self.eye_screen_w,
                                        self.eye_screen_h,
                                        self.monitor_width,
                                        self.monitor_height,
                                        monitor_offset_x = monitor_offset_x,
                                        monitor_offset_y = monitor_offset_y)
        
        self.backup_processor = ScreenProcessor(
                                            self.monitor_width,
                                            self.monitor_height,
                                            self.eye_screen_w,
                                            self.eye_screen_h,
                                            monitor_offset_x = monitor_offset_x,
                                            monitor_offset_y = monitor_offset_y)

        self.pointsBuffor  = Buffor(50)

        self.calibration_freeze = False
        self.back_up_counter = 0

    def push_window(self,x,y):
        print(f"pushing window: {x,y}")
        self.offset_x = x
        self.offset_y = y

    def freeze_calibration(self):
        self.calibration_freeze = True

    def unfreeze_calibration(self):
        self.calibration_freeze = False

    def process(self, point : (int,int)):
        assert(np.array(point).shape[0] == 2)

        self.frame_counter+=1 
        if self.frame_counter < self.starting_frame:
            return [int(self.eye_screen_w/2),int(self.eye_screen_h/2)]

        if not self.calibration_freeze:
            cluster = self.eyeClusters.addPoint(point)
            self.eyeHist.addPoint(point)
        else: 
            cluster = self.eyeClusters.getMainCluster()

        if cluster is not None:
            x,y = cluster.getCenter()
            center = (x + self.offset_x,y + self.offset_y)

            if not self.calibration_freeze:
                self.screen_processor.update(center,self.eyeHist.getBoundaries)
                self.backup_processor.update(center,self.eyeHist.getBoundaries)

            p        = self.screen_processor.process(point,self.eyeHist.getBoundaries)
            p_backup = self.backup_processor.process(point,self.eyeHist.getBoundaries)
            
            percentage_backup = self.backup_processor.poinstInScreen(cluster.getPoints())
            percentage_main   = self.screen_processor.poinstInScreen(cluster.getPoints())

            self.back_up_counter += 1
            if((percentage_backup > percentage_main) and
                        not self.calibration_freeze):
                print(percentage_backup,percentage_main, percentage_backup > percentage_main)

                p = p_backup
                self.screen_processor = self.backup_processor
                if self.screen_processor > 0.2:
                    self.calibration_freeze = True
                    print("calibration stopped from inside")

            if self.back_up_counter > 100:
                self.back_up_counter = 0 
                _,_,w,h = cluster.getBoundaries()
                self.backup_processor = ScreenProcessor(
                                            self.eye_screen_w,
                                            self.eye_screen_h,
                                            self.monitor_width,
                                            self.monitor_height,
                                            x,y,
                                            w,h,
                                            monitor_offset_x = self.monitor_offset_x,
                                            monitor_offset_y = self.monitor_offset_y)

            return p
        return [int(self.eye_screen_w/2),int(self.eye_screen_h/2)]

    def getScreen(self):
        return self.screen_processor.getScreen()

    def getScreenBackup(self):
        return self.backup_processor.getScreen()

    # def getHist(self):
    #     return self.cluster

    def getClusters(self):
        return self.eyeClusters.getClusters()
    
    def getPointsHistory(self):
        return self.screen_processor.getPointsHistory()

    def getEdgeDetector(self):
        return self.screen_processor.getEdgeDetector()