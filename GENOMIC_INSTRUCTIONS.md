Genotic example instructions
===================

genomics_example.py
-----------------------------------

In order to be able to execute genomics_example.py:

1. Set correctly your BUCKET_NAME, fasta_chunks_prefix, fastq_file name:

```python
BUCKET_NAME = 'damianbucket'  # change-me
fasta_chunks_prefix = 'DUMMY_split_' # change-me
fastq_file = '1c-12S_S96_L001_R1_001.fastq.gz' # change-me
```
2. Upload the necessary files to COS for the example to run:

<table>
<tr>
<th align="center">
<img width="400" height="1px">
<p> 
<small>
<a href=".md">Necessary files</a>
</small>
</tr>

<tr>
<td>

```python
file.fastq.gz
split_A.fasta
split_B.fasta
split_C.fasta
      .
      .
      .
split_X.fasta
genomics/indexes/file.fastq.gzi
genomics/indexes/file.fastq.gzi.info
genomics/indexes/file.fastq.gzi_tab.info
genomics/references/sequence.fa
genomics/references/sequence.fa.fai
genomics/references/sequence.gem
```
</td>
</tr>

</table>

3. Run from your UNIX machine

```bash
$ python3 genomics_example.py
```
