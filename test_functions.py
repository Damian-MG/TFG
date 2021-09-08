import lithopsgenetics
from lithops import Storage

BUCKET_NAME = 'josep-datasets'  # change-me, REMEMBER TO DELETE FILES FROM BUCKET WHEN REPROCESSING
TEST_FILE_NAME = '1c-12S_S96_L001_R1_001.fastq.gz'


# This program takes a gzfile stored locally in the machine generates an index and information files for it,
# uploads them to an IBM Cloud Storage bucket to perform the partioning of the gzfile

# MAIN PROGRAM
if __name__ == '__main__':

    # Upload test dataset to the bucket
    storage = Storage()
    try:
        storage.head_object(BUCKET_NAME, TEST_FILE_NAME)
    except Exception:
        print(f'Uploading data/{TEST_FILE_NAME} to cos://{BUCKET_NAME}/{TEST_FILE_NAME}')
        with open(f'data/{TEST_FILE_NAME}', 'rb') as fl:
            storage.put_object(BUCKET_NAME, TEST_FILE_NAME, fl)

    # FUNCTION preprocess_gzfile(BUCKET_NAME, file)
    lithopsgenetics.preprocess_gzfile(BUCKET_NAME, TEST_FILE_NAME)

    # FUNCTION preprocess_chunk_complete_file(BUCKET_NAME, BUCKET_LINK, file, lines)
    #lithopsgenetics.preprocess_chunk_complete_gzfile(BUCKET_NAME, TEST_FILE_NAME, '100000')

    # FUNCTION retrieve_random_chunk_gzfile(BUCKET_NAME, BUCKET_LINK, file, start_line, end_line)
    #lithopsgenetics.retrieve_random_chunk_gzfile(BUCKET_NAME, TEST_FILE_NAME, '101000', '150000')

    # FUNCTION chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, file, lines, total_lines)
    #lithopsgenetics.chunk_complete_gzfile(BUCKET_NAME, TEST_FILE_NAME, '100000', '309956')

    # FUNCTION iter_data_bucket_fasta_fastq(lithops_storage, BUCKET_NAME, fasta_pattern, fastq_pattern)
    #iterdata = lithopsgenetics.iterdata_bucket_fasta_fastq(BUCKET_NAME, 'DUMMY_split_', TEST_FILE_NAME+'_')
    #print(iterdata)

    iterdata = lithopsgenetics.create_iterdata_from_info_files(BUCKET_NAME, 'DUMMY_split_', TEST_FILE_NAME, 100000)
    print(iterdata)
