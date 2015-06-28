class Pool:
    def __init__(self,**kwargs):
        self.factor_date=kwargs.get('factor_date')
        self.cpn=kwargs.get('cpn')
        self.cbal=kwargs.get('cbal')
        self.wac=kwargs.get('wac')
        self.wam=kwargs.get('wam')
        self.wala=kwargs.get('wala')
        
    

    def mprint(self):
        for attr, value in self.__dict__.iteritems():
            print attr, value

            
class FixedRatePool(Pool):
    def __init__(self,**kwargs):
        Pool.__init__(self,**kwargs)
        self.type='FIX'
        
class ArmRatePool(Pool):
    def __init__(self,**kwargs):
        Pool.__init__(self,**kwargs)
        self.lookback=45
        self.type='ARM'
        self.index_name=kwargs.get('index_name')
        if 'lookback' in kwargs:
            self.lookback=kwargs.get('lookback')
            
        
        
# free function instead of staticmethod of Pool class
# unless I have better reason to do so

def makePool(**kwargs):
    if 'lookback' in kwargs:
        return ArmRatePool(**kwargs)
    else:
        return FixedRatePool(**kwargs)
    
    
