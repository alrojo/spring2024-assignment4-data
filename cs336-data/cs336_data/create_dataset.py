#import concurrent.futures
import os
import pathlib
import json
from glob import glob
from xopen import xopen
from tqdm import tqdm
from fastwarc.warc import ArchiveIterator, WarcRecordType
from cs336_data.extract_text import extract_text_from_html_bytes
from cs336_data.identify_language import identify_language
from cs336_data.gopher import gopher_quality_filter
from cs336_data.quality import classify_quality
from cs336_data.deduplication import exact_line_deduplication
from cs336_data.minhash_deduplication import minhash_deduplication

WARC_PATH = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/CC-MAIN-20180420081400-20180420101400-00118.warc.gz"
WARC2_PATH = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/CC-MAIN-2-20180420081400-20180420101400-00118.warc.gz"
output_directory_path = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/cleaned"
staging1 = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/staging1"
staging2 = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/staging2"

warc_filepaths = [WARC_PATH, WARC2_PATH]
filenames = [os.path.splitext(os.path.basename(path))[0] for path in warc_filepaths]
staging_paths = [os.path.join(staging1, filename) for filename in filenames]
print(staging_paths)
def read_warc_file(file_path: str):
    with xopen(file_path, "rb") as f:
        for record in ArchiveIterator(f, record_types=WarcRecordType.response):
            if record.http_headers and record.http_headers.status_code == 200:
                response_data = record.reader.read()
                yield response_data
            else:
                yield None
def get_data_from_warc(path):
    print(path)
    records = read_warc_file(path)
    warc_samples = []
    #i=0
    for record in tqdm(records):
        #i+=1
        #if i==1000:
        #    break
        if record is None:
            continue
        text = extract_text_from_html_bytes(record)
        lang, prob = identify_language(text)
        # only consider english
        if not (prob > 0.6 and lang=="en"):
            continue
        # gopher quality check
        if not gopher_quality_filter(text):
            continue
        quality, _ = classify_quality(text) 
        if not quality == "wiki":
            continue 
        text = "\n".join(line for line in text.splitlines() if line.strip())
        warc_samples.append(text)
    return warc_samples

def process_single_warc_file(input_path: str, staging_path: str):
    warc_samples = get_data_from_warc(input_path)
    for e, warc_sample in enumerate(warc_samples):
        _staging_path = "%s_%d.txt" % (staging_path, e+1)
        with open(_staging_path, "w") as f:
            f.write(warc_sample)
    return True

data = process_single_warc_file(warc_filepaths[0], staging_paths[0])
pre_deduplication = glob("%s/*" % staging1)
exact_line_deduplication(pre_deduplication, staging2)
pre_minhash = glob("%s/*" % staging2)
minhash_deduplication(pre_minhash, 500, 50, 5, 0.8, output_directory_path)
post_minhash = glob("%s/*" % output_directory_path)

"""
# Set up the executor
num_cpus = len(os.sched_getaffinity(0))
executor = concurrent.futures.ProcessPoolExecutor(max_workers=num_cpus)
futures = []
for warc_filepath in warc_filepaths:
    # For each WARC filepath, submit a job to the executor and get a future back
    warc_filename = str(pathlib.Path(warc_filepath).name)
    future = executor.submit(
        process_single_warc_file,
        warc_filepath,
        os.path.join(output_directory_path, warc_filepath)
    )
    # Store the futures
    futures.append(future)

# Iterate over the completed futures as they finish, using a progress bar
# to keep track of progress.
for future in tqdm(
    concurrent.futures.as_completed(futures),
    total=len(warc_filepaths),
):
    output_file = future.result()
    print(f"Output file written: {output_file}")
"""
