from asyncio import tasks
import math
from Task import *
from drs import *
import numpy as np
from functools import reduce
import csv
import random

class TaskSet:
    def __init__(self,tasks=[],scheduler='FP') -> None:
        self.tasks=tasks
        self.tasknom=len(tasks)
        if(tasks!=[]):
            self.U = self.getU()
            self.hp=self.getHP()
        else:
            self.U=0
            self.hp=0

    def getHP(self):
        lcm=1
        for task in self.tasks:
            lcm = lcm*task.period//math.gcd(lcm,task.period)
        self.hp=lcm
        return lcm
    
    def getU(self):
        self.U=sum (task.wcet/task.period for task in self.tasks)
        return self.U

    def generateSyntheticTasks(self,n,Ubound,priorities='RM',Tset=[1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 1000000],periods_nom=None,Tmin=None,Tmax=None,Tstep=None,bcetratio=0.2,implicit=True,UmaxArray=None,UminArray=None,UtilMinGranularity=None,UtilMaxGranularity=None,Regulator=1,wcetmin=1,wcetmax=np.inf) -> None:
        
        self.tasks=[]
        self.tasknom=n
        if(Tset!=None):
            periods = random.choices(Tset,k=n)
        else:
            if(periods_nom!=None):
                Tset=random.sample(self.TS.tasks,k=periods_nom)
            r=np.random.uniform(low=np.log(Tmin), high=np.log(Tmax+Tstep), size=n)
            periods = np.floor(np.exp(r)/Tstep)*Tstep

        if priorities=='Dynamic':
            priorities=[None]*n
        else:
            if priorities=='Random':
                random.shuffle(periods)
            elif priorities=='RM':
                periods=np.sort(periods)
            else:
                raise Exception('priorities')
            priorities=range(0,n)

        if UmaxArray!=None and UminArray!=None:
            utilizations = drs(n=n, sumu=Ubound,upper_constraints=UmaxArray,lower_constraints=UminArray)
        elif(UmaxArray!=None):
            utilizations = drs(n=n, sumu=Ubound,upper_constraints=UmaxArray)
        elif(UmaxArray!=None):
            utilizations = drs(n=n, sumu=Ubound,lower_constraints=UminArray)
        elif(UtilMinGranularity!=None):
            UminArray=[]
            UmaxArray=[]
            for period in periods:
                UminArray.append(max(wcetmin/period,(Ubound/n)/UtilMinGranularity))
                UmaxArray.append(min(wcetmax/period,(Ubound/n)*UtilMaxGranularity))
            utilizations = drs(n=n,sumu=Ubound,lower_constraints=UminArray,upper_constraints=UmaxArray)
        else:
            utilizations = drs(n=n,sumu=Ubound)

        for util in utilizations:
            if(util<=0):
                # print("ERROR NEGATIVE UTILIZATION")
                return None

        self.U=0
        for i in range(0,n):
            period=int(periods[i]*Regulator)
            wcet = max(int(utilizations[i]*period),1) #max(round(utilizations[i]*period),1)
            bcet = max(1,int(bcetratio*wcet)) #max(1,round(bcetratio*wcet))
            self.U+=wcet/period
            # if(self.U>Ubound):
            #     print("couldn't make feasible tasks!","U: ", self.U)
            self.tasks.append(Task(
                period=period,
                wcet = wcet,
                bcet = bcet,
                priority=priorities[i],
                id=i,
            ))
        self.hp=self.getHP()


    def adjustPeriods(self,primes=[2,3,5],implicit=True):
        maxperiod = max(self.tasks,key=lambda x:x.period).period
        # print("maxperiod:"+str(maxperiod))
        maxcloseperiod = np.inf
        # print(maxperiod)
        maxexps=[]
        allperiods=[]
        val=1
        for prime in primes:
            maxexps.append(math.ceil(math.log(maxperiod,prime)))
        # print(maxexps)
        exps=[0]*len(primes)
        dig=0
        while(1):
            val=1
            # print(exps)
            for i in range(len(primes)):
                val=val*(primes[i]**exps[i])
            if(val<maxcloseperiod):
                allperiods.append(val)
                if(val>maxperiod):
                    maxcloseperiod=val
            exps[0]+=1
            dig=0
            while(val>=maxcloseperiod):
                exps[dig]=0
                dig+=1
                if(dig<len(primes)):
                    exps[dig]+=1
                else:
                    break
                val=1
                for i in range(len(primes)):
                    val=val*(primes[i]**exps[i])
            if(dig>=len(primes)):
                break     
            while(exps[dig]>=maxexps[dig]):
                exps[dig]=0
                dig+=1
                if(dig<len(primes)):
                    exps[dig]+=1
                else:
                    break
            if(dig>=len(primes)):
                break
        allperiods.sort()

        for i in range(len(self.tasks)):
            j=0
            while allperiods[j]<=self.tasks[i].period:
                j+=1
            self.tasks[i].period=allperiods[j]
            if(implicit==True):
                self.tasks[i].deadline=self.tasks[i].period
        # self.getHP()
        # print(allperiods)


    def printToFile(self,filename):
        titles=["id","period","deadline","wcet","bcet","priority"]
        f = open(filename, 'w')
        writer = csv.writer(f)
        # write the header
        writer.writerow(titles)
        # write the data
        for task in self.tasks:
            values=[task.id, task.period, task.deadline, task.wcet, task.bcet, task.priority]
            writer.writerow(values)
        f.close()

    def __str__(self) -> str:
        msg="TaskSet = {"
        for tau in self.tasks:
            msg += (tau.__str__() + ", ")
        msg+="}"
        return msg 
    
    def addTask(self,task):
        self.tasks.append(task)
        self.tasknom+=1
        self.getHP()

    def copy(self):
        newTS=TaskSet([task.copy() for task in self.tasks])
        newTS.tasknom=self.tasknom
        newTS.U=self.U
        newTS.hp=self.hp
        return newTS