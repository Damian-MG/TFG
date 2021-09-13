# Python 3.6
#FROM continuumio/miniconda3:4.5.4 

# Python 3.7
#FROM continuumio/miniconda3:4.7.12

# Python 3.8
FROM continuumio/miniconda3:4.9.2

# Python 3.9
#FROM continuumio/miniconda3:4.10.3

# YOU MUST PIN THE PYTHON VERSION TO PREVENT IT TO BE UPDATED
# For python 3.6 use "python==3.6.5"
# For python 3.7 use "python==3.7.4"
# For python 3.8 use "python==3.8.5"
# For python 3.9 use "python==3.9.5"
RUN echo "python==3.8.5" >> /opt/conda/conda-meta/pinned

ENV FLASK_PROXY_PORT 8080

RUN apt-get --allow-releaseinfo-change update \
    # add some packages required for the pip install
    && apt-get install -y \
        gcc \
        zlib1g-dev \
        libxslt-dev \
        libxml2-dev \
        zip \
        unzip \
        make \
        zlib1g-dev \
    # required elements for samtools installation
        autoconf \ 
        automake \ 
        perl \
        libbz2-dev \
        liblzma-dev \
        wget \
    # cleanup package lists, they are not used anymore in this image
    && rm -rf /var/lib/apt/lists/* \
    && apt-cache search linux-headers-generic


# Add your Conda required packages here. Ensure "conda clean --all" at 
# the end to remove temporary data. One "RUN" line is better than multiple
# ones in terms of image size.
# Install samtools and vcftools
RUN conda update -n base conda && conda install -c bioconda -y samtools=1.11 gem3-mapper && conda clean --all


COPY requirements.txt requirements.txt
COPY SiNPle-0.5 /bin/SiNPle-0.5
COPY mpileup_merge_reduce.sh /bin/mpileup_merge_reduce.sh
COPY test.txt test.txt

RUN chmod ugo+x /bin/SiNPle-0.5 && chmod ugo+x /bin/mpileup_merge_reduce.sh
RUN pip install --upgrade pip setuptools six && pip install --no-cache-dir -r requirements.txt


# Download, compile and install gztool
RUN wget https://github.com/circulosmeos/gztool/archive/refs/tags/v1.4.2.zip && \
    unzip v1.4.2.zip && rm v1.4.2.zip && cd gztool-1.4.2 && gcc -O3 -o gztool gztool.c -lz -lm && \
    cp gztool /bin/gztool && chmod ugo+x /bin/gztool


# create action working directory
RUN mkdir -p /action \
    && mkdir -p /actionProxy \
    && mkdir -p /pythonAction

ADD https://raw.githubusercontent.com/apache/openwhisk-runtime-docker/8b2e205c39d84ed5ede6b1b08cccf314a2b13105/core/actionProxy/actionproxy.py /actionProxy/actionproxy.py
ADD https://raw.githubusercontent.com/apache/openwhisk-runtime-python/3%401.0.3/core/pythonAction/pythonrunner.py /pythonAction/pythonrunner.py

CMD ["/bin/bash", "-c", "cd /pythonAction && python -u pythonrunner.py"]