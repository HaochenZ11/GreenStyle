import numpy as np
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision.transforms import transforms
import matplotlib.pyplot as plt
from PIL import Image
import torch.backends.cudnn as cudnn
import torchvision.models

alexnet = torchvision.models.alexnet(pretrained=True)

class TransferNet(nn.Module):
    def __init__(self):
        super(TransferNet, self).__init__()
        self.conv1 = nn.Conv2d(256, 64, 3)
        self.pool = nn.MaxPool2d(2, 2)  # f = 2, stride = 2
        self.fc1 = nn.Linear(4 * 6 * 64, 80)  # 256 output features (for each filter?)
        self.fc2 = nn.Linear(80, 4)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = x.view(-1, 4 * 6 * 64)  # flatten feature data
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def classify_image(imgpath):
    classes = ['bottoms', 'dresses', 'shoes', 'tops']
    modelpath = 'model2.pth'
    #model = TransferNet()
    #image2 = '1a3b3d48-e500-44e4-9fb3-dadde06ea48b.jpg'

    origimage = Image.open(imgpath)
    image = origimage.resize((400, 533))

    transform = transforms.ToTensor()
    image = transform(image)
    image = image.type(torch.FloatTensor)
    im = image[None, :, :]
    feature = alexnet.features(im)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.load(modelpath, map_location=torch.device('cpu'))
    model = model.to(device)
    if device == 'cuda':
        model = torch.nn.DataParallel(model)
        cudnn.benchmark = True

    model.eval()
    output = model(feature)

    pred = output.max(1, keepdim=True)[1]
    return pred

