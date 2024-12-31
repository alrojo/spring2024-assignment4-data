from typing import Any
import glob
import numpy as np
import fasttext
fasttext.FastText.eprint = lambda x: None

path_to_model = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/lid.176.bin"

model = fasttext.load_model(path_to_model)

def identify_language(text: str) -> tuple[Any, float]:
    clean_text = text.replace('\n', ' ')
    labels, probabilities = model.predict(clean_text)
    language = labels[0].replace('__label__', '')
    probability = np.clip(probabilities[0], 0, 1)
    return language, probability

if __name__=='__main__':
    for i in range(1, 20+1):
        file_path = f"out/extract_warc{i}.txt" 
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
            language, probability = identify_language(text_content)
            print("@@@@@@@@@@@@")
            print(text_content.strip("\n"))
            print("@@@@@@@@@@@@")
            print(f"{i}: {language}, {probability}")
            _ = input("next?")
