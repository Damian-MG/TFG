#
# (C) Copyright Cloudlab URV 2021
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pathlib
import os
import shutil
import tempfile
from lithops import Storage
import subprocess as sp
import lithopsgenetics.auxiliaryfunctions as af

CWD = os.getcwd()
CURRENT_PATH = str(pathlib.Path(__file__).parent.resolve())
LOCAL_TMP = os.path.realpath(tempfile.gettempdir())
INDEXES_PREIX = 'genomics/indexes/'
CHUNKS_PREIX = 'genomics/chunks/'


def preprocess_gzfile(bucket_name, file_name):
    """
    The function takes the gzip file, creates the necessary index files
    for partitioning and stores them in the bucket.
    """
    os.chdir(LOCAL_TMP)
    storage = Storage()
    # 0 DOWNLOAD FASTQ.GZ FILE TO LOCAL TMP
    local_filename = os.path.join(LOCAL_TMP, file_name)
    if not os.path.isfile(local_filename):
        print(f'Downloading cos://{bucket_name}/{file_name} to {LOCAL_TMP}')
        obj_stream = storage.get_object(bucket_name, file_name, stream=True)
        with open(local_filename, 'wb') as fl:
            shutil.copyfileobj(obj_stream, fl)

    # 1 GENERATING THE INDEX AND INFORMATION FILES AND UPLOADING TO THE BUCKET
    sp.run(CURRENT_PATH+'/generateIndexInfo.sh '+local_filename, shell=True, check=True, universal_newlines=True)
    output = sp.getoutput(CURRENT_PATH+'/generateIndexInfo.sh '+local_filename)
    output = output.split()
    total_lines = str(af.only_numerics(output[-3]))

    # 2. UPLOAD FILES TO THE BUCKET
    remote_filename = INDEXES_PREIX+file_name

    print(f'Uploading {local_filename}i to cos://{bucket_name}/{INDEXES_PREIX}')
    with open(f'{local_filename}i', 'rb') as fl:
        storage.put_object(bucket_name, f'{remote_filename}i', fl)

    print(f'Uploading {local_filename}i.info to cos://{bucket_name}/{INDEXES_PREIX}')
    with open(f'{local_filename}i.info', 'rb') as fl:
        storage.put_object(bucket_name, f'{remote_filename}i.info', fl)

    print(f'Uploading {local_filename}i_tab.info to cos://{bucket_name}/{INDEXES_PREIX}')
    with open(f'{local_filename}i_tab.info', 'rb') as fl:
        storage.put_object(bucket_name, f'{remote_filename}i_tab.info', fl)

    os.remove(f'{local_filename}i')
    os.remove(f'{local_filename}i.info')
    os.remove(f'{local_filename}i_tab.info')

    os.chdir(CWD)

    return total_lines


def download_index_files(bucket_name, file_name, storage=None):
    """
    Downloads index files of a given fastq file if not present in the local machine
    """
    os.chdir(LOCAL_TMP)

    storage = Storage() if not storage else storage
    print(f'\n--> Downloading {file_name} index files')

    remote_filename = INDEXES_PREIX+file_name

    if not os.path.isfile(f'{file_name}i'):
        remote_filename_i = f'{remote_filename}i'
        obj_stream = storage.get_object(bucket_name, remote_filename_i, stream=True)
        with open(f'{file_name}i', 'wb') as fl:
            shutil.copyfileobj(obj_stream, fl)

    if not os.path.isfile(f'{file_name}i.info'):
        remote_filename_i = f'{remote_filename}i.info'
        obj_stream = storage.get_object(bucket_name, remote_filename_i, stream=True)
        with open(f'{file_name}i.info', 'wb') as fl:
            shutil.copyfileobj(obj_stream, fl)

    if not os.path.isfile(f'{file_name}i_tab.info'):
        remote_filename_i = f'{remote_filename}i_tab.info'
        obj_stream = storage.get_object(bucket_name, remote_filename_i, stream=True)
        with open(f'{file_name}i_tab.info', 'wb') as fl:
            shutil.copyfileobj(obj_stream, fl)

    os.chdir(CWD)


def chunk_complete_gzfile(bucket_name, file_name, lines):
    """
    This function creates the partitions of x 'LINES' of the compressed file,
    unzips them and stores them in the bucket.
    """
    storage = Storage()

    # 1 DOWNLOAD INDEX FILES
    download_index_files(bucket_name, file_name, storage)

    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    print('\n--> Generating chunks')
    os.chdir(LOCAL_TMP)
    total_lines = af.get_total_lines(file_name)
    block_length = str(lines)
    sp.run(CURRENT_PATH+'/generateChunks.sh '+file_name+' '+block_length+' '+total_lines,
           shell=True, check=True, universal_newlines=True)
    chunks, chunk_counter = af.read_chunks_info(file_name)

    print(chunks)

    # 3 RETRIEVE CHUNKS FROM BUCKET AND UNZIP THEM
    for chunk in chunks:
        print("\n--> Processing chunk {}... ".format(chunk['number']))

        byte_range = f"{int(chunk['start_byte'])-1}-{int(chunk['end_byte'])}"
        obj_stream = storage.get_object(bucket_name, file_name, extra_get_args={'Range': f'bytes={byte_range}'}, stream=True)

        local_chunk_filename = os.path.join(LOCAL_TMP, file_name.replace('.fastq.gz', f'_chunk{chunk["number"]}.fastq'))
        local_chunk_filename_gz = f"{local_chunk_filename}.gz"

        with open(local_chunk_filename_gz, 'wb') as fl:
            shutil.copyfileobj(obj_stream, fl)

        cmd = f'gztool -I {file_name}i -n {chunk["start_byte"]} -L {chunk["start_line"]} {local_chunk_filename_gz} | head -{block_length} > {local_chunk_filename}'
        sp.run(cmd, shell=True, check=True, universal_newlines=True)

        print(f'Uploading {local_chunk_filename} to cos://{bucket_name}/{CHUNKS_PREIX}')
        with open(local_chunk_filename, 'rb') as fl:
            remote_chunk_filename = CHUNKS_PREIX+file_name.replace('.fastq.gz', f'_chunk{chunk["number"]}.fastq')
            storage.put_object(bucket_name, remote_chunk_filename, fl)

        os.remove(local_chunk_filename)
        os.remove(local_chunk_filename_gz)

    print(str(chunk_counter)+" chunks decompressed.")

    os.chdir(CWD)


