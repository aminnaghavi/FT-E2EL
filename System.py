from TaskSet import *
from Node import *

class System:
    def __init__(self,TS,nodenom=1,repnom=1,TChains=None) -> None:
        self.nodenom=nodenom
        self.nodes=[Node(i) for i in range(nodenom)]
        self.repnom=repnom
        self.TS=TS
        self.TChains=TChains
        if (TChains!=None):
            self.allchaintasks = [self.TS.tasks[id] for id in set(task.id for sublist in self.TChains for task in sublist.chain)]
            self.allfreetasks = [self.TS.tasks[id] for id in set(task.id for task in self.TS.tasks)-set(task.id for task in self.allchaintasks)]
        else:
            self.allchaintasks = None
            self.allfreetasks = None

    def mapTaskReplicasWorstFit(self,task):
        task=self.TS.tasks[task.id]
        if(len(task.Treplicas)>0):
            return True
        candidnodesid=list(range(self.nodenom))
        for rep_id in range(self.repnom):
            targetnodes=[self.nodes[i] for i in candidnodesid]
            targetnodeid = min(targetnodes, key=lambda node: node.U).id
            successful=self.nodes[targetnodeid].mapTask(task,rep_id)
            if(successful==False):
                return False
            candidnodesid.remove(targetnodeid)
        return True
    
    def mapTaskReplicasBestFit(self,task):
        task=self.TS.tasks[task.id]
        if(len(task.Treplicas)>0):
            return True
        candidnodesid=list(range(self.nodenom))
        for rep_id in range(self.repnom):
            successful=False
            while(len(candidnodesid)>0 and not successful):
                targetnodes=[self.nodes[i] for i in candidnodesid]
                targetnodeid = max(targetnodes, key=lambda node: node.U).id
                nodeutil=self.nodes[targetnodeid].U
                taskutil=task.wcet/task.period
                
                if(taskutil+nodeutil<=1 and self.checkSchedulabilityAfterReplicaMapping(self.nodes[targetnodeid],task)):
                    successful=self.nodes[targetnodeid].mapTask(task,rep_id)

                candidnodesid.remove(targetnodeid)

            if(successful==False):
                return False
        
        return True
    
    
    def mapTaskReplicasMinimizingCommunication(self,task,deptask):
        task=self.TS.tasks[task.id]
        if(len(task.Treplicas)>0):
            return True
        candidnodesid=list(range(self.nodenom))
        for rep_id in range(self.repnom):
            # print("rep_id",rep_id)
            # print("pos",pos)
            
            targetnodeid=deptask.Treplicas[rep_id].node
            nodeutil=self.nodes[targetnodeid].U
            taskutil=task.wcet/task.period
            if(not(taskutil+nodeutil<1 and targetnodeid in candidnodesid)):#If doesn't fit assign it to the node with the highest utilization
                targetnodes=[self.nodes[i] for i in candidnodesid]
                targetnodeid = min(targetnodes, key=lambda node: node.U).id
            successful=self.nodes[targetnodeid].mapTask(task,rep_id)
            if(successful==False):
                return False
            candidnodesid.remove(targetnodeid)
        
        return True
    
    def mapTaskReplicasMinimizingWCRT(self,task):
        task=self.TS.tasks[task.id]
        if(len(task.Treplicas)>0):
            return True
        candidnodesid=list(range(self.nodenom))
        WCRTs=[]
        for node in self.nodes:
            tempnode=node.copy()
            Treplica=TaskReplica(0,tempnode,task)
            tempnode.Treplicas.append(Treplica)
            WCRTs.append(tempnode.get_WCRT(Treplica))
        bestnodes_ids=np.argsort(WCRTs)    
            
        for rep_id in range(self.repnom):
            # print("rep_id",rep_id)
            # print("pos",pos)
            targetnodeid=self.nodes[bestnodes_ids[rep_id]].id
            nodeutil=self.nodes[targetnodeid].U
            taskutil=task.wcet/task.period
            if(not(taskutil+nodeutil<1 and targetnodeid in candidnodesid)):#If doesn't fit assign it to the node with the highest utilization
                targetnodes=[self.nodes[i] for i in candidnodesid]
                targetnodeid = min(targetnodes, key=lambda node: node.U).id
            successful=self.nodes[targetnodeid].mapTask(task,rep_id)
            if(successful==False):
                return False
            candidnodesid.remove(targetnodeid)
        
        return True
    

    def mapTaskReplicasKeepSumWCRT(self,task,taskchain):
        task=self.TS.tasks[task.id]
        if(len(task.Treplicas)>0):
            return True
        nodecurrentwcrt=[0]*self.nodenom
        for node in self.nodes:
            # print(node.U)
            for treplica in node.Treplicas:
                if(treplica.task.id in [task.id for task in taskchain]):
                    nodecurrentwcrt[node.id]+=node.get_WCRT(treplica)

        nodewcrt=[0]*self.nodenom
        for node in self.nodes:
            if(node.U+task.wcet/task.period>1):
                nodewcrt[node.id]=np.inf
                continue
            tempnode=node.copy()
            newTreplica=TaskReplica(0,tempnode,task)
            tempnode.Treplicas.append(newTreplica)
               
            for treplica in tempnode.Treplicas:
                # if(tempnode.get_WCRT(treplica)>treplica.task.deadline):
                #     nodewcrt[node.id]=np.inf
                #     break
                if(treplica.task.id in [task.id for task in taskchain]):
                    nodewcrt[node.id]+=tempnode.get_WCRT(treplica)
        
        
        differences=[nodewcrt[i]-nodecurrentwcrt[i] for i in range(self.nodenom)]
        # print(differences)
        bestnodes_ids=np.argsort(differences)    

        for rep_id in range(self.repnom):
            # print("rep_id",rep_id)
            # print("pos",pos)
            targetnodeid=self.nodes[bestnodes_ids[rep_id]].id
            nodeutil=self.nodes[targetnodeid].U
            taskutil=task.wcet/task.period
            if(not(taskutil+nodeutil<1)):#If it doesn't fit it meas already its wcrt difference is infinity
                return False
            self.nodes[targetnodeid].mapTask(task,rep_id)
        return True
    
    def fakeReplicaMapImproveSumWCRT(self,nodes,task,taskchain):
        task=self.TS.tasks[task.id]

        nodecurrentwcrt=[0]*self.nodenom
        for node in nodes:
            # print(node.U)
            for treplica in node.Treplicas:
                if(treplica.task.id in [task.id for task in taskchain]):
                    nodecurrentwcrt[node.id]+=node.get_WCRT(treplica)

        for nodeid in range(self.nodenom):
            nodes[nodeid].Treplicas = [treplica for treplica in nodes[nodeid].Treplicas if treplica.task.id != task.id]

        candidnodesid=list(range(self.nodenom))
        nodewcrt=[0]*self.nodenom
        for node in nodes:
            if(node.U+task.wcet/task.period>1):
                nodewcrt[node.id]=np.inf
                continue
            tempnode=node.copy()
            newTreplica=TaskReplica(0,tempnode,task)
            tempnode.Treplicas.append(newTreplica)
               
            for treplica in tempnode.Treplicas:
                # if(tempnode.get_WCRT(treplica)>treplica.task.deadline):
                #     nodewcrt[node.id]=np.inf
                #     break
                if(treplica.task.id in [task.id for task in taskchain]):
                    nodewcrt[node.id]+=tempnode.get_WCRT(treplica)
        
        
        differences=[nodewcrt[i]-nodecurrentwcrt[i] for i in range(self.nodenom)]
        # print(differences)
        bestnodes_ids=np.argsort(differences)    

        for rep_id in range(self.repnom):
            # print("rep_id",rep_id)
            # print("pos",pos)
            targetnodeid=nodes[bestnodes_ids[rep_id]].id
            nodeutil=nodes[targetnodeid].U
            taskutil=task.wcet/task.period
            if(not(taskutil+nodeutil<1 and targetnodeid in candidnodesid)):#If doesn't fit assign it to the node with the highest utilization
                targetnodes=[nodes[i] for i in candidnodesid]
                targetnodeid = min(targetnodes, key=lambda node: node.U).id
                if(taskutil+nodes[targetnodeid].U>1):
                    return False, nodes
            Treplica=TaskReplica(rep_id,nodes[targetnodeid],task)
            nodes[targetnodeid].Treplicas.append(Treplica)
            nodes[targetnodeid].U+=(task.wcet/task.period)
            candidnodesid.remove(targetnodeid)
        return True,nodes
    
    def fakeReplicaMapImproveWCRT(self,nodes,task):
        task=self.TS.tasks[task.id]
        for nodeid in range(self.nodenom):
            nodes[nodeid].Treplicas = [treplica for treplica in nodes[nodeid].Treplicas if treplica.task.id != task.id]

        candidnodesid=list(range(self.nodenom))
        WCRTs=[0]*self.nodenom
        for node in nodes:
            if(node.U+task.wcet/task.period>1):
                WCRTs[node.id]=np.inf
                continue
            tempnode=node.copy()
            Treplica=TaskReplica(0,tempnode,task)
            tempnode.Treplicas.append(Treplica)
            WCRTs[node.id]=tempnode.get_WCRT(Treplica)
        bestnodes_ids=np.argsort(WCRTs)    

        for rep_id in range(self.repnom):
            # print("rep_id",rep_id)
            # print("pos",pos)
            targetnodeid=nodes[bestnodes_ids[rep_id]].id
            nodeutil=nodes[targetnodeid].U
            taskutil=task.wcet/task.period
            if(not(taskutil+nodeutil<1 and targetnodeid in candidnodesid)):#If doesn't fit assign it to the node with the highest utilization
                targetnodes=[nodes[i] for i in candidnodesid]
                targetnodeid = min(targetnodes, key=lambda node: node.U).id
                if(taskutil+self.nodes[targetnodeid].U>1):
                    return False, nodes
            Treplica=TaskReplica(rep_id,nodes[targetnodeid],task)
            nodes[targetnodeid].Treplicas.append(Treplica)
            nodes[targetnodeid].U+=(task.wcet/task.period)
            candidnodesid.remove(targetnodeid)
        return True,nodes


    def mapAllTasks(self,MappingMethod="WF",LargestFirst=True):
        sorted_tasks=sorted(self.TS.tasks, key=lambda task: (task.wcet/task.period), reverse=LargestFirst)
        for task in sorted_tasks:
            if(MappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False
        # Priority sorted
        # for node in self.nodes:
        #     node.Treplicas = sorted(node.Treplicas, key=lambda Treplica: Treplica.task.priority)
        return True

    def mapSelectedTasks(self,selectedtasks,MappingMethod="WF",SortingBasis="Period",DescendingOrder=True):
        if(SortingBasis=="Utilization"):
            sorted_tasks=sorted(selectedtasks, key=lambda task: (task.wcet/task.period), reverse=DescendingOrder)
        elif(SortingBasis=="Period"):
            sorted_tasks=sorted(selectedtasks, key=lambda task: task.period, reverse=DescendingOrder)
        for task in sorted_tasks:
            if(MappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(MappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            elif(MappingMethod=="BF"):
                successful=self.mapTaskReplicasBestFit(task)
            elif(MappingMethod=="WF"):
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False    
        return True
    
    def fakeMapTasksWFD(self,nodes,tasks):
        sorted_tasks=sorted(tasks, key=lambda task: (task.wcet/task.period), reverse=True)
        mapped_tasks=set()
        for node_id in range(self.nodenom):
            nodes[node_id].U=sum(rep.task.wcet/rep.task.period for rep in nodes[node_id].Treplicas)
            mapped_tasks.add(task.id for task in nodes[node_id].Treplicas)

        for task in sorted_tasks:
            if(task.id in mapped_tasks):
                continue
            task=self.TS.tasks[task.id]
            candidnodesid=list(range(self.nodenom))
            for rep_id in range(self.repnom):
                targetnodes=[nodes[i] for i in candidnodesid]
                targetnodeid = min(targetnodes, key=lambda node: node.U).id
                nodeutil=nodes[targetnodeid].U
                taskutil=task.wcet/task.period
                if(taskutil+nodeutil>1):
                    return False, nodes
                Treplica=TaskReplica(rep_id,nodes[targetnodeid],task)
                nodes[targetnodeid].Treplicas.append(Treplica)
                nodes[targetnodeid].U+=task.wcet/task.period
                mapped_tasks.add(task.id)
                candidnodesid.remove(targetnodeid)
                
        return True, nodes
    
    def fakeMapTasksWFD(self,nodes,tasks):
        sorted_tasks=sorted(tasks, key=lambda task: (task.wcet/task.period), reverse=True)
        mapped_tasks=set()
        for node_id in range(self.nodenom):
            nodes[node_id].U=sum(rep.task.wcet/rep.task.period for rep in nodes[node_id].Treplicas)
            mapped_tasks.add(task.id for task in nodes[node_id].Treplicas)

        for task in sorted_tasks:
            if(task.id in mapped_tasks):
                continue
            task=self.TS.tasks[task.id]
            candidnodesid=list(range(self.nodenom))
            for rep_id in range(self.repnom):
                targetnodes=[nodes[i] for i in candidnodesid]
                targetnodeid = min(targetnodes, key=lambda node: node.U).id
                nodeutil=nodes[targetnodeid].U
                taskutil=task.wcet/task.period
                if(taskutil+nodeutil>1):
                    return False, nodes
                Treplica=TaskReplica(rep_id,nodes[targetnodeid],task)
                nodes[targetnodeid].Treplicas.append(Treplica)
                nodes[targetnodeid].U+=task.wcet/task.period
                mapped_tasks.add(task.id)
                candidnodesid.remove(targetnodeid)
                
        return True, nodes
    
    def mapTasksKeepWCRTofOtherTasks(self,taskstomap,taskstomaintain, SortingBasis="Utilization", DescendingOrder= True):
        if(SortingBasis=="Utilization"):
            sorted_tasks=sorted(taskstomap, key=lambda task: (task.wcet/task.period), reverse=DescendingOrder)
        elif(SortingBasis=="Period"):
            sorted_tasks=sorted(taskstomap, key=lambda task: task.period, reverse=DescendingOrder)
        
        # longest_chain_tasks = max(taskchains, key=lambda tc: len(tc.chain)).chain
        for task in sorted_tasks:
            successful=self.mapTaskReplicasKeepSumWCRT(task,taskstomaintain)
            if(successful==False):
                return False
        return True


    def mapWFDFirstThenMoveTasks(self,SortingBasis="Period",DescendingOrder=False):
        tempnodes=[Node(i) for i in range(self.nodenom)]
        successful, tempnodes=self.fakeMapTasksWFD(tempnodes,self.TS.tasks)
        if(successful==False):
            return False
        
        if(SortingBasis=="Utilization"):
            sorted_tasks=sorted(self.allfreetasks, key=lambda task: (task.wcet/task.period), reverse=DescendingOrder)
        elif(SortingBasis=="Period"):
            sorted_tasks=sorted(self.allfreetasks, key=lambda task: task.period, reverse=DescendingOrder)
        # longest_chain_tasks = max(self.TChains, key=lambda tc: len(tc.chain)).chain
        for task in sorted_tasks:
            successful, tempnodes=self.fakeMapImproveSumWCRT(tempnodes,task,self.allchaintasks)
            if(successful==False):
                return False
        for nodeid in range(self.nodenom):
            for taskreplica in tempnodes[nodeid].Treplicas:
                self.nodes[nodeid].mapTask(taskreplica.task,taskreplica.id)
        return True
    
    def mapWFDFirstThenImproveChainTaskWCRTLater(self,SortingBasis="Period",DescendingOrder=False):
        tempnodes=[Node(i) for i in range(self.nodenom)]
        successful, tempnodes=self.fakeMapTasksWFD(tempnodes,self.TS.tasks)
        if(successful==False):
            return False

        if(SortingBasis=="Utilization"):
            sorted_tasks=sorted(self.allchaintasks, key=lambda task: (task.wcet/task.period), reverse=DescendingOrder)
        elif(SortingBasis=="Period"):
            sorted_tasks=sorted(self.allchaintasks, key=lambda task: task.period, reverse=DescendingOrder)
        for task in sorted_tasks:
            successful, tempnodes=self.fakeMapImproveWCRT(tempnodes,task)
            if(successful==False):
                return False
        for nodeid in range(self.nodenom):
            for taskreplica in tempnodes[nodeid].Treplicas:
                self.nodes[nodeid].mapTask(taskreplica.task,taskreplica.id)
        return True
    

    
    def mapChainTasksTogether(self,ChainMappingMethod="WF",ChainSortingBasis="Utilization", ChainDescendingOrder=True,MapFreeTasksFirst=False, freeTasksMapping="KeepChainWCRT",freeSortingBasis="Utilization", freeDescendingOrder=True):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            if (successful==False):
                return False

        successful=self.mapSelectedTasks(self.allchaintasks,MappingMethod=ChainMappingMethod,SortingBasis=ChainSortingBasis,DescendingOrder=ChainDescendingOrder)
        if(successful==False):
            return False

        if(not MapFreeTasksFirst):
            if(freeTasksMapping=="KeepChainWCRT"):
                return self.mapTasksKeepWCRTofOtherTasks(self.allfreetasks,self.allchaintasks,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            else:
                return self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
    
        
                
    def mapChainAwareRoot2Leaf(self,ChainMappingMethod="WF",ChainDesendingLength=True,MapFreeTasksFirst=False,freeTasksMapping="WF", freeSortingBasis="Utilization",freeDescendingOrder=True):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            if(successful==False):
                return False
        sorted_taskchain = sorted(self.TChains, key=lambda x: len(x.chain),reverse=ChainDesendingLength)
        for taskchain in sorted_taskchain:
            task=self.TS.tasks[taskchain.chain[0].id]
            if(ChainMappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(ChainMappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False
            
        # maxlength=max([len(taskchain.chain) for taskchain in sorted_taskchain])
        if(ChainDesendingLength==False):
            maxlength=len(sorted_taskchain[-1].chain)
        else:
            maxlength=len(sorted_taskchain[0].chain)

        for pos in range(1,maxlength):
            for taskchain in sorted_taskchain:
                if(pos>=len(taskchain.chain)):
                    continue
                task=self.TS.tasks[taskchain.chain[pos].id]
                prectask=self.TS.tasks[taskchain.chain[pos-1].id]
                if(ChainMappingMethod=="WCRT"):
                    successful=self.mapTaskReplicasMinimizingWCRT(task)
                elif(ChainMappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
                elif(ChainMappingMethod=="Communication"):
                    successful=self.mapTaskReplicasMinimizingCommunication(task,prectask)
                else:
                    successful=self.mapTaskReplicasWorstFit(task)
                     
                if(successful==False):
                    return False
        
        if(not MapFreeTasksFirst):
            if(freeTasksMapping=="KeepChainWCRT"):
                return self.mapTasksKeepWCRTofOtherTasks(self.allfreetasks,self.allchaintasks,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            else:
                return self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)


    def mapChainRoot2LeafTaskBased(self,ChainMappingMethod="WF",ChainSortingBasis="Utilization",ChainDescendingOrder=True,MapFreeTasksFirst=False,freeTasksMapping="WF", freeSortingBasis="Utilization",freeDescendingOrder=True):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            if(successful==False):
                return False
        
        maxlength=max([len(taskchain.chain) for taskchain in self.TChains])

        for pos in range(maxlength):
            filtered_chains=[x for x in self.TChains if len(x.chain) > pos]
            if(ChainSortingBasis=="Utilization"):
                sorted_chain_tasks = [x.chain[pos] for x in sorted(filtered_chains, key=lambda x: x.chain[pos].wcet / x.chain[pos].period, reverse=ChainDescendingOrder)]
            elif(ChainSortingBasis=="Period"):
                sorted_chain_tasks = [x.chain[pos] for x in sorted(filtered_chains, key=lambda x: x.chain[pos].period, reverse=ChainDescendingOrder)]
            
            for task in sorted_chain_tasks:
                if(ChainMappingMethod=="WCRT"):
                    successful=self.mapTaskReplicasMinimizingWCRT(task)
                elif(ChainMappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
                else:
                    successful=self.mapTaskReplicasWorstFit(task)
                     
                if(successful==False):
                    return False

        if(not MapFreeTasksFirst):     
            if(freeTasksMapping=="KeepChainWCRT"):
                return self.mapTasksKeepWCRTofOtherTasks(self.allfreetasks,self.allchaintasks,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            else:
                return self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            

    def mapChainLeaf2RootTaskBased(self,ChainMappingMethod="WF",ChainSortingBasis="Utilization",ChainDescendingOrder=True,MapFreeTasksFirst=False,freeTasksMapping="WF", freeSortingBasis="Utilization",freeDescendingOrder=True):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            if(successful==False):
                return False
        
        maxlength=max([len(taskchain.chain) for taskchain in self.TChains])

        for pos in range(maxlength):
            filtered_chains=[x for x in self.TChains if len(x.chain) > pos]
            
            if(ChainSortingBasis=="Utilization"):
                sorted_chain_tasks = [x.chain[-pos-1] for x in sorted(filtered_chains, key=lambda x: x.chain[-pos-1].wcet / x.chain[-pos-1].period, reverse=ChainDescendingOrder)]
            elif(ChainSortingBasis=="Period"):
                sorted_chain_tasks = [x.chain[-pos-1] for x in sorted(filtered_chains, key=lambda x: x.chain[-pos-1].period, reverse=ChainDescendingOrder)]
            
            for task in sorted_chain_tasks:
                if(ChainMappingMethod=="WCRT"):
                    successful=self.mapTaskReplicasMinimizingWCRT(task)
                elif(ChainMappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
                else:
                    successful=self.mapTaskReplicasWorstFit(task)
                     
                if(successful==False):
                    return False

        if(not MapFreeTasksFirst):     
            if(freeTasksMapping=="KeepChainWCRT"):
                return self.mapTasksKeepWCRTofOtherTasks(self.allfreetasks,self.allchaintasks,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            else:
                return self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
    

    def mapChainAwareLeaf2Root(self,ChainMappingMethod="WF",ChainDesendingLength=True,MapFreeTasksFirst=False,freeTasksMapping="WF", freeSortingBasis="Utilization",freeDescendingOrder=True):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            if(successful==False):
                return False
        sorted_taskchain = sorted(self.TChains, key=lambda x: len(x.chain),reverse=ChainDesendingLength)
        for taskchain in sorted_taskchain:
            task=self.TS.tasks[taskchain.chain[-1].id]
            if(ChainMappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(ChainMappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False

        if(ChainDesendingLength==False):
            maxlength=len(sorted_taskchain[-1].chain)
        else:
            maxlength=len(sorted_taskchain[0].chain)

        for pos in range(1,maxlength):
            for taskchain in sorted_taskchain:
                if(pos>=len(taskchain.chain)):
                    continue
                task=self.TS.tasks[taskchain.chain[-pos-1].id]
                succtask=self.TS.tasks[taskchain.chain[-pos].id]
                
                if(ChainMappingMethod=="WCRT"):
                    successful=self.mapTaskReplicasMinimizingWCRT(task)
                elif(ChainMappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
                elif(ChainMappingMethod=="Communication"):
                    successful=self.mapTaskReplicasMinimizingCommunication(task,succtask)
                else:
                    successful=self.mapTaskReplicasWorstFit(task)
                        
                if(successful==False):
                    return False

        if(not MapFreeTasksFirst):
            if(freeTasksMapping=="KeepChainWCRT"):
                return self.mapTasksKeepWCRTofOtherTasks(self.allfreetasks,self.allchaintasks,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            else:
                return self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)


    def mapChainByChainFromRoot(self,ChainMappingMethod="WF",ChainDesendingLength=True,MapFreeTasksFirst=False,freeTasksMapping="WF", freeSortingBasis="Utilization",freeDescendingOrder=True):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            if(successful==False):
                return False
        sorted_taskchain = sorted(self.TChains, key=lambda x: len(x.chain),reverse=ChainDesendingLength)
        for taskchain in sorted_taskchain:
            task=self.TS.tasks[taskchain.chain[0].id]
            if(ChainMappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(ChainMappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False

            for ctid in range(1,len(taskchain.chain)):
                task=self.TS.tasks[taskchain.chain[ctid].id]
                prectask=self.TS.tasks[taskchain.chain[ctid-1].id]
                
                if(ChainMappingMethod=="WCRT"):
                    successful=self.mapTaskReplicasMinimizingWCRT(task)
                elif(ChainMappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
                elif(ChainMappingMethod=="Communication"):
                    successful=self.mapTaskReplicasMinimizingCommunication(task,prectask)
                else:
                    successful=self.mapTaskReplicasWorstFit(task)
                        
                if(successful==False):
                    return False

        if(not MapFreeTasksFirst):
            if(freeTasksMapping=="KeepChainWCRT"):
                return self.mapTasksKeepWCRTofOtherTasks(self.allfreetasks,self.allchaintasks,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            else:
                return self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)


    def mapChainByChainFromLeaf(self,ChainMappingMethod="WF",ChainDesendingLength=True,MapFreeTasksFirst=False,freeTasksMapping="WF", freeSortingBasis="Utilization",freeDescendingOrder=True):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            if(successful==False):
                return False
        sorted_taskchain = sorted(self.TChains, key=lambda x: len(x.chain),reverse=ChainDesendingLength)
        for taskchain in sorted_taskchain:
            task=self.TS.tasks[taskchain.chain[-1].id]
            if(ChainMappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(ChainMappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False

            for ctid in range(1,len(taskchain.chain)):
                task=self.TS.tasks[taskchain.chain[-ctid-1].id]
                succtask=self.TS.tasks[taskchain.chain[-ctid].id]
                
                if(ChainMappingMethod=="WCRT"):
                    successful=self.mapTaskReplicasMinimizingWCRT(task)
                elif(ChainMappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
                elif(ChainMappingMethod=="Communication"):
                    successful=self.mapTaskReplicasMinimizingCommunication(task,succtask)
                else:
                    successful=self.mapTaskReplicasWorstFit(task)
                        
                if(successful==False):
                    return False


        if(not MapFreeTasksFirst):
            if(freeTasksMapping=="KeepChainWCRT"):
                return self.mapTasksKeepWCRTofOtherTasks(self.allfreetasks,self.allchaintasks,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            else:
                return self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)


    def mapTasksInMostChains(self,ChainMappingMethod="WF",ChainDesendingLength=True,MapFreeTasksFirst=False,freeTasksMapping="WF", freeSortingBasis="Utilization",freeDescendingOrder=True):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            if(successful==False):
                return False
        count=[0]*len(self.TS.tasks)
        for task in self.allchaintasks:
            count[task.id] = sum(1 for Tchain in self.TChains for instance in Tchain.chain if instance.id == task.id)
        
        if(ChainDesendingLength==True):
            sorted_ids = sorted(range(len(count)), key=lambda i: (count[i],self.TS.tasks[i].wcet / self.TS.tasks[i].period), reverse=True)
        else:
            sorted_ids = sorted(range(len(count)), key=lambda i: count[i],reverse=True)

        for tid in sorted_ids:
            if(count[tid]==0):
                break
            task=self.TS.tasks[tid]
            if(ChainMappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(ChainMappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            elif(ChainMappingMethod=="WF"):
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False

        if(not MapFreeTasksFirst):
            if(freeTasksMapping=="KeepChainWCRT"):
                return self.mapTasksKeepWCRTofOtherTasks(self.allfreetasks,self.allchaintasks,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
            else:
                return self.mapSelectedTasks(self.allfreetasks,MappingMethod=freeTasksMapping,SortingBasis=freeSortingBasis,DescendingOrder=freeDescendingOrder)
        


    def mapDataFlowAwareBundleFromRoot(self,MappingMethod="WF",LargestFirst=False,MapFreeTasksFirst=False):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod="WF",SortingBasis="Utilization",DescendingOrder=True)
            if(successful==False):
                return False
        TaskSucc=[[] for i in range(self.TS.tasknom)]
        for taskchain in self.TChains:
            for task in self.TS.tasks:
                if(taskchain.TaskSucc[task.id]!=None):
                    TaskSucc[task.id].append(taskchain.TaskSucc[task.id])
        if(LargestFirst==True):
            sorted_ids = sorted(range(len(TaskSucc)), key=lambda i: (len(TaskSucc[i]),self.TS.tasks[i].wcet / self.TS.tasks[i].period), reverse=True)
        else:
            sorted_ids = sorted(range(len(TaskSucc)), key=lambda i: len(TaskSucc[i]), reverse=True)


        for tid in sorted_ids:
            task=self.TS.tasks[tid]
            if(MappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(MappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False
            prectask=task
            for succtask in TaskSucc[tid]:
                task=self.TS.tasks[succtask]
                if(MappingMethod=="WCRT"):
                    successful=self.mapTaskReplicasMinimizingWCRT(task)
                elif(MappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
                elif(MappingMethod=="Communication"):
                    successful=self.mapTaskReplicasMinimizingCommunication(task,prectask)
                else:
                    successful=self.mapTaskReplicasWorstFit(task)
                        
                if(successful==False):
                    return False

        if(not MapFreeTasksFirst):
            return self.mapAllTasks("WF",True)
    
    def mapDataFlowAwareBundleFromLeaf(self,MappingMethod="WF",LargestFirst=False,MapFreeTasksFirst=False):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod="WF",SortingBasis="Utilization",DescendingOrder=True)
            if(successful==False):
                return False
        TaskPred=[[] for i in range(self.TS.tasknom)]
        for taskchain in self.TChains:
            for task in self.TS.tasks:
                if(taskchain.TaskPred[task.id]!=None):
                    TaskPred[task.id].append(taskchain.TaskPred[task.id])
        if(LargestFirst==True):
            sorted_ids = sorted(range(len(TaskPred)), key=lambda i: (len(TaskPred[i]),self.TS.tasks[i].wcet / self.TS.tasks[i].period), reverse=True)
        else:
            sorted_ids = sorted(range(len(TaskPred)), key=lambda i: len(TaskPred[i]), reverse=True)

        for tid in sorted_ids:
            task=self.TS.tasks[tid]
            if(MappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(MappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False
            succtask=task
            for predtaskid in TaskPred[tid]:
                task=self.TS.tasks[predtaskid]
                if(MappingMethod=="WCRT"):
                    successful=self.mapTaskReplicasMinimizingWCRT(task)
                elif(MappingMethod=="KeepChainWCRT"):
                    successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
                elif(MappingMethod=="Communication"):
                    successful=self.mapTaskReplicasMinimizingCommunication(task,succtask)
                else:
                    successful=self.mapTaskReplicasWorstFit(task)
                        
                if(successful==False):
                    return False

        if(not MapFreeTasksFirst):
            return self.mapAllTasks("WF",True)



    def mapDataFlowAwareSuccessors(self,MappingMethod="WF",LargestFirst=False,MapFreeTasksFirst=False):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod="WF",SortingBasis="Utilization",DescendingOrder=True)
            if(successful==False):
                return False
        TaskSucc=[[] for i in range(self.TS.tasknom)]
        for taskchain in self.TChains:
            for task in self.TS.tasks:
                if(taskchain.TaskSucc[task.id]!=None):
                    TaskSucc[task.id].append(taskchain.TaskSucc[task.id])
        if(LargestFirst==True):
            sorted_ids = sorted(range(len(TaskSucc)), key=lambda i: (len(TaskSucc[i]),self.TS.tasks[i].wcet / self.TS.tasks[i].period), reverse=True)
        else:    
            sorted_ids = sorted(range(len(TaskSucc)), key=lambda i: len(TaskSucc[i]), reverse=True)

        for tid in sorted_ids:
            task=self.TS.tasks[tid]
            if(MappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(MappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False

        if(not MapFreeTasksFirst):
            return self.mapAllTasks("WF",True)
    

    def mapDataFlowAwarePredecessors(self,MappingMethod="WF",LargestFirst=False,MapFreeTasksFirst=False):
        if(MapFreeTasksFirst):
            successful=self.mapSelectedTasks(self.allfreetasks,MappingMethod="WF",SortingBasis="Utilization",DescendingOrder=True)
            if(successful==False):
                return False
        TaskPred=[[] for i in range(self.TS.tasknom)]
        for taskchain in self.TChains:
            for task in self.TS.tasks:
                if(taskchain.TaskPred[task.id]!=None):
                    TaskPred[task.id].append(taskchain.TaskPred[task.id])
        if(LargestFirst==True):
            sorted_ids = sorted(range(len(TaskPred)), key=lambda i: (len(TaskPred[i]),self.TS.tasks[i].wcet / self.TS.tasks[i].period), reverse=True)
        else:
            sorted_ids = sorted(range(len(TaskPred)), key=lambda i: len(TaskPred[i]), reverse=True)

        for tid in sorted_ids:
            task=self.TS.tasks[tid]
            if(MappingMethod=="WCRT"):
                successful=self.mapTaskReplicasMinimizingWCRT(task)
            elif(MappingMethod=="KeepChainWCRT"):
                successful=self.mapTaskReplicasKeepSumWCRT(task,taskchain=self.allchaintasks)
            else:
                successful=self.mapTaskReplicasWorstFit(task)
            if(successful==False):
                return False
        if(not MapFreeTasksFirst):
            return self.mapAllTasks("WF",True)


    def get_allWCRT(self):
        for node in self.nodes:
            node.get_AllWCRT()
    
    def get_allBCRT(self):
        for node in self.nodes:
            node.get_AllBCRT()

    def checkSchedulabilityAfterReplicaMapping(self,node,task):
        tempnode=node.copy()
        Treplica=TaskReplica(0,tempnode,task)
        tempnode.Treplicas.append(Treplica)
        for nodereplica in tempnode.Treplicas:
            if(task.priority<=nodereplica.task.priority):
                if(nodereplica.task.deadline<tempnode.get_WCRT(nodereplica)):
                    return False
        return True


    def checkSchedulabilityRM(self):
        for node in self.nodes:
            for replica in node.Treplicas:
                if(replica.WCRT>replica.task.deadline):
                    return False
        return True
    
    def printToFile(self,filename):
        f = open(filename, 'w')
        writer = csv.writer(f)

        for node in self.nodes:
            title=["Node"+str(node.id)]
            tasks=[str(replica.task.id) for replica in node.Treplicas]
            writer.writerow(title+tasks)
        f.close()

            
        

