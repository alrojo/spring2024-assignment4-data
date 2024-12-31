import os
import textdistance
import nltk
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
import mmh3
from collections import defaultdict

def get_ngrams(text: str, ngram_length: int):
    tokens = word_tokenize(text)
    return list(ngrams(tokens, ngram_length))

def get_minhash_signature(text: str, _ngrams: list, num_hashes: int):
    if _ngrams:
        minhash_values = []
        for seed_value in range(num_hashes):
            # Convert each n-gram to string before hashing
            minhash_value = min(mmh3.hash(str(_ngram), seed=seed_value) for _ngram in _ngrams)
            minhash_values.append(minhash_value)
        return minhash_values
    return [-1]


def get_band(signature, band_index, r):
    start = band_index * r
    end = (band_index + 1) * r
    return signature[start:end]

def merge_into_clusters(doc1, doc2, clusters):
    found_cluster = None
    for cluster in clusters:
        if doc1 in cluster or doc2 in cluster:
            found_cluster = cluster
            break
    
    if found_cluster is not None:
        found_cluster.add(doc1)
        found_cluster.add(doc2)
    else:
        clusters.append({doc1, doc2})
    return clusters

def finalize_clusters(clusters):
    merged_clusters = []
    visited = set()
    for c1 in clusters:
        c1_frozen = frozenset(c1)
        if c1_frozen not in visited:
            merged_cluster = set(c1_frozen)  # start with c1
            for c2 in clusters:
                c2_frozen = frozenset(c2)
                if c2_frozen not in visited and not merged_cluster.isdisjoint(c2_frozen):
                    merged_cluster.update(c2_frozen)
                    visited.add(c2_frozen)
            visited.add(c1_frozen)
            merged_clusters.append(merged_cluster)

    return merged_clusters

def hash_band(band_values):
    band_str = "_".join(str(v) for v in band_values)
    return mmh3.hash(band_str, seed=42)

def minhash_deduplication(
    input_files: list[os.PathLike],
    num_hashes: int,
    num_bands: int,
    ngram_length: int,
    jaccard_threshold: float,
    output_directory: os.PathLike
):
    # 0. basic checks
    if num_hashes % num_bands != 0:
        raise ValueError("num_hashes must be divisible by num_bands.")
    r = num_hashes // num_bands

    # 1. read documents
    documents = {}
    for input_file in input_files:
        filename = os.path.basename(input_file)
        output_path = os.path.join(output_directory, filename)
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        documents[output_path] = {
            "text": text
        }

    # 2. generate n-grams
    for doc_key, doc_data in documents.items():
        _ngrams = get_ngrams(doc_data["text"], ngram_length)
        doc_data["ngrams"] = _ngrams

    # 3. compute MinHash signatures
    for doc_key, doc_data in documents.items():
        signature = get_minhash_signature(doc_data["text"], doc_data["ngrams"], num_hashes)
        doc_data["signature"] = signature

    # 4. LSH - Bucket documents that share the same band hash
    buckets = defaultdict(list)
    for doc_key, doc_data in documents.items():
        for band_index in range(num_bands):
            band_value = get_band(doc_data["signature"], band_index, r)
            bucket_hash = hash_band(band_value)
            buckets[bucket_hash].append(doc_key)

    # 5. collect candidate pairs
    candidate_pairs = set()
    for bucket_hash, docs_in_bucket in buckets.items():
        # Compare docs in the same bucket
        for i in range(len(docs_in_bucket)):
            for j in range(i+1, len(docs_in_bucket)):
                doc1 = docs_in_bucket[i]
                doc2 = docs_in_bucket[j]
                candidate_pairs.add((doc1, doc2))

    # 6. confirm duplicates with Jaccard similarity
    clusters = []
    visited_pairs = set()
    for (doc1, doc2) in candidate_pairs:
        if (doc1, doc2) not in visited_pairs and (doc2, doc1) not in visited_pairs:
            # Compare their signatures or original n-grams
            list1 = documents[doc1]["ngrams"]
            list2 = documents[doc2]["ngrams"]
            sim = textdistance.jaccard(list1, list2)
            if sim >= jaccard_threshold:
                merge_into_clusters(doc1, doc2, clusters)
            visited_pairs.add((doc1, doc2))
            visited_pairs.add((doc2, doc1))

    # 7. merge any overlapping clusters
    final_clusters = finalize_clusters(clusters)

    # 8. determine which documents to keep:
    #  keep exactly one doc from each cluster
    #  also keep any docs not in any cluster
    all_docs = set(documents.keys())
    clustered_docs = set().union(*final_clusters) if final_clusters else set()
    unclustered_docs = all_docs - clustered_docs  # docs that never appeared in a cluster

    unique_files = set()

    # one doc per cluster
    for cluster in final_clusters:
        sorted_cluster = sorted(cluster)  # pick a deterministic doc
        chosen_doc = sorted_cluster[0]
        unique_files.add(chosen_doc)

    # add all unclustered docs (these are not duplicates at all)
    unique_files |= unclustered_docs

    # 9. write out chosen docs to the output directory
    #    this ensures doc1 duplicates won't appear multiple times.
    for doc_key in unique_files:
        text = documents[doc_key]["text"]
        with open(doc_key, 'w', encoding='utf-8') as out_f:
            out_f.write(text)

    print("Deduplication complete.")
    print(f"Total documents: {len(documents)}")
    print(f"Unique documents: {len(unique_files)}")
    print(f"Number of clusters formed: {len(final_clusters)}")
