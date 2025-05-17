import numpy as np
import random

class JobReplica():
    def __init__(self,job,Treplica,AETmin=None,AETmax=None) -> None:
        self.job=job
        self.node=Treplica.node
        self.Treplica=Treplica
        self.read_start=0
        self.read_end=0
        self.data_start=0
        self.data_end=0
        if(AETmin!=None):
            self.AET=random.randint(AETmin, min(AETmax,self.job.task.wcet))
        else:
            self.AET=self.job.task.wcet


        
class Job:
    # def actualExe(self,wcet) -> int:
    #     return np.random.randint(1,self.wcet)
    def __init__(self,task,release,id=-1,AETmin=None,AETmax=None,priority=None) -> None:
        self.task=task
        self.Jreplicas=[JobReplica(self,task.Treplicas[i],AETmin,AETmax) for i in range(len(task.Treplicas))]
        if(id!=-1):
            self.jobID=id
        else:
            self.jobID=self.task.LastJobID
            self.task.LastJobID+=1
        
        self.release=release
        self.deadline=self.release+self.task.deadline
        if(priority==None):
            if (self.task.priority!=0):
                self.priority=self.task.priority
            else:
                self.priority=self.deadline #for EDF
        else:
            self.priority=priority

    def getJreplica(self,nodeid):
        Jreplica=next((Jreplica for Jreplica in self.Jreplicas if Jreplica.node==nodeid),None)
        return Jreplica
    
    def __str__(self) -> str:
        return "Job"+str(self.task.id)+","+str(self.jobID)+"(R="+str(self.release)+", D="+str(self.deadline)+", B="+str(self.task.bcet)+", C="+str(self.task.wcet)+", P="+str(self.priority)+")"