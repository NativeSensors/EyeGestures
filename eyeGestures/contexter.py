
class Contexter:

    def __init__(self):
        self.context = dict()

    def add_context(self,context_id, object):
        if context_id not in self.context.keys(): 
            self.context[context_id] = object
            return True
        return False
    
    def rm_context(self,context_id):
        if context_id in self.context.keys(): 
            del self.context[context_id]
            return True
        return False
    
    def get_context(self,context_id,constructor):
        if context_id in self.context.keys(): 
            return self.context[context_id]
        self.add_context(context_id,constructor)
        return self.context[context_id]