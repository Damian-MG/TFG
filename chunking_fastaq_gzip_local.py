from lithops import Storage
import subprocess as sp
import os.path

BUCKET_NAME = 'damianbucket'  # change-me, REMEMBER TO DELETE FILES FROM BUCKET WHEN REPROCESSING
BUCKET_LINK = 'https://damianbucket.s3.eu-de.cloud-object-storage.appdomain.cloud/' # change-me


# This program takes a gzfile stored locally in the machine generates an index and information files for it,
# uploads them to an IBM Cloud Storage bucket to perform the partioning of the gzfile
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
            list.append({'number':(counter+1), 'start_line':str(info[0]), 'finish_line':str(info[1]), 'start_byte':str(info[2]), 'finish_byte':str(info[3])})
            counter+=1
    return list,counter


# MAIN PROGRAM
if __name__ == '__main__':

    # 1 GENERATING THE INDEX AND INFORMATION FILES AND UPLOADING TO THE BUCKET
    file,lines = gzfile_info()
    file = ('1c-12S_S96_L001_R1_001.fastq.gz')
    #sp.run('./generateUploadIndexInfoBucket.sh '+file+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True)
    sp.run('./generateUploadIndexInfo.sh '+file, shell=True, check=True, universal_newlines=True)
    output = sp.getoutput('./generateUploadIndexInfoBucket.sh '+file)
    output = output.split()
    total_lines = str(only_numerics(output[-3]))
    block_lenght = str(lines)
    

    # 2 GENERATING LINE INTERVAL LIST AND GETTING CHUNK'S BYTE RANGES
    sp.run('./generateChunks.sh '+file+' '+block_lenght+' '+total_lines+' '+BUCKET_NAME, shell=True, check=True, universal_newlines=True) 
    chunk, chunk_counter = read_chunks_info(file)
    print(chunk)
    print(chunk_counter)

    # 3 RETRIEVE CHUNKS FROM BUCKET AND UNZIP THEM
    #for i in range():
    #print(chunk[0]['start_byte'])
    #chunk_gzdata = storage.get_object(BUCKET_NAME, file, extra_get_args={'Range': 'bytes=9-909613'})
    #print(len(chunk_gzdata))  # will show 100
    #chunk_file = f'test3.gz'
    #with open(f'{chunk_file}', 'wb') as chunk_f:
    #    chunk_f.write(chunk_gzdata)

       












    # Get the index and save it locally
    #index_data = storage.get_object(BUCKET_NAME,file+'i')
    #print(index_data)
    # Esto es realmente necesario? Ya lo tenemos localmente
    #index_file = f'hola'+file+'i'
    #with open(f'{index_file}', 'wb') as index_f:
    #    index_f.write(index_data)
    #print(index_data)

    # Get the first block chunk:
    #chunk_gzdata = get_chunk(chunk_counter, blocks)
    #print(len(chunk_gzdata))  # will show 100
    
    # get the index and save it locally
    # index_data = storage.get_object(local, file+'i.info')

    #intervals = interval_list(10000,96520)
    #sp.run('./extraer.sh '+file, shell=True, check=True, universal_newlines=True)
    


# 
#def get_chunk(i, blocks):
#    byte_range = 'bytes='+str(MIN_BLOCK_LENGHT*i*blocks)+'-'+str(MAX_BLOCK_LENGTH*(i+1)*blocks)
#    print(byte_range)
#    chunk = storage.get_object(BUCKET_NAME, file, extra_get_args={'Range': byte_range})
#    return 
