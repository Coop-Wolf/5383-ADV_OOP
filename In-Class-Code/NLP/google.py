import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

url = "https://msutexas.edu"
response = requests.get(url)

print(len(response.text))
soup = BeautifulSoup(response.text, 'html.parser')


text = ""

pieces_of_inforation = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p'])
for piece_of_info in pieces_of_inforation:
    text += piece_of_info.get_text(" ", strip=True) + " "
    # print(piece_of_info)

sw = stopwords.words("english")
# print(sw)

clean_words = []


words = word_tokenize(text)

for word in words:
    if word not in sw:
        clean_words.append(word)

clean_clean_words = []
lemmatizer = WordNetLemmatizer()
for cw in clean_words:
    ccw = lemmatizer.lemmatize(cw.lower())
    clean_clean_words.append(ccw)


print("clean words")
print(clean_words)
print(len(words))
print(len(clean_words))

print("clean clean words")
print(clean_clean_words)
print(len(clean_clean_words))


unique_clean_clean_words = set(clean_clean_words)
print("unique clean words")
print(unique_clean_clean_words)
print(len(unique_clean_clean_words))
# print(words)
# print(len(words))


# print(stopwords)
# print(pieces_of_inforation)

# print(soup)


# with open("msu.html", "w", encoding="utf-8") as file:
#     file.write(response.text)