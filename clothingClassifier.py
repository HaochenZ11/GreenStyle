#Note: model originally trained on Google Colaboratory

import numpy as np
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import DataLoader, TensorDataset
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
import matplotlib.pyplot as plt

torch.manual_seed(1)

#drive.mount('/content/gdrive')  # mount google drive

def get_data():
    #path = '/content/gdrive/My Drive/Colab Notebooks/SheHacks/Clothing_Dataset'
    path = 'Clothing_Dataset'
    data = torchvision.datasets.ImageFolder(
        root=path,
        transform=transforms.Compose(
            [transforms.Resize((400, 533)), transforms.ToTensor()])
    )
    return data

data = get_data()

def data_loader(data, batch_size):
    labels = torch.tensor(data.targets)
    print("labels: ", labels)
    train_inds = []
    val_inds = []
    test_inds = []

    for i in range(len(data.classes)):
        targets = (labels == i).nonzero()  # gets indices in this class

        split1 = int(len(targets) * 0.6)
        split2 = int(len(targets) * 0.8)

        # put 60% into train, 20% into val, 20% into test
        train_targets = targets[:split1]
        val_targets = targets[split1:split2]
        test_targets = targets[split2:]

        train_inds.extend(train_targets)
        val_inds.extend(val_targets)
        test_inds.extend(test_targets)

    # creates random sampler from the indices for each set
    train_sampler = SubsetRandomSampler(train_inds)
    val_sampler = SubsetRandomSampler(val_inds)
    test_sampler = SubsetRandomSampler(test_inds)

    print(len(train_inds))
    print(len(val_inds))
    print(len(test_inds))

    # creates each data loader for training, validation, and test data
    train_loader = DataLoader(data, batch_size=batch_size, sampler=train_sampler)
    val_loader = DataLoader(data, batch_size=batch_size, sampler=val_sampler)
    test_loader = DataLoader(data, batch_size=batch_size, sampler=test_sampler)

    return train_loader, val_loader, test_loader

train_loader, val_loader, test_loader = data_loader(data, 64)

import os
import torchvision.models

def get_features(data):
    alexnet = torchvision.models.alexnet(pretrained=True)

    # Main folder to save
    #master_path = '/content/gdrive/My Drive/Colab Notebooks/SheHacks/Features'
    master_path = 'Features'

    train_path = os.path.join(master_path, 'train')
    val_path = os.path.join(master_path, 'val')

    # load the datasets
    batch_size = 1  # save 1 file at a time, hence batch_size = 1
    train_loader, val_loader, test_loader = data_loader(data, batch_size=batch_size)

    classes = ['bottoms', 'dresses', 'shoes', 'tops']

    # save training features to folder as tensors
    n = 0
    for img, label in iter(train_loader):
        features = alexnet.features(img)
        features_tensor = torch.from_numpy(features.detach().numpy())  # creates feature tensor

        folder_name = train_path + '/' + str(classes[label])
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)

        torch.save(features_tensor.squeeze(0), folder_name + '/' + str(n) + '.tensor')
        n += 1

    n = 0
    for img, label in iter(val_loader):
        features = alexnet.features(img)
        features_tensor = torch.from_numpy(features.detach().numpy())

        folder_name = val_path + '/' + str(classes[label])
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)

        torch.save(features_tensor.squeeze(0), folder_name + '/' + str(n) + '.tensor')
        n += 1

    # Main folder to load from
    train_data = torchvision.datasets.DatasetFolder(train_path, loader=torch.load, extensions=('.tensor'))
    val_data = torchvision.datasets.DatasetFolder(val_path, loader=torch.load, extensions=('.tensor'))

    # Prepare training and validation data loaders
    batch_size = 64
    num_workers = 1
    train_features = torch.utils.data.DataLoader(train_data, batch_size=batch_size,
                                                 num_workers=num_workers, shuffle=True)
    val_features = torch.utils.data.DataLoader(val_data, batch_size=batch_size,
                                               num_workers=num_workers, shuffle=True)

    train_iter = iter(train_features)
    features, labels = train_iter.next()
    return alexnet

alexnet = get_features(data)

class TransferNet(nn.Module):
    def __init__(self):
        super(TransferNet, self).__init__()
        self.conv1 = nn.Conv2d(256, 64, 3)
        self.pool = nn.MaxPool2d(2, 2)  # f = 2, stride = 2
        self.fc1 = nn.Linear(4 * 6 * 64, 80)
        self.fc2 = nn.Linear(80, 4)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = x.view(-1, 4 * 6 * 64)  # flatten feature data
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def get_accuracy(model, data_loader, batch_size):  # new get_accuracy function that uses alexnet features
    correct = 0
    total = 0
    for imgs, labels in iter(data_loader):

        if use_cuda and torch.cuda.is_available():
            imgs = imgs.cuda()
            labels = labels.cuda()

        features = alexnet.features(imgs)  # compute alexnet features
        output = model(features)

        # select index with maximum prediction score
        pred = output.max(1, keepdim=True)[1]
        correct += pred.eq(labels.view_as(pred)).sum().item()
        total += imgs.shape[0]
    return correct / total


def transfer_train(net, train_loader, val_loader, batch_size, learning_rate, epochs,
                   weight_decay):  # trains the model with AlexNet features

    #savepath1 = '/content/gdrive/My Drive/Colab Notebooks/SheHacks/model1.pth'
    #savepath2 = '/content/gdrive/My Drive/Colab Notebooks/SheHacks/model2.pth'
    savepath1 = 'model1.pth'
    savepath2 = 'model2.pth'

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=learning_rate, momentum=0.9, weight_decay=weight_decay)

    train_acc = []
    losses = []
    iters = []
    val_acc = []

    n = 0
    for i in range(epochs):
        for images, labels in iter(train_loader):  # iterates over each batch

            # To Enable GPU Usage
            if use_cuda and torch.cuda.is_available():
                # print("GPU enabled")
                images = images.cuda()
                labels = labels.cuda()

            features = alexnet.features(images)  # compute alexnet features
            output = net(features)  # input features into CNN classifier

            loss = criterion(output, labels)  # CE loss
            loss.backward()
            optimizer.step()  # adjust weights
            optimizer.zero_grad()

            iters.append(n)
            losses.append(float(loss) / batch_size)  # average loss over batch
            train_acc.append(get_accuracy(net, train_loader, batch_size))  # training accuracy
            val_acc.append(get_accuracy(net, val_loader, batch_size))  # validation accuracy
            n = n + 1

            print(("Iteration {}: Train acc: {}, Train loss: {} |").format(
                n,
                train_acc[n - 1],
                losses[n - 1]))

    print("Final Training Accuracy: {}".format(train_acc[-1]))
    print("Final Validation Accuracy: {}".format(val_acc[-1]))

    plt.title("Training Curve")
    plt.plot(iters, losses, label="Train")
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    plt.show()

    plt.title("Training Curve")
    plt.plot(iters, train_acc, label="Train")
    plt.plot(iters, val_acc, label="Validation")
    plt.xlabel("Iterations")
    plt.ylabel("Training Accuracy")
    plt.legend(loc='best')
    plt.show()

    torch.save(transferNet.state_dict(), savepath1)
    torch.save(transferNet, savepath2)
    return net


transferNet = TransferNet()
use_cuda = True
if use_cuda and torch.cuda.is_available():
    print("GPU Available")
    alexnet.features.cuda()
    transferNet.cuda()

transferNet = transfer_train(transferNet, train_loader, val_loader, 64, 0.005, 4, 0.0005)

test_acc = get_accuracy(transferNet, test_loader, 64)

print(test_acc)

