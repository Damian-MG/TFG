from lithops import Storage
import subprocess as sp
import os.path

BUCKET_NAME = 'damianbucket'  # change-me, REMEMBER TO DELETE FILES FROM BUCKET WHEN REPROCESSING
BUCKET_LINK = 'https://damianbucket.s3.eu-de.cloud-object-storage.appdomain.cloud/' # change-me

# This program takes a gzfile stored in a bucket and retrieves a chunk determined by a line interval

# Function to get input information
def gzfile_info():
    file = input('Indicate the name of the gz file to chunk:')
    start_line = input('Indicate the start line of the chunk:')
    end_line = input('Indicate the end line of the chunk:')
    return file,start_line,end_line

# Function to read information of the chunks from a file
def read_chunk_info(file, start_line, end_line):
    with open(file+'.random_chunk_'+start_line+'_'+end_line+'.info', 'r') as f:
        for line in f:
            info = line.split()
            chunk = {'number':(1), 'start_line':str(info[0]), 'end_line':str(info[1]), 'start_byte':str(info[2]), 'end_byte':str(info[3])}
    return chunk

if __name__ == '__main__':
   
    file,start_line,end_line=gzfile_info()
    block_length = int(end_line) - int(start_line) + 1
    block_length = str(block_length)
    sp.run('./randomChunkRange.sh '+file+' '+start_line+' '+end_line+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True)
    chunk = read_chunk_info(file, start_line, end_line)
    sp.run('./downloadDecompressChunk.sh '+file+' '+BUCKET_LINK+' '+BUCKET_NAME+' '+chunk['start_line']+' '+block_length+' '+chunk['start_byte']+' '+chunk['end_byte'], shell=True, check=True, universal_newlines=True)
    

