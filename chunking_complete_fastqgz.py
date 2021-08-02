from lithops import Storage
import subprocess as sp
import os.path

BUCKET_NAME = 'damianbucket'  # change-me, REMEMBER TO DELETE FILES FROM BUCKET WHEN REPROCESSING
BUCKET_LINK = 'https://damianbucket.s3.eu-de.cloud-object-storage.appdomain.cloud/' # change-me

# This program takes a gzfile stored locally in the machine generates an index and information files for it,
# uploads them to an IBM Cloud Storage bucket to perform the partioning of the gzfile

# Function to get input information
def gzfile_info():
    file = input('Indicate the name of the gz file to chunk:')
    lines = input('Indicate the number of lines to retrieve for a chunk:')
    return file,lines

# Function to remove all non-numeric characters from a string
def only_numerics(string):
    string_type = type(string)
    return string_type().join(filter(string_type.isdigit, string))

# Function to read information of the chunks from a file
def read_chunks_info(file):
    list = []
    counter = 0
    with open(file+'.chunks.info', 'r') as f:
        for line in f:
            print('Chunk info:'+str(counter))
            info = line.split()
            list.append({'number':(counter+1), 'start_line':str(info[0]), 'end_line':str(info[1]), 'start_byte':str(info[2]), 'end_byte':str(info[3])})
            counter+=1
    return list,counter


# MAIN PROGRAM
if __name__ == '__main__':

    # 1 GENERATING THE INDEX AND INFORMATION FILES AND UPLOADING TO THE BUCKET
    file,lines = gzfile_info()
    sp.run('./generateUploadIndexInfoBucket.sh '+file+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True)
    output = sp.getoutput('./generateUploadIndexInfoBucket.sh '+file)
    output = output.split()
    total_lines = str(only_numerics(output[-3]))
    block_length = str(lines)

    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    sp.run('./generateChunks.sh '+file+' '+block_length+' '+total_lines+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True) 
    chunk, chunk_counter = read_chunks_info(file)
    
    # 3 RETRIEVE CHUNKS FROM BUCKET AND UNZIP THEM
    for i in chunk:
        print("Processing first chunk... ",i['number'])
        sp.run('./downloadDecompressChunk.sh '+file+' '+BUCKET_LINK+' '+BUCKET_NAME+' '+i['start_line']+' '+block_length+' '+i['start_byte']+' '+i['end_byte'], shell=True, check=True, universal_newlines=True)


       