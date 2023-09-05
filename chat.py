import gc
import os
import random
import json
import torch
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from database import save_unanswered_question, exibir_perguntas_nao_respondidas
from transformers import AutoModel, AutoTokenizer
from model import BERT_Arch
import re
import pickle
import transformers
import sklearn
with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

if os.path.exists('intents.xlsx'):
    df = pd.read_excel('intents.xlsx')
else:
    data = []
    for intent in intents['intents']:
        tag = intent['tag']
        for pattern in intent['patterns']:
            data.append({'text': pattern, 'label': tag})

    df = pd.DataFrame(data)
    df.to_excel('intents.xlsx', index=False)

if os.path.exists('label_encoder.pkl'):
    with open('label_encoder.pkl', 'rb') as f:
        le = pickle.load(f)
else:
    le = LabelEncoder()
    df['label'] = le.fit_transform(df['label'])
    with open('label_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

tokenizer = AutoTokenizer.from_pretrained('tokenizer_directory')
bert = AutoModel.from_pretrained('bert_directory')

FILE = "bert_model.pth"
checkpoint = torch.load(FILE)

label_counts = checkpoint['label_counts']

model = BERT_Arch(bert, label_counts)
model.load_state_dict(checkpoint['model_state_dict'])
model = model.to(device)
model.eval()

bot_name = "Carol"

def get_prediction(str):
    str = re.sub(r'[^a-zA-Z\s]', '', str)
    test_text = [str]
    model.eval()

    tokens_test_data = tokenizer(
        test_text,
        max_length=64,
        padding='max_length',
        truncation=True,
        return_token_type_ids=False
    )
    test_seq = torch.tensor(tokens_test_data['input_ids'])
    test_mask = torch.tensor(tokens_test_data['attention_mask'])

    preds = None
    with torch.no_grad():
        preds = model(test_seq.to(device), test_mask.to(device))
    preds = preds.detach().cpu().numpy()
    preds = np.argmax(preds, axis=1)
    print("Intent Identified: ", le.inverse_transform(preds)[0])
    return le.inverse_transform(preds)[0]


def get_response(msg, username, registration):
    pred = get_prediction(msg)
    tokens = tokenizer.encode_plus(msg, max_length=64, padding='max_length', truncation=True, return_tensors='pt')
    input_ids = tokens['input_ids'].to(device)
    attention_mask = tokens['attention_mask'].to(device)
    output = model(input_ids, attention_mask)
    predicted = torch.argmax(output, dim=1)
    prob = torch.softmax(output, dim=1)[0][predicted].item()
    print('probabilidade', prob)
    result = "Desculpe, não consegui encontrar uma resposta adequada."
    if prob > 0.7:
        for i in intents['intents']:
            if i["tag"] == pred:
                print("tag", pred)
                result = random.choice(i['responses'])
                break
        return result, pred
    else:
        print("prob3", prob)
        save_unanswered_question(msg, username, registration)
        exibir_perguntas_nao_respondidas()
        return f"Enviamos a pergunta ao tutor e logo mais ele responderá", pred


def reload_model():
    global model

    # Limpar a memória do modelo antes de recarregar
    del model
    gc.collect()

    checkpoint = torch.load(FILE)
    label_counts = checkpoint['label_counts']

    model = BERT_Arch(checkpoint['bert'], label_counts)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()

    print("Model reloaded.")

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    username = 'dsadas'
    registration = 2323
    while True:
        # sentence = "do you use credit cards?"
        sentence = input("You: ")
        if sentence == "quit":
            break
        resp = get_response(sentence,username,registration)


