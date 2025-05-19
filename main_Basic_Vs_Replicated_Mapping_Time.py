from TaskSet import *
from TaskChain import *
from JobSet import *
from JobChain import *
from System import *
from excel import *
from datetime import datetime
import timeit
import time

# For the number of sample of tasksets, we change the size of the chain from min_chainlength to max_chainlength and measure the end-to-end latency

max_allowed_jobchains=inf

functions=[
    # ("mapAllTasks", {"MappingMethod":"WF","LargestFirst":True}),  # Function for not replicated
    # ("mapAllTasks", {"MappingMethod":"WF","LargestFirst":True}),  # Functions for replicated
    ("mapChainLeaf2RootTaskBased", {"ChainMappingMethod":"WF","ChainSortingBasis":"Utilization","ChainDescendingOrder":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True})
]
# functions=[
#     ("mapAllTasks", {"MappingMethod":"WF","LargestFirst":True}),  # Function for not replicated
#     ("mapAllTasks", {"MappingMethod":"WF","LargestFirst":True}),  # Functions for replicated
    
#     ("mapChainTasksTogether", {"ChainMappingMethod":"WF","ChainSortingBasis":"Utilization", "ChainDescendingOrder":True,"MapFreeTasksFirst":False, "freeTasksMapping":"KeepChainWCRT","freeSortingBasis":"Utilization", "freeDescendingOrder":True}),
#     ("mapChainTasksTogether", {"ChainMappingMethod":"KeepChainWCRT","ChainSortingBasis":"Utilization", "ChainDescendingOrder":True,"MapFreeTasksFirst":False, "freeTasksMapping":"KeepChainWCRT","freeSortingBasis":"Utilization", "freeDescendingOrder":True}),
#     ("mapChainTasksTogether", {"ChainMappingMethod":"WF","ChainSortingBasis":"Period", "ChainDescendingOrder":True,"MapFreeTasksFirst":False, "freeTasksMapping":"KeepChainWCRT","freeSortingBasis":"Utilization", "freeDescendingOrder":True}),
#     ("mapChainTasksTogether", {"ChainMappingMethod":"WF","ChainSortingBasis":"Period", "ChainDescendingOrder":False,"MapFreeTasksFirst":False, "freeTasksMapping":"KeepChainWCRT","freeSortingBasis":"Utilization", "freeDescendingOrder":True}),
#     ("mapChainTasksTogether", {"ChainMappingMethod":"WF","ChainSortingBasis":"Utilization", "ChainDescendingOrder":True,"MapFreeTasksFirst":True, "freeTasksMapping":"BF","freeSortingBasis":"Utilization", "freeDescendingOrder":True}), 

#     ("mapChainByChainFromLeaf", {"ChainMappingMethod":"WF","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),
#     ("mapChainByChainFromRoot", {"ChainMappingMethod":"WF","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),

#     ("mapChainAwareLeaf2Root", {"ChainMappingMethod":"WF","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),
#     ("mapChainAwareRoot2Leaf", {"ChainMappingMethod":"WF","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),

#     ("mapChainRoot2LeafTaskBased", {"ChainMappingMethod":"WF","ChainSortingBasis":"Utilization","ChainDescendingOrder":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),
#     ("mapChainLeaf2RootTaskBased", {"ChainMappingMethod":"WF","ChainSortingBasis":"Utilization","ChainDescendingOrder":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),

#     ("mapTasksInMostChains", {"ChainMappingMethod":"WF","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),

#     # ("mapAllTasks", (), {"MappingMethod":"WCRT","LargestFirst":LargestFirst}), 
#     # ("mapDataFlowAwarePredecessors", {"MappingMethod":MappingMethod, "LargestFirst":LargestFirst,"WFDFreeTasksFirst":WFDFreeTasksFirst}),
#     # ("mapChainLeaf2RootLargeTaskFirst", {"MappingMethod":MappingMethod, "DesendingLength":DesendingLength,"WFDFreeTasksFirst":WFDFreeTasksFirst}),
#     # ("mapDataFlowAwareSuccessors", {"MappingMethod":MappingMethod, "LargestFirst":LargestFirst,"WFDFreeTasksFirst":WFDFreeTasksFirst}),
#     # ("mapDataFlowAwareBundleFromLeaf", {"MappingMethod":MappingMethod, "LargestFirst":LargestFirst,"WFDFreeTasksFirst":WFDFreeTasksFirst}),
#     # ("mapDataFlowAwareBundleFromRoot", {"MappingMethod":MappingMethod, "LargestFirst":LargestFirst,"WFDFreeTasksFirst":WFDFreeTasksFirst}),

# ]


JChains=[None]*len(functions)
system=[None]*len(functions)
systemTS=[None]*len(functions)

TS=TaskSet()
Debug=True
samples=100
tasknom=20
involvedtasks_nom=10
min_chainlength=3
max_chainlength=6
numchain=max_chainlength-min_chainlength+1
chain_sampling="UnderSampling"
# numchain=4
periods_nom=10

MappingTime=[[] for func in functions]

E2ELatencyTime=[[] for func in functions]

num_jchain=[[[ 0 for sample in range(samples) ] for i in range(max_chainlength-min_chainlength+1)] for func in functions]

# timeout=180 #seconds
timeout=180 #seconds

Ubound=1.2

base_nodenom=2

