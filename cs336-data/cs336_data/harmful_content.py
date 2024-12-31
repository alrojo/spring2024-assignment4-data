from typing import Any
import numpy as np
import fasttext
fasttext.FastText.eprint = lambda x: None

nsfw_path = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/jigsaw_fasttext_bigrams_nsfw_final.bin"
toxic_speech_path = "/home/sasha/classes/cs336/spring2024-assignment4-data/dumps/jigsaw_fasttext_bigrams_hatespeech_final.bin"

nsfw_model = fasttext.load_model(nsfw_path)
toxic_speech_model = fasttext.load_model(toxic_speech_path)

def classify_nsfw(text: str) -> tuple[Any, float]:
    labels, probabilities = nsfw_model.predict(text)
    label = labels[0].replace('__label__', '')
    probability = np.clip(probabilities[0], 0, 1)
    return label, probability

def classify_toxic_speech(text: str) -> tuple[Any, float]:
    labels, probabilities = toxic_speech_model.predict(text)
    label = labels[0].replace('__label__', '')
    probability = np.clip(probabilities[0], 0, 1)
    return label, probability

if __name__=='__main__':
    for i in range(1, 40+1):
        file_path = f"out/extract_warc{i}.txt" 
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read().replace('\n', '')
            nsfw_label, nsfw_probability = classify_nsfw(text_content)
            toxic_speech_label, toxic_speech_probability = classify_toxic_speech(text_content)
            print("@@@@@@@@@@@@")
            print(text_content)
            print("@@@@@@@@@@@@")
            print(f"{i}: {nsfw_label}, {nsfw_probability} | "
                  f"{toxic_speech_label}, {toxic_speech_probability}")
            _ = input("next?")
