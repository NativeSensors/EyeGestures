import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.utils import Buffor
class Contexter:

    def __init__(self):
        self.context = dict()

    def addContext(self,context_id, object):
        if context_id not in self.context.keys(): 
            self.context[context_id] = object
            return True
        return False
    
    def rmContext(self,context_id):
        if context_id in self.context.keys(): 
            del self.context[context_id]
            return True
        return False
    
    def getContext(self,context_id):
        if context_id in self.context.keys(): 
            return self.context[context_id]
        return None
    
    def updateContext(self,context_id,data):
        if context_id in self.context.keys(): 
            self.context[context_id] = data
            return True
        self.add_context(context_id,data)
        return True
    
    def getNumberContextes(self):
        return len(self.context.keys())
    
class Gcontext:

    def __init__(self,
                 display,
                 roi,
                 edges,
                 cluster_boundaries,
                 gazeBuffor,
                 l_pupil,
                 r_pupil):
        
        self.roi = roi
        self.edges = edges
        self.cluster_boundaries = cluster_boundaries
        self.gazeBuffor = gazeBuffor
        self.l_pupil = l_pupil
        self.r_pupil = r_pupil
        self.display = display

class GazeContext:

    def __init__(self):
        self.contexter = Contexter()
        pass

    def get(self,
                id,
                display,
                roi = dp.ScreenROI(225,225,5,20),
                edges = dp.ScreenROI(225,225,20,20),
                cluster_boundaries = dp.ScreenROI(225,225,20,20),
                buffor  = Buffor(500),
                l_pupil = Buffor(20),
                r_pupil = Buffor(20)):

        context = Gcontext(display,
                           roi,
                           edges,
                           cluster_boundaries,
                           buffor,
                           l_pupil,
                           r_pupil)

        if self.contexter.addContext(id,context):
            return context
        else:
            return self.contexter.getContext(id)
        
    def update(self,
                id,
                context):
        
        self.contexter.updateContext(id,context)