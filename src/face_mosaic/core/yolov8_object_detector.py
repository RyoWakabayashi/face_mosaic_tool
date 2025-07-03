from ultralytics import YOLO
import os


class YoloV8ObjectDetector:
    def __init__(
        self, model_path=None, device=None, label_names=None, score_thresh=0.5
    ):
        # デフォルトパス
        if model_path is None:
            # models/yolov8/ ディレクトリ配下の.ptファイルを自動検出
            default_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../models/yolov8")
            )
            model_path = None
            if os.path.isdir(default_dir):
                candidates = [f for f in os.listdir(default_dir) if f.endswith(".pt")]
                if candidates:
                    model_path = os.path.join(default_dir, candidates[0])
            if model_path is None:
                model_path = "yolov8n.pt"  # ultralyticsのデフォルト

        self.device = device or (
            "cuda"
            if (
                hasattr(YOLO(model_path), "device")
                and YOLO(model_path).device.type == "cuda"
            )
            else "cpu"
        )
        self.model = YOLO(model_path)
        self.model.to(self.device)
        self.score_thresh = score_thresh

        if label_names is not None:
            self.label_names = label_names
        elif hasattr(self.model, "names"):
            self.label_names = self.model.names
        else:
            self.label_names = []

    def detect(self, image, target_labels=None):
        # image: numpy.ndarray (HWC, BGR or RGB)
        # target_labels: list of str or None
        results = self.model(image)
        detections = results[0]
        boxes = detections.boxes.xyxy.cpu().numpy()  # (N, 4)
        scores = detections.boxes.conf.cpu().numpy()  # (N,)
        labels = detections.boxes.cls.cpu().numpy().astype(int)  # (N,)
        out = []
        for box, label, score in zip(boxes, labels, scores):
            if score < self.score_thresh:
                continue
            label_name = self.label_names[label] if self.label_names else str(label)
            if (target_labels is None) or (label_name in target_labels):
                x1, y1, x2, y2 = box.astype(int)
                out.append(
                    {
                        "box": [x1, y1, x2, y2],
                        "label": label_name,
                        "score": float(score),
                    }
                )
        return out
