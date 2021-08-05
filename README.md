# Final Degree Project
Implementation of a Python genomic function library, for the management of large genomic files and the distributed processing of them
Teachers: Pedro, GARCIA LOPEZ & Josep, SAMPE DOMENECH

## Authors
* **Damián Maleno González** - [Damian-MG](https://github.com/Damian_MG)

## Description

In recent years, the size of the files that store genomic data has increased exponentially to the point where it is no longer feasible to store these files locally without
compressing them in formats such as gzip. In addition, thanks to cloud computing we can carry out parallel computing, accelerating the execution time of the programs that use 
this genomic data. This library of python functions for managing large genomic files is designed to work with [Lithops](https://github.com/lithops-cloud/lithops) and its 
objective is to partition compressed genomic files in gzip format for their parallel execution.


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
   
   An example of BUCKET_LINK would be: 'https://BUCKET_NAME.s3.END-POINT.cloud-object-storage.appdomain.cloud/'
   
## Functions

  1. preprocess_chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, 'FILE', 'LINES')

Files required locally: file.gz
Files required in the bucket: none
Description: The function takes the gzip file, creates the necessary index files for partitioning and stores them in the bucket. Then it creates the partitions of x 'LINES' of the compressed file, unzips them and stores them in the bucket.

  2. retrieve_random_chunk_gzfile(BUCKET_NAME, BUCKET_LINK, 'FILE', 'start_line', 'end_line')

Files required locally: file.gzi, file.gzi.info, file.gzi_tab.info
Files required in the bucket: file.gz
Description: The function retrieves a random chunk definded by 'start_line' and 'end_line' of the gzip file stored in the bucket, unzips it and stores it back in the bucket.

  3. preprocess_gzfile(BUCKET_NAME, 'FILE')

Files required locally: file.gz
Files required in the bucket: none
Description: The function takes the gzip file, creates the necessary index files for partitioning and stores them in the bucket.
Returns: total_lines

  4. chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, 'FILE', 'LINES', 'total_lines')
 
Files required locally: file.gzi, file.gzi.info, file.gzi_tab.info
Files required in the bucket: file.gz
Description: For an already preprocessed gzip file, creates the partitions of x 'LINES' of the compressed file, unzips them and stores them in the bucket.
   
