"""
Cloudbutton Genomics Use case - Variant Caller Demo - processing fastq and
fasta  inputs into chunks to parallelise mapping and mpileup stage. Reduce
function merges mpileup and calls SNPs using SiNPle
​
to do:
- add single vs paired end option
- 
"""
​
import subprocess as sp
import lithops 
import shutil
from lithops import Storage
import os.path
import lithopsgenetics
import json 
​
​
BUCKET_NAME = 'lithops-genomics-varcaller'  # change-me, REMEMBER TO DELETE FILES FROM BUCKET WHEN REPROCESSING
fasta_chunks_prefix = 'DUMMY_split_'
fastq_file = '1c-12S_S96_L001_R1_001.fastq.gz' 
​
# object prefixes
ref_folder = "genomics/references/"
out_folder = "genomics/outputs/"
idx_folder = "genomics/indexes/"
​
​
def copy_to_runtime(storage, bucket, folder, file_name, byte_range=None):
    print(f'Copying {file_name} to local disk')
    extra_get_args = {'Range': f'bytes={byte_range}'} if byte_range else {}
    obj_stream = storage.get_object(bucket=bucket, key=folder+file_name, stream=True, extra_get_args=extra_get_args)
    temp_file = "/tmp/" + file_name
    with open(temp_file, 'wb') as file:
        shutil.copyfileobj(obj_stream, file)
        print(f'Finished copying {file_name} to local disk')
    return temp_file
​
def check_temp_file(temp_file, no_of_lines):
    print("\nPrinting " + temp_file )
    file = open(temp_file, 'r')
    Lines = file.readlines()
    count = 0
    # Strips the newline character
    for line in Lines:
        count += 1
        if count < no_of_lines:
            print(line.strip())
            #print("Line{}: {}".format(count, line.strip()))
    print("Finished printing " + temp_file + "\n")
​
def my_map_function(fasta_chunk, fastq_chunk, storage):
    """
    gem3 mapper to mpileup output
    """
    # copying fasta chunk to runtime
    temp_fasta = copy_to_runtime(storage, BUCKET_NAME, '', fasta_chunk)
    check_temp_file(temp_fasta, 50)
​
    # copying fastq chunk to runtime
    fastq_file_key = fastq_chunk[0]
    fastq_chunk_data = fastq_chunk[1]
    byte_range = f"{int(fastq_chunk_data['start_byte'])-1}-{int(fastq_chunk_data['end_byte'])}"
    temp_fastq_gz = copy_to_runtime(storage, BUCKET_NAME, '', fastq_file_key, byte_range)
​
    # getting index and decompressing fastq chunk
    temp_fastq = temp_fastq_gz.replace('.fastq.gz', f'_chunk{fastq_chunk_data["number"]}.fastq')
    temp_fastq_i = copy_to_runtime(storage, BUCKET_NAME, idx_folder, f'{fastq_file_key}i')
    block_length = str(int(fastq_chunk_data['end_line']) - int(fastq_chunk_data['start_line']) + 1)
    cmd = f'gztool -I {temp_fastq_i} -n {fastq_chunk_data["start_byte"]} -L {fastq_chunk_data["start_line"]} {temp_fastq_gz} | head -{block_length} > {temp_fastq}'
    sp.run(cmd, shell=True, check=True, universal_newlines=True)
    check_temp_file(temp_fastq, 100)
​
    # create gem index file for fasta chunk [gem-indexer adds .gem to the output name]
    temp_gem_ref_nosuffix = os.path.splitext(temp_fasta)[0]
    print("temp_gem_ref_nosuffix " + temp_gem_ref_nosuffix)
    temp_gem_ref = os.path.splitext(temp_fasta)[0]+'.gem'
    # sp.call(['gem-indexer', '-i', temp_fasta], stdout=open(temp_gem_ref, 'w'))
    sp.call(['gem-indexer', '-i', temp_fasta, '-o', temp_gem_ref_nosuffix])
 
    #check_temp_file(temp_gem_ref, 50)
