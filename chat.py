import random
import json
import torch
import numpy as np
from database import save_unanswered_question, exibir_perguntas_nao_respondidas
from sklearn.metrics.pairwise import cosine_similarity
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize, stem
import gc

global model, tags, all_words
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


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


def get_response(msg, username, registration):
    with open('intents.json', 'r', encoding='utf-8') as json_data:
        intents = json.load(json_data)
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                response = random.choice(intent['responses'])
                print("prob1", prob.item())
                print("tag", tag)
                return response, tag
    else:
        print("prob2", prob.item())
        similarities = []
        for intent in intents['intents']:
            # Imprimir o padrão original
            print(f"Original pattern: {intent['patterns'][0]}")
            intent_words = [stem(word) for word in tokenize(intent['patterns'][0])]
            # Imprimir o padrão após o pré-processamento de texto
            print(f"Preprocessed pattern: {intent_words}")
            intent_vector = bag_of_words(intent_words, all_words)
            # Imprimir a representação vetorial do padrão
            print(f"Pattern vector: {intent_vector}")
            similarity = cosine_similarity(X, intent_vector.reshape(1, -1))
            similarities.append(similarity)
            # Imprimir o valor de similaridade
            print(f"Similarity: {similarity}")
        max_similarity_idx = np.argmax(similarities)
        max_similarity = similarities[max_similarity_idx]

        if max_similarity > 0.4 and prob.item() > 0.5:
            print("similarity", max_similarity)
            tag = intents['intents'][max_similarity_idx]["tag"]
            return f"Desculpe, não tenho certeza sobre isso. Você está se referindo a '{tag}'?", tag
        else:
            print("prob3", prob.item())
            save_unanswered_question(msg, username, registration)
            exibir_perguntas_nao_respondidas()
            return f"Enviamos a pergunta ao tutor e logo mais ele responderá", tag


def reload_model():
    global model, all_words, tags

    # Limpar a memória do modelo antes de recarregar
    del model
    gc.collect()

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