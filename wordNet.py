from PyMultiDictionary import MultiDictionary

from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)

prompt = "love"
dictionary = MultiDictionary()
print(dictionary.synonym('en', prompt))
candidate_labels = dictionary.synonym('en', prompt)

result = classifier(prompt, candidate_labels)
prompt_word = result['labels']
print(prompt_word)