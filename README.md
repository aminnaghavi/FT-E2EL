Please first install all the python dependencies.

For getting the End-to-End Latency results over 100 task sets please run the file "main_Basic_Vs_Replicated_Mapping_Latency.py". 
You can find the reuslts in the "Latency" folder that will be created. For each method, the excel files contains the end-to-end latency of each chain in each task set for 100 task-sets.

For measuring the Acceptance ratio, please run the file "main_Basic_Vs_Replicated_Mapping_Latency.py". 
The results of the acceptance ratio of each method is found in the folder named "AcceptanceRatio". The excel fine contains the ratio of schedulable task-sets for each total utilization.

To measure the execution time of the mapping and end-to-end latency method, you can run the file "main_Basic_Vs_Replicated_Mapping_Time.py". 
The results will be generated in the folder named "ExecutionTime" for 100 execution of the mapping and the latency calculation.

You can change the settings in "main_Basic_Vs_Replicated_Mapping_Latency", "main_Basic_Vs_Replicated_Mapping_Latency", and "main_Basic_Vs_Replicated_Mapping_Time.py" for different scenarios, different number of nodes, etc.


