from fastapi import FastAPI
from pydantic import BaseModel
from collections import defaultdict, Counter
import random
import re
from typing import List
import spacy
import subprocess

# Try to load spaCy model, download if missing
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_md"])
    nlp = spacy.load("en_core_web_md")

# Create FastAPI instance
app = FastAPI()

# Example corpus for the Bigram model
corpus = [
    "The Count of Monte Cristo is a novel written by Alexandre Dumas.",
    "This is another example sentence.",
    "Bigram models are simple but effective."
]

# --- Bigram Model ---
class BigramModel:
    def __init__(self, corpus: List[str], lowercase: bool = True, seed: int = 42):
        random.seed(seed)
        self.lowercase = lowercase
        self.bigram = defaultdict(Counter)
        self._train(corpus)

    def _tokenize(self, text: str) -> List[str]:
        if self.lowercase:
            text = text.lower()
        return [t for t in re.split(r"\W+", text) if t]

    def _train(self, corpus: List[str]):
        for doc in corpus:
            tokens = self._tokenize(doc)
            for w1, w2 in zip(tokens, tokens[1:]):
                self.bigram[w1][w2] += 1

    def next_word(self, word: str) -> str:
        counts = self.bigram.get(word.lower() if self.lowercase else word)
        if not counts:
            return word
        return random.choices(list(counts.keys()), weights=counts.values())[0]

    def generate_text(self, start_word: str, length: int = 10) -> str:
        generated = [start_word]
        cur = start_word
        for _ in range(length):
            cur = self.next_word(cur)
            generated.append(cur)
        return " ".join(generated)

# Initialize bigram model
bigram_model = BigramModel(corpus)

# --- API Schemas ---
class TextGenerationRequest(BaseModel):
    start_word: str
    length: int

class EmbeddingRequest(BaseModel):
    text: str

# --- Routes ---
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/generate")
def generate_text(request: TextGenerationRequest):
    generated_text = bigram_model.generate_text(request.start_word, request.length)
    return {"generated_text": generated_text}

@app.post("/embed")
def embed_text(request: EmbeddingRequest):
    doc = nlp(request.text)
    return {"embedding": doc.vector.tolist()}
