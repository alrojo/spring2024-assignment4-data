from typing import Any
import random
import fasttext as ft
from xopen import xopen
import sys
import subprocess
from glob import glob
import json
from cs336_data.extract_text import extract_text_from_html_bytes
from cs336_data.identify_language import identify_language
from cs336_data.gopher import gopher_quality_filter
from tqdm import tqdm

from fastwarc.warc import ArchiveIterator, WarcRecordType

WIKI_DIR = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/positive_samples"
GOLD_PATH = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/gold_samples.json"
WARC_PATH = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/CC-MAIN-20180420081400-20180420101400-00118.warc.gz"
TRAIN_PATH = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/train.txt"

def read_warc_file(file_path: str):
    with xopen(file_path, "rb") as f:
        for record in ArchiveIterator(f, record_types=WarcRecordType.response):
            if record.http_headers and record.http_headers.status_code == 200:
                response_data = record.reader.read()
                yield response_data
            else:
                yield None

def get_gold_samples(gold_folder, prefix="subsampled_positive_urls_*"):
    paths=glob("%s/%s" % (gold_folder, prefix))
    paths = paths
    gold_samples = []
    for e, path in enumerate(tqdm(paths)):
        records = read_warc_file(path)
        if records is None:
            continue
        for record in records:
            if record is None:
                continue
            text = extract_text_from_html_bytes(record)
            # only consider english
            lang, prob = identify_language(text)
            if not (prob > 0.5 and lang=="en"):
                continue
            # gopher quality assessment
            if not gopher_quality_filter(text):
                continue
            text = "\n".join(line for line in text.splitlines() if line.strip())
            gold_samples.append(text)
    return gold_samples


def get_gold(directory):
    samples = get_gold_samples(WIKI_DIR)
    gold_samples = []
    for sample in samples:
        gold_samples.append("__label__wiki %s" % (sample.replace("\n", " ")))
    return gold_samples

def get_warcs(path, num_negatives=1e16):
    records = read_warc_file(path)
    warc_samples = []
    for record in tqdm(records):
        if record is None:
            continue
        text = extract_text_from_html_bytes(record)
        lang, prob = identify_language(text)
        # only consider english
        if not (prob > 0.5 and lang=="en"):
            continue
        # gopher quality check
        if not gopher_quality_filter(text):
            continue
        text = "\n".join(line for line in text.splitlines() if line.strip())
        warc_samples.append(text.replace('\n', ' '))
        if len(warc_samples)>num_negatives:
            break
    return warc_samples

def save_file_txt(data_points, path):
    with open(path, 'w', encoding='utf-8') as file:
        for data_point in data_points[:-1]:
            file.write(data_point + '\n')
        file.write(data_points[-1])

if __name__=='__main__':
    num_negatives = 10000
    gold_samples = get_gold(WIKI_DIR)
    print("got %d gold" % len(gold_samples))
    warc_samples = get_warcs(WARC_PATH, num_negatives)
    negative_samples = ['__label__cc %s' % (txt) for txt in warc_samples]
    size_diff = len(negative_samples) - len(gold_samples)
    upsampled_gold_samples = gold_samples + random.choices(gold_samples, k=size_diff)
    # here
    train_set = negative_samples + upsampled_gold_samples
    print("saving %d data points" % len(train_set))
    save_file_txt(train_set, TRAIN_PATH)
