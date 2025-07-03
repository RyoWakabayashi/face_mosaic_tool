import torch
import torchvision

# 1. モデルの準備（pretrainedをTrueにするとCOCOの重み付き）
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

# 2. 任意でモデルをCUDAに移す（GPUがある場合）
# model = model.cuda()

# 3. モデルを .pt 形式で保存
torch.save(model, "models/fasterrcnn_model.pt")

print("モデルがfasterrcnn_model.ptとして保存されました。")
