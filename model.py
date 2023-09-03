import torch
import torch.nn as nn
from transformers import AutoModel


class BERT_Arch(nn.Module):
    def __init__(self, bert, label_counts):
        super(BERT_Arch, self).__init__()
        self.bert = bert
        self.label_counts = len(label_counts)  # Obtém o número de classes únicas

        # Camada de dropout
        self.dropout = nn.Dropout(0.2)

        # Função de ativação ReLU
        self.relu = nn.ReLU()
        # Camada densa
        self.fc1 = nn.Linear(768, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, self.label_counts)  # Use self.label_counts aqui
        # Função de ativação softmax
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, sent_id, mask):
        # Passa as entradas para o modelo
        cls_hs = self.bert(sent_id, attention_mask=mask)[0][:, 0]
        x = self.fc1(cls_hs)
        x = self.relu(x)
        x = self.dropout(x)

        x = self.fc2(x)
        x = self.relu(x)
        x = self.dropout(x)

        # Camada de saída
        x = self.fc3(x)

        # Aplica a ativação softmax
        x = self.softmax(x)
        return x
