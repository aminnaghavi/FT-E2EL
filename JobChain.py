import math
from JobSet import *
import signal
import csv
from concurrent.futures import ThreadPoolExecutor, TimeoutError


# class ReplicaBundle:
#     def __init__(self,Jreplicas) -> None:
#         self.Jreplicas=Jreplicas
#         for Jreplica in Jreplicas:
#             # self.read_start=min(Jreplicas,key=lambda rep:rep.read_start).read_start
#             self.read_end=max(Jreplicas,key=lambda rep:rep.read_end).read_end
#             self.data_start=sorted(Jreplicas, key=lambda rep: rep.data_start)[math.floor(len(Jreplicas)/2)].data_start #floor: because it starts from zero
#             self.data_end=max(Jreplicas,key=lambda rep:rep.data_end).data_end

class JobChainSet:
    def __init__(self,TS,ComBCET=0,ComWCET=0,TChain=None,JS=None) -> None:
        self.TS=TS 
        self.TChain=TChain
        self.chains=[]
        self.ComBCET=ComBCET
        self.ComWCET=ComWCET
        if(JS==None):
            if(TChain!=None):
                self.getObservationWindow()
            self.JS=JobSet(self.TS)
            self.JS.makeAllJobs(2*self.TS.hp)
        else:
            self.JS=JS

    def setTaskChain(self,TChain):
        self.TChain=TChain

    
    def getReplicaDataIntervals(self,Jreplica):
        D_low=Jreplica.job.release+Jreplica.Treplica.BCRT
        D_high=Jreplica.job.release+Jreplica.job.task.period+Jreplica.Treplica.WCRT
        return D_low,D_high

    def getReplicaReadIntervals(self,Jreplica):
        R_low=Jreplica.job.release
        R_high=Jreplica.job.release+Jreplica.Treplica.WCRT-Jreplica.job.task.wcet
        return R_low,R_high

    def getAllReadIntervals(self):
        for i in range(len(self.JS.jobs)):
            for job in self.JS.jobs[i]:
                for replica in job.Jreplicas:
                    replica.read_start,replica.read_end=self.getReplicaReadIntervals(replica)
                

    def getAllDataIntervals(self):
        for i in range(len(self.JS.jobs)):
            for job in self.JS.jobs[i]:
                for replica in job.Jreplicas:
                    replica.data_start,replica.data_end=self.getReplicaDataIntervals(replica)


    def createPossibleChains(self,faultmodel="Fault"):
        jobchains={(job,) for job in self.JS.jobs[self.TChain.chain[0].id]}
        self.jobchains={}
        taskchain=self.TChain.chain
        for succtask in taskchain[1:]:
            tempbchain=jobchains.copy()
            jobchains=set()
            for jchain in tempbchain:
                job=jchain[-1]
                for succjob in self.JS.jobs[succtask.id]:
                    nomorejob=False
                    for succrep in succjob.Jreplicas:
                        rep=job.getJreplica(succrep.node)
                        nomorejob=False
                        if(rep!=None):
                            if(not(rep.data_start>succrep.read_end or rep.data_end<succrep.read_start)):
                                jobchains.add(jchain+(succjob,))
                            if(rep.data_end<succrep.read_start):
                                nomorejob=True
                        else:
                            f=math.floor(len(succjob.Jreplicas)/2)
                            if(f!=0):
                                vdata_start=sorted([rep.data_start for rep in job.Jreplicas])[f+1]
                                if(faultmodel=="NoFault"):
                                    vdata_end=sorted([rep.data_end for rep in job.Jreplicas],reverse=True)[f+1]
                                elif(faultmodel=="Fault"):
                                    vdata_end=max([rep.data_end for rep in job.Jreplicas])
                                else:
                                    raise Exception("Fault model does not exist!")
                            else:
                                vdata_start=job.Jreplicas[0].data_start
                                vdata_end=job.Jreplicas[0].data_end
                            vdata_start+=self.ComBCET #Adding communication delay
                            vdata_end+=self.ComWCET #Adding communication delay
                            if(not(vdata_start>succrep.read_end or vdata_end<succrep.read_start)):
                                jobchains.add(jchain+(succjob,))
                                self.jobchains=jobchains
                            vread_max_start=succrep.read_start#This is correct because the read start doesn't change for different replicas of the same reading job.
                            if(vdata_end<vread_max_start):
                                nomorejob=True
                    if(nomorejob==True):#This is correct because the read start doesn't change for different replicas of the same reading job.
                        break
        return jobchains


    def createPossibleChainsTimeout(self,timeout=60,faultmodel="Fault"):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.createPossibleChains,faultmodel)
            try:
                self.chains = future.result(timeout=timeout)  # Wait for the result or timeout
                return True
            except TimeoutError:
                print("Function execution timed out!")
                print("Number of job chains so far: ", len(self.jobchains))
                return False

    # def createPossibleChains(self,taskchain): 
    #     jobchains=[[job] for job in self.JS.jobs[taskchain[0].id]]
    #     for taskchainid in range(0,len(taskchain)-1):
    #         tempchain=jobchains.copy()
    #         # taskid=taskchain[taskchainid].id
    #         succtaskid=taskchain[taskchainid+1].id
    #         jobchains=[]
    #         for chain in tempchain:
    #             jobid=chain[-1].jobID
    #             for succjobid in range(len(self.JS.jobs[succtaskid])):
    #                 if(self.DataIntervals[taskid][jobid][1]<self.ReadIntervals[succtaskid][succjobid][0]):
    #                     break
    #                 if(not(self.DataIntervals[taskid][jobid][0]>self.ReadIntervals[succtaskid][succjobid][1] or self.DataIntervals[taskid][jobid][1]<self.ReadIntervals[succtaskid][succjobid][0])):
    #                     jobchains.append(chain+[self.JS.jobs[succtaskid][succjobid]])
    #     return jobchains

    # def createAllPossibleChains(self):
    #     self.getAllDataIntervals()
    #     self.getAllReadIntervals()
    #     for taskchainid in range(len(self.TChains.chains)):
    #         self.chains.append(self.createPossibleChains(taskchainid))
            
                
    def printChain(self,number=None):
        iter=0
        for jchain in self.chains:
            if(number==None or iter<number):
                print([str(job) for job in jchain])
                iter+=1
            else:
                break

    def getE2ELatency(self,chain):
        firstjob=chain[0].Jreplicas[0].job
        lastjob=chain[-1].Jreplicas[0].job
        max_replica_wcrt=max(lastjob.Jreplicas,key=lambda rep:rep.Treplica.WCRT).Treplica.WCRT
        e2e=lastjob.release + max_replica_wcrt - firstjob.release
        return e2e

    def getMaxEndtoEndLatency(self):
        maxe2e=0
        for chain in self.chains:
            maxe2e=max(maxe2e,self.getE2ELatency(chain))
        return maxe2e


                    
    def getChainNom(self):
        return len(self.chains)
    
    def printToFile(self,filename):
        titles=["T"+str(task.id) for task in self.TChain.chain]
        f = open(filename, 'w')
        writer = csv.writer(f)
        # write the header
        writer.writerow(titles)
        # write the data
        for chain in self.chains:
            values=[job.jobID for job in chain]
            writer.writerow(values)
        f.close()