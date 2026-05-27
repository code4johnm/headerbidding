from __future__ import annotations

import os

from getSitesToVisit import GetSitesToVisit as GS
class Lancher:
    def __init__(self):
        pass
    def doABTraining(self):
        pass
    def doABTesting(self):
        pass
    def doMLTraining(self):
        config = self.getMLTrainingConfig()
        sites = GS()
        print(sites)
    def doMLTesting(self):
        pass
    
    def getABTrainingConfig(self):
        pass
    def getABTestingConfig(self):
        pass
    def getMLTrainingConfig(self):
        pass
    def getMLTestingConfig(self):
        pass
if __name__ == "__main__":

    a = Lancher()
    a.doMLTraining()