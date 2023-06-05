import random
import json

import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize, stem

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Carol"


def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.8:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses']), tag
    else:
        similarities = []
        for intent in intents['intents']:
            intent_words = [stem(word) for word in tokenize(intent['patterns'][0])]
            intent_vector = bag_of_words(intent_words, all_words)
            similarity = cosine_similarity(X, intent_vector.reshape(1, -1))
            similarities.append(similarity)
        max_similarity_idx = np.argmax(similarities)
        max_similarity = similarities[max_similarity_idx]

        if max_similarity > 0.5:
            tag = intents['intents'][max_similarity_idx]["tag"]
            return f"Desculpe, não tenho certeza sobre isso. Você está se referindo a '{tag}'?", tag
        else:
            return f"Desculpe, não entendi o que você quis dizer. Você perguntou sobre '{tag}'...?", tag


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)
