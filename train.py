import numpy as np
import json
# *-* encoding: utf-8 *-*
import torch
import pandas as pd
import torch.nn as nn
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import compute_class_weight
from torch.optim import lr_scheduler
from torch.utils.data import Dataset, DataLoader, TensorDataset, RandomSampler
from transformers import BertTokenizerFast, AutoModel, BertTokenizer, BertModel, AutoTokenizer
from torchinfo import summary
from transformers import AdamW
from model import BERT_Arch
import re
import random

with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

# Prepare data for DataFrame
data = []
for intent in intents['intents']:
    tag = intent['tag']
    for pattern in intent['patterns']:
        data.append({'text': pattern, 'label': tag})

df = pd.DataFrame(data)
df.to_excel('intents.xlsx', index=False)

df = pd.read_excel("intents.xlsx")
label_counts = df['label'].value_counts()

le = LabelEncoder()
df['label'] = le.fit_transform(df['label'])
# check class distribution
n_counts = df['label'].value_counts(normalize=True)
train_text, train_labels = df['text'], df['label']

tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
tokenizer.save_pretrained('tokenizer_directory')
bert = AutoModel.from_pretrained('neuralmind/bert-base-portuguese-cased')
bert.save_pretrained('bert_directory')

max_length = 128

tokens_train = tokenizer(
    train_text.tolist(),
    max_length=max_length,
    padding="max_length",
    truncation=True,
    return_token_type_ids=False
)

# for train set
train_seq = torch.tensor(tokens_train['input_ids'])
train_mask = torch.tensor(tokens_train['attention_mask'])
train_y = torch.tensor(train_labels.tolist())

batch_size = 32
train_data = TensorDataset(train_seq, train_mask, train_y)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# freeze all the parameters. This will prevent updating of model weights during fine-tuning.
for param in bert.parameters():
    param.requires_grad = False
model = BERT_Arch(bert, label_counts)
# push the model to GPU
model = model.to(device)

# summary(model)

optimizer = AdamW(model.parameters(), lr=1e-3, no_deprecation_warning=True)
class_wts = compute_class_weight('balanced', classes=np.unique(train_labels), y=train_labels)

# convert class weights to tensor
weights = torch.tensor(class_wts, dtype=torch.float)
weights = weights.to(device)
# loss function
cross_entropy = nn.NLLLoss(weight=weights)

# empty lists to store training and validation loss of each epoch
train_losses = []
# number of training epochs
epochs = 150
# We can also use learning rate scheduler to achieve better results
lr_sch = lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.1)


def train():
    model.train()
    total_loss = 0

    total_preds = []

    for step, batch in enumerate(train_dataloader):
        if step % 50 == 0 and not step == 0:
            print('  Batch {:>5,}  of  {:>5,}.'.format(step, len(train_dataloader)))

        batch = [r.to(device) for r in batch]
        sent_id, mask, labels = batch
        preds = model(sent_id, mask)
        loss = cross_entropy(preds, labels)

        total_loss = total_loss + loss.item()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        optimizer.step()

        optimizer.zero_grad()

        preds = preds.detach().cpu().numpy()
        total_preds.append(preds)
        avg_loss = total_loss / len(train_dataloader)

        total_preds = np.concatenate(total_preds, axis=0)
        return avg_loss, total_preds


for epoch in range(epochs):
    print('\n Epoch {:} / {:}'.format(epoch + 1, epochs))

    # train model
    train_loss, _ = train()

    # append training and validation loss
    train_losses.append(train_loss)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print(f'\nTraining Loss: {train_loss:.3f}')


def get_prediction(str):
    str = re.sub(r'[^a-zA-Z\s]', '', str)
    test_text = [str]
    model.eval()

    tokens_test_data = tokenizer(
        test_text,
        max_length=64,
        padding="max_length",
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


torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'epoch': epochs,
    'train_losses': train_losses,
    'label_encoder': le,
    'tokenizer': tokenizer,
    'label_counts': label_counts,
}, 'bert_model.pth')

print("Model saved.")