def preprocess_chunk_complete_gzfile(bucket_name, file_name, lines):
    """
    The function takes the gzip file, creates the necessary index files for
    partitioning and stores them in the bucket. Then it creates the partitions
    of x 'LINES' of the compressed file, unzips them and stores them in the bucket.
    """
    # 1 GENERATING THE INDEX AND INFORMATION FILES AND UPLOADING TO THE BUCKET
    preprocess_gzfile(bucket_name, file_name)

    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    chunk_complete_gzfile(bucket_name, file_name, lines)


def retrieve_random_chunk_gzfile(bucket_name, file_name, start_line, end_line):
    """
    The function retrieves a random chunk defined by 'start_line' and 'end_line'
    of the gzip file stored in the bucket, unzips it and stores it back in the bucket.
    """
    # 1 DOWNLOAD INDEX FILES
    download_index_files(bucket_name, file_name)

    # 1 GETTING CHUNK BYTE RANGE
    os.chdir(LOCAL_TMP)
    sp.run(CURRENT_PATH+'/randomChunkRange.sh '+file_name+' '+start_line+' '+end_line,
           shell=True, check=True, universal_newlines=True)
    chunk = af.read_chunk_info_random(file_name, start_line, end_line)

    # 2 RETRIEVE CHUNK FROM BUCKET AND UNZIP IT
    remote_file_name = file_name.replace(LOCAL_TMP+'/', '')
    storage = Storage()
    byte_range = f"{int(chunk['start_byte'])-1}-{int(chunk['end_byte'])}"
    obj_stream = storage.get_object(bucket_name, remote_file_name, extra_get_args={'Range': f'bytes={byte_range}'}, stream=True)

    local_chunk_filename = os.path.join(LOCAL_TMP, file_name.replace('.fastq.gz', f'_chunk{chunk["number"]}.fastq'))
    local_chunk_filename_gz = f"{local_chunk_filename}.gz"

    with open(local_chunk_filename_gz, 'wb') as fl:
        shutil.copyfileobj(obj_stream, fl)

    block_length = str(int(end_line) - int(start_line) + 1)
    cmd = f'gztool -I {file_name}i -n {chunk["start_byte"]} -L {chunk["start_line"]} {local_chunk_filename_gz} | head -{block_length} > {local_chunk_filename}'
    sp.run(cmd, shell=True, check=True, universal_newlines=True)

    print(f'Uploading {local_chunk_filename} to cos://{bucket_name}/{CHUNKS_PREIX}')
    with open(local_chunk_filename, 'rb') as fl:
        remote_chunk_filename = CHUNKS_PREIX+file_name.replace('.fastq.gz', f'_chunk{chunk["number"]}.fastq')
        storage.put_object(bucket_name, remote_chunk_filename, fl)

    os.remove(local_chunk_filename)
    os.remove(local_chunk_filename_gz)

    print("Chunk decompressed")

    os.chdir(CWD)


def iterdata_bucket_fasta_fastq(bucket_name, fasta_pattern, fastq_pattern):
    """
    Generates all possible combinations of fasta and fastq chunk objects
    """
    # 1 RETRIEVE KEYS OF THE BUCKET MATCHING THE PREFIX PATTERN AND ITER THROUGH THEM
    storage = Storage()
    list_fasta = storage.list_keys(bucket_name, prefix=fasta_pattern)
    list_fastq = storage.list_keys(bucket_name, prefix=CHUNKS_PREIX+'/'+fastq_pattern)

    iterdata = []
    for fasta_key in list_fasta:
        for fastq_key in list_fastq:
            iterdata.append({'fasta_chunk': fasta_key, 'fastq_chunk': fastq_key})
    return iterdata


def create_iterdata_from_info_files(bucket_name, fasta_file_prefix, fastq_file_name, lines):
    """
    Creates the lithops iterdata from the fasta chunks and the fastq index files
    """
    storage = Storage()
    # 1 DOWNLOAD FASTQ INDEX FILES
    download_index_files(bucket_name, fastq_file_name, storage)

    os.chdir(LOCAL_TMP)
    total_lines = af.get_total_lines(fastq_file_name)
    total_lines = str(int(total_lines) + 1)

    list_fasta = storage.list_keys(bucket_name, prefix=fasta_file_prefix)

    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    print('\n--> Generating chunks')
    block_length = str(lines)
    sp.run(CURRENT_PATH+'/generateChunks.sh '+fastq_file_name+' '+block_length+' '+total_lines,
           shell=True, check=True, universal_newlines=True)
    chunks, chunk_counter = af.read_chunks_info(fastq_file_name)

    list_fastq = []
    for chunk in chunks:
        list_fastq.append((fastq_file_name, chunk))

    iterdata = []
    for fasta_key in list_fasta:
        for fastq_key in list_fastq:
            iterdata.append({'fasta_chunk': fasta_key, 'fastq_chunk': fastq_key})

    os.chdir(CWD)

    return iterdata
