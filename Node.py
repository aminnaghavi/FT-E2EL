from Task import *
import math

class Node:
    def __init__(self,id=0,Treplicas=None) -> None:
        self.id=id
        if(Treplicas==None):
            self.Treplicas=[]
        else:
            self.Treplicas=Treplicas
        self.U=self.getU()

    def copy(self):
        cnode=Node(id=self.id)
        cnode.Treplicas=[]
        for Treplica in self.Treplicas:
            cnode.Treplicas.append(TaskReplica(Treplica.id,cnode,Treplica.task))
        return cnode

    def getU(self):
        U=0
        U=sum (Treplica.task.wcet/Treplica.task.period for Treplica in self.Treplicas)
        return U
    
    def mapTask(self,task,rep_id):
        if((task.wcet/task.period)+self.U>1):
            return False
        Treplica=TaskReplica(rep_id,self.id,task,task.wcet,task.bcet)
        self.Treplicas.append(Treplica)
        task.Treplicas.append(Treplica)
        self.U+=(task.wcet/task.period)
        return True

    def get_WCRT(self,Treplica):
        # U=sum(r.task.wcet/r.task.period for r in self.Treplicas)
        # if(U>1):
        #     return None
        WR=Treplica.task.wcet
        WR_prev=0
        HighPrioTasks=[r.task for r in self.Treplicas if r.task.priority<Treplica.task.priority]
        while(WR_prev!=WR):
            WR_prev=WR
            WR=Treplica.task.wcet+sum(math.ceil(WR/t.period)*t.wcet for t in HighPrioTasks)
        Treplica.WCRT=WR
        return Treplica.WCRT

    def get_BCRT(self,Treplica):
        BR=Treplica.task.bcet
        BR_prev=0
        HighPrioTasks=[r.task for r in self.Treplicas if r.task.priority<Treplica.task.priority]
        while(BR_prev!=BR):
            BR_prev=BR
            BR=Treplica.task.bcet+sum((math.ceil(BR/t.period)-1)*t.bcet for t in HighPrioTasks)
        Treplica.BCRT=BR

    def get_AllWCRT(self):
        for Treplica in self.Treplicas:
            self.get_WCRT(Treplica)

    def get_AllBCRT(self):
        for Treplica in self.Treplicas:
            self.get_BCRT(Treplica)