import eyeGestures.screenTracker.dataPoints as dp
from eyeGestures.utils import Buffor
class Contexter:

    def __init__(self):
        self.context = dict()

    def addContext(self, context_id, object):
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
                r_pupil,
                l_eye_buff,
                r_eye_buff,
                calibration):
        
        self.roi = roi
        self.edges = edges
        self.cluster_boundaries = cluster_boundaries
        self.gazeBuffor = gazeBuffor
        self.l_pupil = l_pupil
        self.r_pupil = r_pupil
        self.l_eye_buff = l_eye_buff
        self.r_eye_buff = r_eye_buff
        self.display = display
        self.calibration = calibration

class GazeContext:

    def __init__(self):
        self.contexter = Contexter()
        pass

    def get(self,
            id,
            display,
            roi = dp.ScreenROI(285,105,80,15),
            edges = dp.ScreenROI(285,105,80,15),
            cluster_boundaries = dp.ScreenROI(225,125,20,20),
            buffor  = Buffor(200),
            l_pupil = Buffor(20),
            r_pupil = Buffor(20),
            l_eye_buff = Buffor(20),
            r_eye_buff = Buffor(20),
            calibration = False):

        context = Gcontext(display,
                           roi,
                           edges,
                           cluster_boundaries,
                           buffor,
                           l_pupil,
                           r_pupil,
                           l_eye_buff,
                           r_eye_buff,
                           calibration)

        if self.contexter.addContext(id,context):
            return context
        else:
            return self.contexter.getContext(id)
        
    def update(self,
                id,
                context):
        
        self.contexter.updateContext(id,context)