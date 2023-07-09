import json
import torch
import torch.nn as nn
import numpy as np
from model import NeuralNet
from torch.utils.data import Dataset, DataLoader
from startingWithNLTK import tokenize, stem, bag_of_words

with open('./LLMS/intents.json', 'r') as f :
    intents = json.load(f)

all_words = list()
tags = list()
xy = list()

for intent in intents['intents'] :
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns'] :
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

ignore_words = [i for i in "`~!@#$%^&*()-_=+[{]}\|;:'\",<.>/?"]
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))
#print(tags)

x_train = []
y_train = []
for (pattern_sentence, tag) in xy :
    bag = bag_of_words(pattern_sentence, all_words)
    x_train.append(bag)
    label = tags.index(tag)
    y_train.append(label)

x_train = np.array(x_train)
y_train = np.array(y_train)

class ChatDataset(Dataset) :
    def __init__(self) : 
        self.n_samples = len(x_train)
        self.x_data = x_train
        self.y_data = y_train

    def __getitem__(self, index) : 
        return self.x_data[index], self.y_data[index]
    
    def __len__(self) :
        return self.n_samples

batch_size = 8
hidden_size = 32
output_size = len(tags)
input_size = len(x_train[0])
learning_rate = 0.001
num_epochs = 5192

dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle =True)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

for epoch in range(num_epochs) :
    for (words, labels) in train_loader :
        words = words.to(device)
        labels = labels.to(device)

        outputs = model(words)
        loss =criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    if (epoch+1) % 100 == 0 : 
        print(f"epoch : {epoch+1}/{num_epochs}, loss : {loss.item()}")

print(f"final loss, loss = {loss.item()}")

data = {
    "model_state" : model.state_dict(),
    "input_size" : input_size,
    "hidden_size" : hidden_size,
    "output_size" : output_size,
    "all_words" : all_words,
    "tags" : tags
}

FILE = "data.pth"
torch.save(data, FILE)

print(f'Training complete, saved to {FILE}')