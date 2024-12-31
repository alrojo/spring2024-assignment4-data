from resiliparse.extract.html2text import extract_plain_text
from resiliparse.parse.encoding import detect_encoding, bytes_to_str
from resiliparse.parse.encoding import bytes_to_str

import gzip
import warcio 
def _extract_text_from_html_bytes(html_bytes: bytes) -> str | None:
    decoded = bytes_to_str(html_bytes, detect_encoding(html_bytes))
    plain_text = extract_plain_text(decoded)
    return plain_text

def _read_warc_file(warc_file_path : str):
    with gzip.open(warc_file_path, 'rb') as stream:
        for record in warcio.archiveiterator.ArchiveIterator(stream):
            if record.rec_type == 'response':
                url = record.rec_headers.get_header('WARC-Target-URI')
                content = record.content_stream().read()
                yield content

from resiliparse.parse.html import HTMLTree
from xopen import xopen
from fastwarc.warc import ArchiveIterator, WarcRecordType
from tqdm import tqdm
import sys

def __read_warc_file(file_path: str):
    with xopen(file_path, "rb") as f:
        for record in ArchiveIterator(f, record_types=WarcRecordType.response):
            yield record.reader.read()

def __extract_text_from_html_bytes(html_bytes: bytes) -> str:
    encoding = detect_encoding(html_bytes)
    html_bytes = HTMLTree.parse_from_bytes(html_bytes, encoding)
    return extract_plain_text(html_bytes, encoding)

read_warc_file = __read_warc_file
extract_text_from_html_bytes = __extract_text_from_html_bytes


if __name__=='__main__':
    input_path = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/CC-MAIN-20180420081400-20180420101400-00118.warc.gz"
    records = read_warc_file(input_path)
    
    # extract first 20 record and save as txt
    count = 0
    for record in records:
        if count > 40:
            break
        else:
            count += 1
            with open(f'out/extract_warc{count}.txt', 'w') as f:
                text = extract_text_from_html_bytes(record)
                f.write(text)
    print('Done')
