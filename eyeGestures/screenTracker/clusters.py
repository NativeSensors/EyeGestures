from sklearn.cluster import DBSCAN
import numpy as np

class Cluster:
    """Class representing one ROI cluster"""

    def __init__(self, label, points):
        
        self.label    = label
        self.points   = np.array(points)
        self.weight   = len(self.points)
        self.__centroid = self.centroid(points)

        x,y,w,h = self.boundaries(points)

        self.x =  x
        self.y =  y
        self.w =  w
        self.h =  h

    def centroid(self,points):
        """Function calculating and returning center of ROI"""
        
        x,y,w,h = self.boundaries(points)

        c_x, c_y = (x+w/2,y+h/2)

        x,y = sum(points)/len(points)

        c_x, c_y = (c_x + x)/2, (c_y + y)/2
        return (c_x, c_y)

    def boundaries(self,points):
        """Function calculating and returning boundaries of cluster"""

        x = np.min(points[:,0]) 
        width = abs(np.max(points[:,0]) - x) 

        y = np.min(points[:,1]) 
        height = abs(np.max(points[:,1]) - y) 

        return (x,y,width,height)
    
    def getBoundaries(self):
        """Function returning boundaries of cluster"""
        return (self.x,self.y,self.w,self.h)
    
    def getCenter(self):
        """Function returning center of ROI"""
        return (self.__centroid)
    
class Clusters:
    """Algorithm dividing tracked points into clusters so it can be estimated were is center of ROI"""

    def __init__(self,buffer):
        buffer = np.array(buffer)
        
        self.head = len(buffer) - 1
        self.main_cluster = None
        self.clusters = []

        dbScan     = DBSCAN(eps=12, min_samples=3)
        clustering = dbScan.fit(buffer)

        labels = clustering.labels_
        unique_labels = set(labels) - {-1}

        for u_label in unique_labels:
            core_sample_indices = clustering.core_sample_indices_
            cluster_points = buffer[core_sample_indices][labels[clustering.core_sample_indices_] == u_label]
            self.clusters.append(Cluster(u_label,cluster_points))

        # return sorted(self.clusters, key=lambda cluster: cluster.weight)[-1]
        if len(self.clusters) > 0:
            self.main_cluster = self.clusters[
                    labels[self.head]
                ]
        else:
            self.main_cluster = None

    def clearPoints(self):
        """[Possibly dead code] Function reseting cluster"""
        self.head = 0

    def getClusters(self):
        """Function returning all clusters"""
        return self.clusters
    
    def getMainCluster(self):
        """Function returning main clusters"""
        return self.main_cluster
