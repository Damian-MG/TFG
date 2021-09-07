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


def gzfile_info():
    file = input('Indicate the name of the gz file to chunk:')
    lines = input('Indicate the number of lines to retrieve for a chunk:')
    return file, lines


# Function to get input information
def gzfile_info_random():
    file = input('Indicate the name of the gz file to chunk:')
    start_line = input('Indicate the start line of the chunk:')
    end_line = input('Indicate the end line of the chunk:')
    return file, start_line, end_line


# Function to remove all non-numeric characters from a string
def only_numerics(string):
    string_type = type(string)
    return string_type().join(filter(string_type.isdigit, string))


def get_total_lines(file_name):
    """
    gets the total number of lines from the index_tab.info file
    """
    with open(file_name+'i_tab.info', 'r') as f:
        for last_line in f:
            pass

    return last_line.split(' ')[1]


# Function to read information of the chunks from a file
def read_chunks_info(file):
    chunk_list = []
    counter = 0
    with open(file+'.chunks.info', 'r') as f:
        for line in f:
            print('Chunk info:'+str(counter))
            info = line.split()
            chunk_list.append({'number': (counter+1), 'start_line': str(info[0]),
                               'end_line': str(info[1]), 'start_byte': str(info[2]),
                               'end_byte': str(info[3])})
            counter += 1
    return chunk_list, counter


# Function to read information of the chunks from a file
def read_chunk_info_random(file, start_line, end_line):
    with open(file+'.random_chunk_'+start_line+'_'+end_line+'.info', 'r') as f:
        for line in f:
            info = line.split()
            chunk = {'number': (1), 'start_line': str(info[0]), 'end_line': str(info[1]),
                     'start_byte': str(info[2]), 'end_byte': str(info[3])}
    return chunk
