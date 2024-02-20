import screen_tracker.dataPoints

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
    
class gazeContext:

    def __init__(self,,):
        pass