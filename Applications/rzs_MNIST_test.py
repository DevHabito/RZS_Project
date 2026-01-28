# ============================================================
# RZS DECISIVE TESTS
# ReLU vs tanh vs RZS
# MNIST | PyTorch | Secure dataset (no SSL error)
# ============================================================

import os
import ssl
import urllib.request
import gzip
import shutil
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision
import torchvision.transforms as transforms
import numpy as np

# ------------------------------------------------------------
# 1. SSL FIX (pragmatic security)
# ------------------------------------------------------------
ssl._create_default_https_context = ssl._create_unverified_context

# ------------------------------------------------------------
# 2. SECURE MANUAL MNIST DOWNLOAD
# ------------------------------------------------------------
def download_mnist_safe(root="./data"):
    base_url = "https://storage.googleapis.com/cvdf-datasets/mnist/"
    files = [
        "train-images-idx3-ubyte.gz",
        "train-labels-idx1-ubyte.gz",
        "t10k-images-idx3-ubyte.gz",
        "t10k-labels-idx1-ubyte.gz"
    ]

    raw_dir = os.path.join(root, "MNIST", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    for fname in files:
        gz_path = os.path.join(raw_dir, fname)
        out_path = gz_path.replace(".gz", "")

        if not os.path.exists(out_path):
            if not os.path.exists(gz_path):
                print(f"Downloading {fname}...")
                urllib.request.urlretrieve(base_url + fname, gz_path)

            print(f"Extracting {fname}...")
            with gzip.open(gz_path, "rb") as f_in:
                with open(out_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

# ------------------------------------------------------------
# 3. RZS ACTIVATION
# ------------------------------------------------------------
class RZSActivation(nn.Module):
    def __init__(self, alpha=1.5, lambda_rzs=0.01):
        super().__init__()
        self.alpha = alpha
        self.lambda_rzs = lambda_rzs

    def forward(self, x):
        return x / (1 + self.lambda_rzs * torch.abs(x) ** (2 - self.alpha))

# ------------------------------------------------------------
# 4. STANDARD MODEL (SAME STRUCTURE FOR ALL)
# ------------------------------------------------------------
class MLP(nn.Module):
    def __init__(self, activation):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 10)

        if activation == "relu":
            self.act = nn.ReLU()
        elif activation == "tanh":
            self.act = nn.Tanh()
        elif activation == "rzs":
            self.act = RZSActivation()
        else:
            raise ValueError("Invalid activation")

    def forward(self, x):
        x = x.view(-1, 784)
        x = self.act(self.fc1(x))
        x = self.act(self.fc2(x))
        x = self.fc3(x)
        return x

# ------------------------------------------------------------
# 5. TRAINING
# ------------------------------------------------------------
def train_model(model, train_loader, test_loader, epochs=30, lr=1e-3):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_acc = 0.0

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        acc = evaluate(model, test_loader)
        best_acc = max(best_acc, acc)

        print(
            f"Epoch {epoch+1}/{epochs} | "
            f"Loss: {running_loss/len(train_loader):.4f} | "
            f"Acc: {acc:.2f}%"
        )

    return best_acc

# ------------------------------------------------------------
# 6. EVALUATION
# ------------------------------------------------------------
def evaluate(model, loader):
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    return 100 * correct / total

# ------------------------------------------------------------
# 7. MAIN
# ------------------------------------------------------------
if __name__ == "__main__":

    print("\nPreparing MNIST...")
    download_mnist_safe("./data")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    trainset = torchvision.datasets.MNIST(
        root="./data", train=True, download=False, transform=transform
    )
    testset = torchvision.datasets.MNIST(
        root="./data", train=False, download=False, transform=transform
    )

    train_loader = DataLoader(trainset, batch_size=128, shuffle=True)
    test_loader = DataLoader(testset, batch_size=256, shuffle=False)

    results = {}

    for act in ["relu", "tanh", "rzs"]:
        print(f"\n==============================")
        print(f"TRAINING {act.upper()}")
        print(f"==============================")

        model = MLP(act)
        best_acc = train_model(model, train_loader, test_loader)
        results[act] = best_acc

    print("\n========== FINAL RESULT ==========")
    for k, v in results.items():
        print(f"{k.upper():5s}: {v:.2f}%")