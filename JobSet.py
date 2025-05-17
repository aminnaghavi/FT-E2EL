import random
import math
from Job import *

class JobSet:
    def __init__(self,TS) -> None:
        self.TS=TS
        self.jobs=[[] for i in range(TS.tasknom)]

    def makeJobs(self, task, duration=None,prioritymethod="RM",AETmin=None,AETmax=None):
        jobnom=math.ceil((duration-task.phase)/task.period)
        for i in range(jobnom):
            if(prioritymethod=="RM"):
                priority=task.period
            elif(prioritymethod=="DM"):
                priority=task.deadline
            elif(prioritymethod=="EDF"):
                priority=task.phase+i*task.period+task.deadline

            self.jobs[task.id].append(Job(task,task.phase+i*task.period,id=i,AETmin=AETmin,AETmax=AETmax,priority=priority))
                

    def makeAllJobs(self, duration,prioritymethod="RM",AETmin=None,AETmax=None):
        for task in self.TS.tasks:
            self.makeJobs(task,duration,prioritymethod,AETmin,AETmax)