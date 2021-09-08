FROM python:3.8-slim-buster

ENV FLASK_PROXY_PORT 8080
# Set up miniconda path 
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN apt-get update \
    # add some packages required for the pip install
    && apt-get install -y \
        gcc \
        zlib1g-dev \
        libxslt-dev \
        libxml2-dev \
        zip \
        unzip \
        make \
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

# install miniconda
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

# Install samtools and vcftools
RUN conda install -c bioconda -y samtools=1.11
RUN conda install -c bioconda gem3-mapper

COPY requirements.txt requirements.txt
COPY SiNPle-0.5 /bin/SiNPle-0.5
COPY mpileup_merge_reduce.sh bin/mpileup_merge_reduce.sh
COPY test.txt test.txt

RUN chmod u+x /bin/SiNPle-0.5
RUN chmod u+x bin/mpileup_merge_reduce.sh
RUN pip install --upgrade pip setuptools six && pip install --no-cache-dir -r requirements.txt

# create action working directory
RUN mkdir -p /action \
    && mkdir -p /actionProxy \
    && mkdir -p /pythonAction

ADD https://raw.githubusercontent.com/apache/openwhisk-runtime-docker/8b2e205c39d84ed5ede6b1b08cccf314a2b13105/core/actionProxy/actionproxy.py /actionProxy/actionproxy.py
ADD https://raw.githubusercontent.com/apache/openwhisk-runtime-python/3%401.0.3/core/pythonAction/pythonrunner.py /pythonAction/pythonrunner.py

CMD ["/bin/bash", "-c", "cd /pythonAction && python -u pythonrunner.py"]