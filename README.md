# Final Degree Project
Implementation of a Python genomic function library, for the management of large genomic files and the distributed processing of them
Teachers: Pedro, GARCIA LOPEZ & Josep, SAMPE DOMENECH

## Authors
* **Damián Maleno González** - [Damian-MG](https://github.com/Damian_MG)

## Description

In recent years, the size of the files that store genomic data has increased exponentially to the point where it is no longer feasible to store these files locally without
compressing them in formats such as gzip. In addition, thanks to cloud computing we can carry out parallel computing, accelerating the execution time of the programs that use this 
genomic data. This library of python functions for managing large genomic files is designed to work with [Lithops] (https://github.com/lithops-cloud/lithops) and its objective is 
to partition compressed genomic files in gzip format for their parallel execution.


## Requirements
  1. Install Lithops from the PyPi repository:

      ```bash
      $ pip install lithops
      ```
   2. Configuration:
 
 Lithops provides an extensible backend architecture (compute, storage) that is designed to work with different Cloud providers and on-premise backends. In this sense, you can 
 code in python and run it unmodified in IBM Cloud, AWS, Azure, Google Cloud and Alibaba Aliyun. Moreover, it provides support for running jobs on vanilla kubernetes, or by
 using a kubernetes serverless framework like Knative or OpenWhisk.
   
   **The Bucket used has to be of public access: The Public Access group will have the role of Content Reader (one can read and list objects in the bucket)
   
## Functions
   
