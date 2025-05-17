from Job import *
from itertools import count
import numpy as np

class TaskReplica:
    def __init__(self,id,node,task,WCRT=0,BCRT=0) -> None:
        self.id=id
        self.BCRT=BCRT
        self.WCRT=WCRT
        self.node=node
        self.task=task
    def __str__(self):
        return str(self.task)+"rep_id: "+str(self.id)


class Task:
    def __init__(self,id,period,wcet,priority,phase=0,bcet=None,deadline=None,LastJobID=0) -> None:
        self.id=id
        self.period=period
        self.wcet=wcet
        self.bcet=bcet
        self.phase=phase
        self.Treplicas=[]
        self.priority=priority
        if deadline==None:
            self.deadline=period
        else:
            self.deadline=deadline
        self.LastJobID=LastJobID

    def getTreplica(self,nodeid):
        Treplica=next((Treplica for Treplica in self.Treplicas if Treplica.node==nodeid),None)
        return Treplica

    def __str__(self) -> str:
        return "tau"+str(self.id)+"("+"T="+str(self.period)+", D="+str(self.deadline)+", B="+str(self.bcet)+", C="+str(self.wcet)+", P="+str(self.priority)+")"
    
    def copy(self):
        newTask=Task(self.id,self.period,self.wcet,self.priority,self.phase,self.bcet,self.deadline,self.LastJobID)
        return newTask