replicated_repnom=3
replicated_nodenom=5


# Ubound=1.1

# base_nodenom=2

# replicated_repnom=3
# replicated_nodenom=4

replica_nums=[replicated_repnom for x in range(0,len(functions))]
node_nums=[replicated_nodenom for x in range(0,len(functions))]

# replica_nums=[1]
# replica_nums+=[replicated_repnom for x in range(1,len(functions))]

# node_nums=[base_nodenom]
# node_nums+=[replicated_nodenom for x in range(1,len(functions))]

ComBCET=100
ComWCET=1000

ResultFolder="ExecutionTime/"
now = datetime.now()
folder_name = now.strftime("A%d%m%Y-%H%M%S/")
try:
    os.mkdir(ResultFolder)
except:
    pass

try:
    os.mkdir(ResultFolder+folder_name)
except:
    print("could not make the folder")
    pass

notes = '''
Benchmark
Number of samples = {samples}
Number of tasks = {tasknom}
Number of tasks that are involved in chains={involvedtasks_nom}
Minimum number of tasks per chain = {min_chainlength}
Maximum number of tasks per chain = {max_chainlength}
Random or under-sampling = {chain_sampling}
Number of different periods = {periods_nom}
Ubound = {Ubound}
Number of nodes without replication = {base_nodenom}
Number of replicas = {replicated_repnom}
Number of nodes with replication = {replicated_nodenom}
Minimum communication delay = {ComBCET}
Maximum communication delay = {ComWCET}
Data folder name = {folder_name}
'''.format(samples=samples,tasknom=tasknom,involvedtasks_nom=involvedtasks_nom,min_chainlength = min_chainlength, max_chainlength = max_chainlength,chain_sampling=chain_sampling,periods_nom=periods_nom, Ubound=Ubound, base_nodenom=base_nodenom, replicated_nodenom=replicated_nodenom,replicated_repnom=replicated_repnom, ComBCET=ComBCET, ComWCET=ComWCET,folder_name=folder_name)

lengths=random.sample(range(min_chainlength,max_chainlength+1),k=numchain)

for sample in range(samples):
    print("sample: ",sample)
    successful=False
    while(successful==False):
        TS.generateSyntheticTasks(n=tasknom,Ubound=Ubound,periods_nom=periods_nom)
        # print([str(task) for task in TS.tasks])
        maxperiod=max(TS.tasks,key=lambda task:task.period).period
        minperiod=min(TS.tasks,key=lambda task:task.period).period
        maxtaskjobs= 2*TS.hp/minperiod
        TChains=[]
        
        # for cnom in range(chainnom):
        # lengths=random.sample(range(min_chainlength,max_chainlength+1),k=numchain)
        candidtaskIDs=random.sample(range(tasknom),k=involvedtasks_nom)
        for chainid in range(numchain):
            TChain=TaskChain(TS)
            while(True):#Filtering out big chains
                TChain.makeRandomChains(length=lengths[chainid],type=chain_sampling,candidtaskIDs=candidtaskIDs)
                jobcounts_upperbound=TChain.getMaxJobChainNom()
                if(jobcounts_upperbound<=max_allowed_jobchains):
                    break
                else:
                    print("Max Allowed is Surpassed!")
            TChains.append(TChain)

        

        for i in range(len(functions)):
            systemTS[i]=TS.copy()

            system[i]=System(TS=systemTS[i],nodenom=node_nums[i],repnom=replica_nums[i],TChains=TChains)

            method_name, kwargs = functions[i]  # Extract method details
            method = getattr(system[i], method_name)  # Get method by name
            successful=False

            def mapping():
                global successful
                successful=method(**kwargs)  # Call method with unpacked arguments

            def calculate_end_to_end_latency():
                global successful

                system[i].get_allWCRT()
                system[i].get_allBCRT()

                if(system[i].checkSchedulabilityRM()==False):
                    successful=False
                    return False
                JChains[i]=JobChainSet(TS=systemTS[i],ComBCET=ComBCET,ComWCET=ComWCET)
                JChains[i].getAllReadIntervals()
                JChains[i].getAllDataIntervals()

                for TChain in TChains:
                    length=len(TChain.chain)

                    JChains[i].setTaskChain(TChain)

                    successful=JChains[i].createPossibleChainsTimeout(timeout=timeout)
                    if(successful==False):
                        break

                if(successful==False):
                    return False

                maxe2e=JChains[i].getMaxEndtoEndLatency()
            
            mapping_time_ms=timeit.timeit(mapping,number=1) * 1000
            if(successful==False):
                print("Mapping was not successful")
                continue
                
            e2e_time_ms=timeit.timeit(calculate_end_to_end_latency,number=1) * 1000

            if(successful==True):
                print(f"Mapping time: {mapping_time_ms:.2f} ms")
                print(f"E2E calculation time: {e2e_time_ms:.2f} ms")
                MappingTime[i].append(mapping_time_ms)
                E2ELatencyTime[i].append(e2e_time_ms)
                suffix = ", ".join(f"{k}={v}" for k, v in kwargs.items())
                writeExelByRow(ResultFolder+folder_name+method_name+suffix+"_r"+str(system[i].repnom)+"n"+str(system[i].nodenom)+"_ExeTime",["Mapping","E2E Calculation"],[MappingTime[i],E2ELatencyTime[i]],notes=notes)


        
           
            
           