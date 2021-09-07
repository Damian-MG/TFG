import lithopsgenetics

BUCKET_NAME = 'josep-datasets'  # change-me, REMEMBER TO DELETE FILES FROM BUCKET WHEN REPROCESSING
BUCKET_REGION = 'us-east'

BUCKET_LINK = f'https://{BUCKET_NAME}.s3.{BUCKET_REGION}.cloud-object-storage.appdomain.cloud/' # change-me


# This program takes a gzfile stored locally in the machine generates an index and information files for it,
# uploads them to an IBM Cloud Storage bucket to perform the partioning of the gzfile

# MAIN PROGRAM
if __name__ == '__main__':

    # FUNCTION preprocess_chunk_complete_file(BUCKET_NAME, BUCKET_LINK, file, lines)
    lithopsgenetics.preprocess_chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, '1c-12S_S96_L001_R1_001.fastq.gz', '100000')

    # FUNCTION retrieve_random_chunk_gzfile(BUCKET_NAME, BUCKET_LINK, file, start_line, end_line)
    #lithopsgenetics.retrieve_random_chunk_gzfile(BUCKET_NAME, BUCKET_LINK, '1c-12S_S96_L001_R1_001.fastq.gz', '101000', '150000')

    # FUNCTION preprocess_gzfile(BUCKET_NAME, file)
    #lithopsgenetics.preprocess_gzfile(BUCKET_NAME, '1c-12S_S96_L001_R1_001.fastq.gz')

    # FUNCTION chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, file, lines, total_lines)
    #lithopsgenetics.chunk_complete_gzfile(BUCKET_NAME, BUCKET_LINK, '1c-12S_S96_L001_R1_001.fastq.gz', '100000', '309956')

    # FUNCTION iter_data_bucket_fasta_fastq(lithops_storage, BUCKET_NAME, fasta_pattern, fastq_pattern)
    #list = lithopsgenetics.iter_data_bucket_fasta_fastq(storage, BUCKET_NAME, 'DUMMY_split_', '1c-12S_S96_L001_R1_001.fastq.gz_')
    #print(list)
