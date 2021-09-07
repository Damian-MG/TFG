# Library of python functions to work with genomic compressed fastq/fasta files
import pathlib
from lithops import Storage
import subprocess as sp
import lithopsgenetics.auxiliaryfunctions as af

CURRENT_PATH = str(pathlib.Path(__file__).parent.resolve())


# FUNCTION preprocess_chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, file, lines)
def preprocess_chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, file, lines):
    # 1 GENERATING THE INDEX AND INFORMATION FILES AND UPLOADING TO THE BUCKET

    sp.run(CURRENT_PATH+'/generateUploadIndexInfoBucket.sh '+file+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True)
    output = sp.getoutput(CURRENT_PATH+'/generateUploadIndexInfoBucket.sh '+file)
    output = output.split()
    total_lines = str(af.only_numerics(output[-3]))
    block_length = str(lines)
    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    sp.run(CURRENT_PATH+'/generateChunks.sh '+file+' '+block_length+' '+total_lines+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True) 
    chunk, chunk_counter = af.read_chunks_info(file)
    # 3 RETRIEVE CHUNKS FROM BUCKET AND UNZIP THEM
    for i in chunk:
        print("Processing first chunk... ", i['number'])
        sp.run(CURRENT_PATH+'/downloadDecompressChunk.sh '+file+' '+BUCKET_LINK+' '+BUCKET_NAME+' '+i['start_line']+' '+block_length+' '+i['start_byte']+' '+i['end_byte'], shell=True, check=True, universal_newlines=True)
    sp.run('rm '+file+'.chunks.info', shell=True, check=True, universal_newlines=True)
    print(str(chunk_counter)+" chunks decompressed.")


# FUNCTION retrieve_random_chunk_gzfile(BUCKET_NAME, BUCKET_LINK, file, start_line, end_line)
def retrieve_random_chunk_gzfile(BUCKET_NAME, BUCKET_LINK, file, start_line, end_line):
    block_length = int(end_line) - int(start_line) + 1
    block_length = str(block_length)
    # 1 GETTING CHUNK BYTE RANGE
    sp.run(CURRENT_PATH+'/randomChunkRange.sh '+file+' '+start_line+' '+end_line+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True)
    chunk = af.read_chunk_info_random(file, start_line, end_line)
    # 2 RETRIEVE CHUNK FROM BUCKET AND UNZIP IT
    sp.run(CURRENT_PATH+'/downloadDecompressChunk.sh '+file+' '+BUCKET_LINK+' '+BUCKET_NAME+' '+chunk['start_line']+' '+block_length+' '+chunk['start_byte']+' '+chunk['end_byte'], shell=True, check=True, universal_newlines=True)
    sp.run('rm '+file+'.random_chunk_'+start_line+'_'+end_line+'.info', shell=True, check=True, universal_newlines=True)
    print("Chunk decompressed.")


# FUNCTION preprocess_gzfile(BUCKET_NAME, file)
def preprocess_gzfile(BUCKET_NAME, file):
    # 1 GENERATING THE INDEX AND INFORMATION FILES AND UPLOADING TO THE BUCKET
    sp.run(CURRENT_PATH+'/generateUploadIndexInfoBucket.sh '+file+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True)
    output = sp.getoutput(CURRENT_PATH+'/generateUploadIndexInfoBucket.sh '+file)
    output = output.split()
    total_lines = str(af.only_numerics(output[-3]))
    return total_lines


# FUNCTION chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, file, lines)
def chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, file, lines, total_lines):
    block_length = str(lines)
    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    sp.run(CURRENT_PATH+'/generateChunks.sh '+file+' '+block_length+' '+total_lines+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True) 
    chunk, chunk_counter = af.read_chunks_info(file)
    # 3 RETRIEVE CHUNKS FROM BUCKET AND UNZIP THEM
    for i in chunk:
        print("Processing first chunk... ", i['number'])
        sp.run(CURRENT_PATH+'/downloadDecompressChunk.sh '+file+' '+BUCKET_LINK+' '+BUCKET_NAME+' '+i['start_line']+' '+block_length+' '+i['start_byte']+' '+i['end_byte'], shell=True, check=True, universal_newlines=True)
    sp.run('rm '+file+'.chunks.info', shell=True, check=True, universal_newlines=True)
    print(str(chunk_counter)+" chunks decompressed.")


# FUNCTION iter_data_bucket_fasta_fastq(BUCKET_NAME, fasta_pattern, fastq_pattern)
def iter_data_bucket_fasta_fastq(storage, BUCKET_NAME, fasta_pattern, fastq_pattern):
    # 1 RETRIEVE KEYS OF THE BUCKET MATCHING THE PREFIX PATTERN AND ITER THROUGH THEM
    storage = Storage()
    list_fasta = storage.list_objects(BUCKET_NAME, prefix=fasta_pattern)
    list_fastq = storage.list_objects(BUCKET_NAME, prefix=fastq_pattern)
    iter_data = []
    for i in list_fasta:
        for j in list_fastq:
            iter_data.append({'fasta_chunk': i['Key'], 'fastq_chunk': j['Key']})
    return iter_data