​
    # create samtools index file for fasta chunk (.fai)
    temp_fai_ref = os.path.splitext(temp_fasta)[0]+'.fasta.fai'
    sp.call(['samtools', 'faidx', temp_fasta], stdout=open(temp_fai_ref, 'w'))
    check_temp_file(temp_fai_ref, 50)
​
    # verify all files are in /tmp
    print("\nlist of files in /tmp folder")
    print('\n'.join(sorted(os.listdir("/tmp"))))
​
    print('\nGoing to process fastq chunk:', temp_fastq)
    print(fastq_chunk_data)
​
    # temporary intermediate file names
    sam_name = os.path.splitext(temp_fastq)[0]+'.se.sam'
    bam_name = os.path.splitext(sam_name)[0]+'.bam'
    bam_sorted_name = os.path.splitext(bam_name)[0]+'.sorted.bam'
    
​
    # 1. fastq to sam (gem3-mapper)
    sp.call(['gem-mapper', '-I', temp_gem_ref, '-i', temp_fastq,], stdout=open(sam_name, 'w'))
    check_temp_file(sam_name, 50)
​
​
    # retrieve index (number of mismatches for each aligned read in each fasta chunk) for sam aln
    # ********
​
    #############################################
​
    # send index to redis (or equivalent)
    # ********
​
    # receive corrected index from redis
    # ********
    #############################################
​
    # correct sam file 
    # ********
    
​
    # 2. sam to bam (samtools)
    print("'samtools', 'view', '-bS', sam_name, stdout=open(bam_name, 'w'")
    print('samtools' + ' view' + ' -bS ' + sam_name + "\t" + bam_name)
    sp.call(['samtools', 'view', '-bS', sam_name], stdout=open(bam_name, 'w'))
    # 3. sort bam (samtools)
    sp.call(['samtools', 'sort', bam_name], stdout=open(bam_sorted_name, 'w'))
    # 4. generate mpileup (samtools)
    
    mpileup_out = sp.check_output(['samtools', 'mpileup', '-A', '-B', '-Q', '0', '-f', temp_fasta, bam_sorted_name])
    
    # 5. fix mpileup coordinates
    # ********
    #print(mpileup_out)
    #mpileup_out = "A"
​
    return mpileup_out
​
​
def my_reduce_function(results, storage):
    """
    Mpileup merge and SNP calling with SiNPle
    """
    lineout = []
    for line in results:
        line = line.decode('UTF-8')
        lineout.append(line)
    output = "".join(lineout)
​
    temp_mpileup = '/tmp/file.mpileup'
    with open(temp_mpileup, 'w') as f:
        f.write(output)
    sinple_out = sp.check_output(['bash', '/bin/mpileup_merge_reduce.sh', temp_mpileup, '/bin/'])
    sinple_out = sinple_out.decode('UTF-8')
​
    storage.put_object(BUCKET_NAME, out_folder+'test2.txt', body=sinple_out)
​
​
if __name__ == "__main__":
​
    # Preliminary steps:
    # 1. upload the fastq.gz into BUCKET_NAME
    # 2. Upload the fasta chunks into BUCKET_NAME
​
    # Create index files (only once)
    #lithopsgenetics.preprocess_gzfile(BUCKET_NAME, fastq_file)  # Uncomment only one time
​
    # Generate iterdata
    iterdata = lithopsgenetics.create_iterdata_from_info_files(BUCKET_NAME, fasta_chunks_prefix, fastq_file, 100000)
    print("\niterdata")
    print(json.dumps(iterdata, indent=4))
    fexec = lithops.FunctionExecutor(runtime='lumimar/ibm_gem3_runtime:0.4',runtime_memory=1024,log_level='DEBUG')
    fexec.map_reduce(my_map_function, iterdata, my_reduce_function)
    result = fexec.get_result()