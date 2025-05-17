from TaskSet import *
from TaskChain import *
from JobSet import *
from JobChain import *
from System import *
from excel import *
from datetime import datetime

# For the number of sample of tasksets, we change the size of the chain from min_chainlength to max_chainlength and measure the end-to-end latency

max_allowed_jobchains=inf

functions=[
    ("mapAllTasks", {"MappingMethod":"WF","LargestFirst":True}),  # Function for not replicated
    ("mapAllTasks", {"MappingMethod":"WF","LargestFirst":True}),  # Functions for replicated
    
    ("mapChainTasksTogether", {"ChainMappingMethod":"WF","ChainSortingBasis":"Utilization", "ChainDescendingOrder":True,"MapFreeTasksFirst":False, "freeTasksMapping":"KeepChainWCRT","freeSortingBasis":"Utilization", "freeDescendingOrder":True}),
    ("mapChainTasksTogether", {"ChainMappingMethod":"KeepChainWCRT","ChainSortingBasis":"Utilization", "ChainDescendingOrder":True,"MapFreeTasksFirst":False, "freeTasksMapping":"KeepChainWCRT","freeSortingBasis":"Utilization", "freeDescendingOrder":True}),
    ("mapChainTasksTogether", {"ChainMappingMethod":"WF","ChainSortingBasis":"Period", "ChainDescendingOrder":True,"MapFreeTasksFirst":False, "freeTasksMapping":"KeepChainWCRT","freeSortingBasis":"Utilization", "freeDescendingOrder":True}),
    ("mapChainTasksTogether", {"ChainMappingMethod":"WF","ChainSortingBasis":"Period", "ChainDescendingOrder":False,"MapFreeTasksFirst":False, "freeTasksMapping":"KeepChainWCRT","freeSortingBasis":"Utilization", "freeDescendingOrder":True}),
    ("mapChainTasksTogether", {"ChainMappingMethod":"WF","ChainSortingBasis":"Utilization", "ChainDescendingOrder":True,"MapFreeTasksFirst":True, "freeTasksMapping":"BF","freeSortingBasis":"Utilization", "freeDescendingOrder":True}), 

    ("mapChainByChainFromLeaf", {"ChainMappingMethod":"KeepChainWCRT","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),
    ("mapChainByChainFromRoot", {"ChainMappingMethod":"KeepChainWCRT","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),

    ("mapChainAwareLeaf2Root", {"ChainMappingMethod":"KeepChainWCRT","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),
    ("mapChainAwareRoot2Leaf", {"ChainMappingMethod":"KeepChainWCRT","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),

    ("mapChainRoot2LeafTaskBased", {"ChainMappingMethod":"KeepChainWCRT","ChainSortingBasis":"Utilization","ChainDescendingOrder":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),
    ("mapChainLeaf2RootTaskBased", {"ChainMappingMethod":"KeepChainWCRT","ChainSortingBasis":"Utilization","ChainDescendingOrder":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),

    ("mapTasksInMostChains", {"ChainMappingMethod":"KeepChainWCRT","ChainDesendingLength":True,"MapFreeTasksFirst":False,"freeTasksMapping":"KeepChainWCRT", "freeSortingBasis":"Utilization","freeDescendingOrder":True}),

    # ("mapAllTasks", (), {"MappingMethod":"WCRT","LargestFirst":LargestFirst}), 
    # ("mapDataFlowAwarePredecessors", {"MappingMethod":MappingMethod, "LargestFirst":LargestFirst,"WFDFreeTasksFirst":WFDFreeTasksFirst}),
    # ("mapChainLeaf2RootLargeTaskFirst", {"MappingMethod":MappingMethod, "DesendingLength":DesendingLength,"WFDFreeTasksFirst":WFDFreeTasksFirst}),
    # ("mapDataFlowAwareSuccessors", {"MappingMethod":MappingMethod, "LargestFirst":LargestFirst,"WFDFreeTasksFirst":WFDFreeTasksFirst}),
    # ("mapDataFlowAwareBundleFromLeaf", {"MappingMethod":MappingMethod, "LargestFirst":LargestFirst,"WFDFreeTasksFirst":WFDFreeTasksFirst}),
    # ("mapDataFlowAwareBundleFromRoot", {"MappingMethod":MappingMethod, "LargestFirst":LargestFirst,"WFDFreeTasksFirst":WFDFreeTasksFirst}),

]

function_names=[]
for i in range(len(functions)):
    method_name,  kwargs = functions[i]
    function_names.append(method_name+", ".join(f"{k}={v}" for k, v in kwargs.items()))

JChains=[None]*len(functions)
system=[None]*len(functions)
systemTS=[None]*len(functions)

TS=TaskSet()
UMin=1
UMax=1.7
samples=1000
tasknom=20
involvedtasks_nom=10
min_chainlength=3
max_chainlength=10
numchain=max_chainlength-min_chainlength+1
chain_sampling="UnderSampling"
# numchain=4
periods_nom=10

timeout=180 #seconds

base_nodenom=2

replicated_repnom=3
replicated_nodenom=5

# Ubound=1.1

# base_nodenom=2

# replicated_repnom=3
# replicated_nodenom=4

replica_nums=[1]
replica_nums+=[replicated_repnom for x in range(1,len(functions))]

node_nums=[base_nodenom]
node_nums+=[replicated_nodenom for x in range(1,len(functions))]

ComBCET=100
ComWCET=1000

ResultFolder="AcceptanceRatio/"
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
UMin = {UMin}
UMax = {UMax}
Number of nodes without replication = {base_nodenom}
Number of replicas = {replicated_repnom}
Number of nodes with replication = {replicated_nodenom}
Minimum communication delay = {ComBCET}
Maximum communication delay = {ComWCET}
Data folder name = {folder_name}
'''.format(samples=samples,tasknom=tasknom,involvedtasks_nom=involvedtasks_nom,min_chainlength = min_chainlength, max_chainlength = max_chainlength,chain_sampling=chain_sampling,periods_nom=periods_nom, UMin=UMin, UMax=UMax, base_nodenom=base_nodenom, replicated_nodenom=replicated_nodenom,replicated_repnom=replicated_repnom, ComBCET=ComBCET, ComWCET=ComWCET, folder_name=folder_name)






Ubounds=np.arange(UMin,UMax,0.01)
Acceptednom=[]

for i in range(len(functions)):
    if(Ubounds[0]==0):
        Acceptednom.append([1]+[0]*(len(Ubounds)-1))
        ui=1
    else:
        Acceptednom.append([0]*len(Ubounds))
        ui=0

lengths=random.sample(range(min_chainlength,max_chainlength+1),k=numchain)

for uid in range(ui,len(Ubounds)):
    u=Ubounds[uid]
    print("Ubound: ",u)
    if(u<=0):
        continue
    for sample in range(samples):
        successful=False
        # print("sample: ",sample)
        TS.generateSyntheticTasks(n=tasknom,Ubound=u,periods_nom=periods_nom)
        maxperiod=max(TS.tasks,key=lambda task:task.period).period
        minperiod=min(TS.tasks,key=lambda task:task.period).period
        maxtaskjobs= 2*TS.hp/minperiod
        TChains=[]
        
        # print("maximum allowed number of job chains: ",max_allowed_jobchains)
        # for cnom in range(chainnom):
        lengths=random.sample(range(min_chainlength,max_chainlength+1),k=numchain)
        for chainid in range(numchain):
            TChain=TaskChain(TS)
            while(True):#Filtering out big chains
                TChain.makeRandomChains(length=lengths[chainid],type=chain_sampling)
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
            successful=method(**kwargs)  # Call method with unpacked arguments

            if(successful==False):
                continue

            system[i].get_allWCRT()
            system[i].get_allBCRT()

            if(system[i].checkSchedulabilityRM()==False):
                successful=False
                continue

            Acceptednom[i][uid]+=1
    AR_data=[[x / samples for x in sublist] for sublist in Acceptednom]
    print("Accepance ratios"+ ": ", [function_names[i]+": "+ str(AR_data[i][uid]) for i in range(len(functions))])

    writeExelByRow(ResultFolder+folder_name+"/AcceptanceRatio",["Ubound"]+function_names,[Ubounds]+AR_data,notes=notes)

            

            


            
