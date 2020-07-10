# experiment-parser
* mergeDatasets folder contains code to iterate across experimentFolder
    * Find directories containing experiment results (e.g.: experiment1, experiment2).
    * The files application_metrics.csv and system_metrics.csv inside the folder, are merged based on timestamp.
    * The result is written inside outputFolder as experiment_name.csv (e.g.: experiment1.csv)
    
# Required structure of application and system metrics
* application_metrics.csv
    * Collection method - Observability
    * 10 sec granularity
    * timestamp followed by other application metrics 
    (e.g.: timestamp, avg_latency, throughput, ...)
    
* system_metrics.csv
    * Collection method - 
        1) cadvisor (refer experiment1 folder)
        2) kubernetes metric server(refer experiment2 folder)
    * approx 2 sec granularity (**less than 10sec**) 
    * timestamp followed by other system metrics 
    (e.g.: timestamp,cpu_usage,memory_usage)
    
    
      
