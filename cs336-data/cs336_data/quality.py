import fasttext as ft

from typing import Any
import glob
import numpy as np
import fasttext
fasttext.FastText.eprint = lambda x: None

path_to_model = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/quality.bin"

model = fasttext.load_model(path_to_model)
def classify_quality(text: str, threshold=0.6) -> tuple[Any, float]:
    clean_text = text.replace('\n', ' ')
    labels, probabilities = model.predict(clean_text)
    labels = [label.replace('__label__', '') for label in labels]
    probability = np.clip(probabilities[0], 0, 1)
    label = labels[0]
    if label=="cc" and probability<0.6:
        label = "wiki"
        probability = 1-probability
    return label, probability

if __name__=='__main__':
    for i in range(1, 20+1):
        file_path = f"out/extract_warc{i}.txt" 
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
            quality, probability = classify_quality(text_content)
            print("@@@@@@@@@@@@")
            print(text_content.strip("\n"))
            print("@@@@@@@@@@@@")
            print(f"{i}: {quality}, {probability}")
            _ = input("next?")
