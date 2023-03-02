import random
import json
import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

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

bot_name = "Sam"


def fallback_response():
    subject = tags[fallback_subject_index]
    print(f"Sorry, I'm not sure what you mean. Do you mean '{subject}'? (yes or no)")
    response = input().lower()
    if response == "yes":
        for intent in intents["intents"]:
            if intent["tag"] == subject:
                return random.choice(intent["responses"])
    else:
        return "Please rephrase your question."

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

    global fallback_subject_index
    if prob.item() < 0.99:
        max_prob = 0
        max_index = None
        for i, p in enumerate(probs[0]):
            if p.item() > max_prob and p.item() >= 0.75:
                max_prob = p.item()
                max_index = i
        if max_index is not None:
            fallback_subject_index = max_index
            return fallback_response()

    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])

    fallback_subject_index = predicted.item()
    return fallback_response()


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)
