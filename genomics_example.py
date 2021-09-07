'''
Cloudbutton Genomics Use case - Variant Caller Demo - processing fastq and fasta inputs into chunks to parallelise mapping and mpileup stage. Reduce function merges mpileup and calls SNPs using SiNPle
to do:
- add fasta to iterdata
- index fasta chunks and parse correct location for each chunk
- add fastq byte ranges to iterdata
- fix SiNPle output (not generated in lithops)
'''

import os
import subprocess as sp
import logging
import lithops 
import shutil
from lithops import Storage
import os.path
import lithopsgenetics


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def copy_to_runtime(storage, storage_location, folder, file_name):
    obj_stream = storage.get_object(bucket=storage_location, key=folder+file_name, stream=True)
    temp_file = "/tmp/" + file_name
    with open(temp_file, 'wb') as file:
        shutil.copyfileobj(obj_stream, file)
        print('Finished copying'+ file_name + 'to local disk')
    return temp_file


# gem3 mapper to mpileup output
def my_map_function(obj, storage):

    print('Bucket: {}'.format(obj.bucket))
    print('Copying fastq dataset to local disk')
    temp_fastq = '/tmp/file.fastq'
    with open(temp_fastq, 'wb') as fastqfile:
        shutil.copyfileobj(obj.data_stream, fastqfile)
        print('Finished copying fastq dataset to local disk')

    # copying reference genomes from cloud storage to runtime
    temp_gem_ref = copy_to_runtime(storage, storage_location, ref_folder, gem_genome)
    temp_fa_ref = copy_to_runtime(storage, storage_location, ref_folder, fa_genome)
    temp_fai_ref = copy_to_runtime(storage, storage_location, ref_folder, fai_genome)

    # temporary intermediate file names
    sam_name = os.path.splitext(temp_fastq)[0]+'.se.sam'
    bam_name = os.path.splitext(sam_name)[0]+'.bam'
    bam_sorted_name = os.path.splitext(bam_name)[0]+'.sorted.bam'

    # 1. fastq to sam (gem3-mapper)
    sp.call(['gem-mapper', '-I', temp_gem_ref, '-i', temp_fastq],
                 stdout=open(sam_name,'w'))
    # 2. sam to bam (samtools)
    sp.call(['samtools', 'view', '-bS', sam_name],
                 stdout=open(bam_name,'w'))
    # 3. sort bam (samtools)
    sp.call(['samtools', 'sort', bam_name],
                    stdout=open(bam_sorted_name,'w'))
    # 4. generate mpileup (samtools)
    mpileup_out = sp.check_output(['samtools', 'mpileup', '-A', '-B', '-Q', '0', '-f', temp_fa_ref, bam_sorted_name])

    return mpileup_out


# mpileup merge and SNP calling with SiNPle
def my_reduce_function(results, storage):
    lineout = []
    for line in results:
        line = line.decode('UTF-8') 
        lineout.append(line)
    output="".join(lineout)
    #print(output)
    # temp_mpileup = '/tmp/file.mpileup'
    # f = open(temp_mpileup, 'w')
    # f.write(output)
    # sinple_out = sp.check_output(['bash','/bin/mpileup_merge_reduce.sh', temp_mpileup, '/bin/'])
    # sinple_out = sinple_out.decode('UTF-8') 
    # print("sinple output \n")
    # print(sinple_out)
    # storage.put_object(storage_location, 'outputs/test2.txt', body=sinple_out)
    storage.put_object(storage_location, 'outputs/test2.txt', body=output)


if __name__ == "__main__":

    BUCKET_NAME = 'lithops-genomics-varcaller'  # change-me, REMEMBER TO DELETE FILES FROM BUCKET WHEN REPROCESSING
    BUCKET_LINK = 'https://' + BUCKET_NAME + '.s3.eu-gb.cloud-object-storage.appdomain.cloud/' # change-me
    lithopsgenetics.preprocess_chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, '1c-12S_S96_L001_R1_001.fastq.gz', '100000')

    # input genome files
    gem_genome = 'NC_000861_charr.gem'
    fa_genome = 'NC_000861_charr.fa'
    fai_genome = 'NC_000861_charr.fa.fai'

    # cloud bucket locations (IBM cos)
    storage_location = 'cloudbutton-bioinformatics'
    fastq_location = BUCKET_NAME
    ref_folder = "references/"
    out_folder = "outputs/"

    iterdata = [fastq_location]

    fexec = lithops.FunctionExecutor(runtime='lumimar/ibm_gem3_runtime:0.2')
    #fexec.map(my_map_function, iterdata)
    fexec.map_reduce(my_map_function, iterdata, my_reduce_function)
    result = fexec.get_result()
