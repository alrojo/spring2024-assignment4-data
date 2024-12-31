from nltk import word_tokenize

MINIMUM_WORDS = 50 
MAXIMUM_WORDS = int(1e5)
MINIMUM_AVG_WORD = 3
MAXIMUM_AVG_WORD = 10
MAX_PERCENT_ELLIPSIS = 0.3
MIN_PERCENT_ALPH = 0.8

has_char = lambda word : any(char.isalpha() for char in word)

def gopher_quality_filter(text: str) -> bool:
    # setup lines and words
    lines = text.split("\n") 
    words = []
    for line in lines:
        words += word_tokenize(line) 

    # 1. remove less than 50 and more than 100k words
    num_words = len(words)
    if num_words < MINIMUM_WORDS or num_words > MAXIMUM_WORDS:
#        print("too many or little words! ", num_words)
        return False

    # 2. check average word length between 3 to 10
    mean_word_length = sum([len(word) for word in words]) / num_words
    cond1 = mean_word_length < MINIMUM_AVG_WORD
    cond2 = mean_word_length > MAXIMUM_AVG_WORD
    if cond1 or cond2:
#        print("word length is too short or long!", mean_word_length)
        return False

    # 3. more than 30% of lines ending with an ellipsis (”...”)
    num_lines = len(lines)
    mean_ending_ellipsis = sum([int(line.endswith("...")) for line in lines]) / num_lines
    if mean_ending_ellipsis > MAX_PERCENT_ELLIPSIS:
#        print("too many sentences ending in ...!", mean_ending_ellipsis)
        return False

    # 4. less than 80% of words with at least one alphabetic character
    mean_contain_alph = sum([int(has_char(word)) for word in words]) / num_words
    if mean_contain_alph < MIN_PERCENT_ALPH:
#        print("failed! words without charactors..!", mean_contain_alph)
        return False

    # all works, then return
    return True

if __name__=='__main__':
    for i in range(1, 40+1):
        file_path = f"out/extract_warc{i}.txt" 
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
            quality = "Accept" if gopher_quality_filter(text_content) else "Reject"
            print("@@@@@@@@@@@@")
            print(text_content.replace('\n', ''))
            print("@@@@@@@@@@@@")
            print(f"{i}: {quality}")
            _ = input("next?")
