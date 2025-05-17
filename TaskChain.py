import random        
import math
import csv
class TaskChain:
    def __init__(self,TS) -> None:
        self.TS=TS
        self.TaskPred=[None for i in range(self.TS.tasknom)]
        self.TaskSucc=[None for i in range(self.TS.tasknom)]
        self.chain=[]
        self.num=0
    
    def makeChain(self,chaintask):
        self.chain=chaintask
        for i in range(1,len(chaintask)):
            self.TaskPred[chaintask[i].id]=chaintask[i-1].id

        for i in range(0,len(chaintask)-1):
            self.TaskSucc[chaintask[i].id]=chaintask[i+1].id
        self.ow=self.getObservationWindow()

    def makeRandomChains(self,length,type="Random",candidtaskIDs=None):
        if(candidtaskIDs!=None):
            tasks=[self.TS.tasks[i] for i in candidtaskIDs]
        else:
            tasks=self.TS.tasks
        if(type=="Random"):
            chaintasks = random.sample(tasks,k=length)
            self.makeChain(chaintasks)
        
        elif(type=="UnderSampling"):
            chaintasks = random.sample(tasks,k=length)
            sorted_chain = sorted(chaintasks, key=lambda task: task.period)
            self.makeChain(sorted_chain)

        elif(type=="OverSampling"):
            chaintasks = random.sample(tasks,k=length)
            sorted_chain = sorted(chaintasks, key=lambda task: task.period,reverse=True)
            self.makeChain(sorted_chain)


    def getMaxJobChainNom(self):
        jobcounts=self.ow/self.chain[0].period
        for i in range(1,len(self.chain)):
            jobcounts=jobcounts*math.ceil(self.chain[i-1].period/self.chain[i].period)
        return jobcounts

    def getObservationWindow(self):
        if(self.TS.hp==0):
            self.TS.getHP()
        maxageupperbound=0
        
        wcl = sum(2*task.period for task in self.chain)
        maxageupperbound=max(maxageupperbound,math.ceil(wcl/self.TS.hp)*self.TS.hp)
        # print("wcl:",maxageupperbound)
        self.ow=max(2*self.TS.hp,maxageupperbound)
        return self.ow
    
    def printChain(self):
        print([str(task) for task in self.chain])

    def printToFile(self,filename):
        f = open(filename, 'w')
        writer = csv.writer(f)
        writer.writerow(self.chain)
        f.close()