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

CURRENT_PATH = str(pathlib.Path(__file__).parent.resolve())
LOCAL_TMP = os.path.realpath(tempfile.gettempdir())
REMOTE_PREIX = 'genomics/tmp'


def preprocess_gzfile(bucket_name, file):
    """
    The function takes the gzip file, creates the necessary index files
    for partitioning and stores them in the bucket.
    """
    # 1 GENERATING THE INDEX AND INFORMATION FILES AND UPLOADING TO THE BUCKET
    sp.run(CURRENT_PATH+'/generateIndexInfo.sh '+file+' '+bucket_name, shell=True, check=True, universal_newlines=True)
    output = sp.getoutput(CURRENT_PATH+'/generateIndexInfo.sh '+file)
    output = output.split()
    total_lines = str(af.only_numerics(output[-3]))

    # 2. UPLOAD FILES TO THE BUCKET
    storage = Storage()
    os.chdir(LOCAL_TMP)

    filename = file.replace(LOCAL_TMP+'/', '')

    print(f'Uploading {filename}i')
    with open(f'{filename}i', 'rb') as fl:
        storage.put_object(bucket_name, f'{REMOTE_PREIX}/{filename}i', fl)
    print(f'Uploading {filename}i.info')
    with open(f'{filename}i.info', 'rb') as fl:
        storage.put_object(bucket_name, f'{REMOTE_PREIX}/{filename}i.info', fl)
    print(f'Uploading {filename}i_tab.info')
    with open(f'{filename}i_tab.info', 'rb') as fl:
        storage.put_object(bucket_name, f'{REMOTE_PREIX}/{filename}i_tab.info', fl)

    return total_lines


def chunk_complete_gzfile(bucket_name, file_name, lines, total_lines):
    """
    This function creates the partitions of x 'LINES' of the compressed file,
    unzips them and stores them in the bucket.
    """
    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    print('\n--> Generating chunks')
    block_length = str(lines)
    sp.run(CURRENT_PATH+'/generateChunks.sh '+file_name+' '+block_length+' '+total_lines+' '+bucket_name,
           shell=True, check=True, universal_newlines=True)
    chunks, chunk_counter = af.read_chunks_info(file_name)

    print(chunks)

    # 3 RETRIEVE CHUNKS FROM BUCKET AND UNZIP THEM
    remote_file_name = file_name.replace(LOCAL_TMP+'/', '')
    for chunk in chunks:
        print("\n--> Processing chunk {}... ".format(chunk['number']))
        storage = Storage()
        byte_range = f"{int(chunk['start_byte'])-1}-{int(chunk['end_byte'])}"
        obj_stream = storage.get_object(bucket_name, remote_file_name, extra_get_args={'Range': f'bytes={byte_range}'}, stream=True)

        local_chunk_filename = f"{file_name}_{chunk['start_line']}.fastq"
        local_chunk_filename_gz = f"{local_chunk_filename}.gz"

        with open(local_chunk_filename_gz, 'wb') as fl:
            shutil.copyfileobj(obj_stream, fl)

        cmd = f'gztool -I {file_name}i -n {chunk["start_byte"]} -L {chunk["start_line"]} {local_chunk_filename_gz} | head -{block_length} > {local_chunk_filename}'
        sp.run(cmd, shell=True, check=True, universal_newlines=True)

        print(f'Uploading {local_chunk_filename} to bucket {bucket_name}')
        with open(local_chunk_filename, 'rb') as fl:
            remote_chunk_filename = REMOTE_PREIX+local_chunk_filename.replace(LOCAL_TMP, '')
            storage.put_object(bucket_name, remote_chunk_filename, fl)

        os.remove(local_chunk_filename)
        os.remove(local_chunk_filename_gz)

    print(str(chunk_counter)+" chunks decompressed.")


def preprocess_chunk_complete_gzfile(bucket_name, file_name, lines):
    """
    The function takes the gzip file, creates the necessary index files for
    partitioning and stores them in the bucket. Then it creates the partitions
    of x 'LINES' of the compressed file, unzips them and stores them in the bucket.
    """

    # 1 GENERATING THE INDEX AND INFORMATION FILES AND UPLOADING TO THE BUCKET
    total_lines = preprocess_gzfile(bucket_name, file_name)

    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    chunk_complete_gzfile(bucket_name, file_name, lines, total_lines)


def retrieve_random_chunk_gzfile(bucket_name, file_name, start_line, end_line):
    """
    The function retrieves a random chunk definded by 'start_line' and 'end_line'
    of the gzip file stored in the bucket, unzips it and stores it back in the bucket.
    """
    block_length = str(int(end_line) - int(start_line) + 1)

    # 1 GETTING CHUNK BYTE RANGE
    sp.run(CURRENT_PATH+'/randomChunkRange.sh '+file_name+' '+start_line+' '+end_line+' '+bucket_name, shell=True, check=True, universal_newlines=True)
    chunk = af.read_chunk_info_random(file_name, start_line, end_line)

    # 2 RETRIEVE CHUNK FROM BUCKET AND UNZIP IT
    remote_file_name = file_name.replace(LOCAL_TMP+'/', '')
    storage = Storage()
    byte_range = f"{int(chunk['start_byte'])-1}-{int(chunk['end_byte'])}"
    obj_stream = storage.get_object(bucket_name, remote_file_name, extra_get_args={'Range': f'bytes={byte_range}'}, stream=True)

    local_chunk_filename = f"{file_name}_{chunk['start_line']}.fastq"
    local_chunk_filename_gz = f"{local_chunk_filename}.gz"

    with open(local_chunk_filename_gz, 'wb') as fl:
        shutil.copyfileobj(obj_stream, fl)

    cmd = f'gztool -I {file_name}i -n {chunk["start_byte"]} -L {chunk["start_line"]} {local_chunk_filename_gz} | head -{block_length} > {local_chunk_filename}'
    sp.run(cmd, shell=True, check=True, universal_newlines=True)

    print(f'Uploading {local_chunk_filename} to bucket {bucket_name}')
    with open(local_chunk_filename, 'rb') as fl:
        remote_chunk_filename = REMOTE_PREIX+local_chunk_filename.replace(LOCAL_TMP, '')
        storage.put_object(bucket_name, remote_chunk_filename, fl)

    os.remove(local_chunk_filename)
    os.remove(local_chunk_filename_gz)

    print("Chunk decompressed")


def iterdata_bucket_fasta_fastq(bucket_name, fasta_pattern, fastq_pattern):
    """
    Generates all possible combinations of fasta and fastq chunk objects
    """
    # 1 RETRIEVE KEYS OF THE BUCKET MATCHING THE PREFIX PATTERN AND ITER THROUGH THEM
    storage = Storage()
    list_fasta = storage.list_keys(bucket_name, prefix=REMOTE_PREIX+'/'+fasta_pattern)
    list_fastq = storage.list_keys(bucket_name, prefix=REMOTE_PREIX+'/'+fastq_pattern)

    iter_data = []
    for fasta_key in list_fasta:
        for fastq_key in list_fastq:
            iter_data.append({'fasta_chunk': fasta_key, 'fastq_chunk': fastq_key})
    return iter_data
