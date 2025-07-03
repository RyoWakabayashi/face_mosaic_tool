import torch
import torchvision
from torchvision.models.detection import (
    fasterrcnn_resnet50_fpn,
    FasterRCNN_ResNet50_FPN_Weights,
)
from torchvision.transforms import functional as F
import numpy as np
import os
import json


class ObjectDetector:
    def __init__(
        self,
        model_name="fasterrcnn_resnet50_fpn",
        device=None,
        label_names=None,
        score_thresh=0.5,
        model_path=None,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        weights = FasterRCNN_ResNet50_FPN_Weights.DEFAULT

        # モデルパスが指定されていればそれをロード
        if model_path is None:
            # modelsディレクトリ配下の.pthファイルを自動検出
            models_dir = os.path.join(os.path.dirname(__file__), "../../../models")
            models_dir = os.path.abspath(models_dir)
            if os.path.isdir(models_dir):
                candidates = [f for f in os.listdir(models_dir) if f.endswith(".pt")]
                if candidates:
                    model_path = os.path.join(models_dir, candidates[0])

        if model_path is not None and os.path.isfile(model_path):
            print(f"ローカル学習済みモデルをロード: {model_path}")
            self.model = torch.load(
                model_path, map_location=self.device, weights_only=False
            )
            if isinstance(self.model, torch.nn.Module):
                self.model.eval()
            else:
                raise ValueError("ロードしたモデルがtorch.nn.Moduleではありません")

        else:
            print(f"事前学習済みモデルをロード: {model_name} ({weights})")
            self.model = fasterrcnn_resnet50_fpn(pretrained=True, weights=weights)
            self.model.eval()

        self.model.to(self.device)
        self.score_thresh = score_thresh

        # ラベル名の決定
        labels_path = os.path.join(
            os.path.dirname(__file__), "../../../models/labels.json"
        )
        labels_path = os.path.abspath(labels_path)
        if label_names is not None:
            self.label_names = label_names
        elif os.path.isfile(labels_path):
            with open(labels_path, "r", encoding="utf-8") as f:
                self.label_names = json.load(f)
            print(
                f"labels.jsonからラベル名を読み込み: {self.label_names[:5]} ... (全{len(self.label_names)}件)"
            )
        else:
            self.label_names = weights.meta["categories"]
            print(
                f"デフォルトラベルを使用: {self.label_names[:5]} ... (全{len(self.label_names)}件)"
            )

    def detect(self, image, target_labels=None):
        # image: numpy.ndarray (HWC, BGR or RGB)
        # target_labels: list of str or None
        img_tensor = F.to_tensor(image).to(self.device)
        with torch.no_grad():
            outputs = self.model([img_tensor])[0]
        boxes, labels, scores = outputs["boxes"], outputs["labels"], outputs["scores"]

        print(f"検出された物体数: {len(boxes)}")

        results = []
        for box, label, score in zip(boxes, labels, scores):
            if score < self.score_thresh:
                continue

            label_name = self.label_names[label]
            if (target_labels is None) or (label_name in target_labels):
                results.append(
                    {
                        "box": box.cpu().numpy().astype(int),
                        "label": label_name,
                        "score": float(score.cpu().numpy()),
                    }
                )

        print(f"検出結果: {len(results)} 個の物体")

        return results
