import logging
from pathlib import Path
from typing import Any

from ultralytics import YOLO

from app.config import settings

logger = logging.getLogger(__name__)


class YOLOService:
    """Singleton wrapper around Ultralytics YOLOv8 for person detection."""

    def __init__(self) -> None:
        self._model: YOLO | None = None

    def load(self) -> None:
        """Load the model into memory (called once at startup)."""
        if self._model is None:
            self._model = YOLO(settings.yolo_model)
            logger.info("YOLO model '%s' loaded into memory.", settings.yolo_model)

    def is_loaded(self) -> bool:
        return self._model is not None

    def detect_people(self, image_path: Path) -> list[dict[str, Any]]:
        """
        Run inference on *image_path* and return a list of person detections.

        Each detection is a dict:
            {
                "id":         int,    # 1-based index
                "x":          float,  # left edge, % of image width
                "y":          float,  # top edge, % of image height
                "w":          float,  # width,    % of image width
                "h":          float,  # height,   % of image height
                "confidence": float,  # [0, 1]
                "x_abs":      int,    # pixel left
                "y_abs":      int,    # pixel top
                "w_abs":      int,    # pixel width
                "h_abs":      int,    # pixel height
            }
        """
        if self._model is None:
            self.load()

        # classes=[0] restricts detection to "person" (COCO class 0)
        results = self._model(  # type: ignore[misc]
            str(image_path),
            classes=[0],
            conf=settings.confidence_threshold,
            verbose=False,
        )

        detections: list[dict[str, Any]] = []
        for result in results:
            img_h, img_w = result.orig_shape
            for idx, box in enumerate(result.boxes, start=1):
                x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
                w_abs = x2 - x1
                h_abs = y2 - y1

                detections.append(
                    {
                        "id": idx,
                        "x": round(x1 / img_w * 100, 2),
                        "y": round(y1 / img_h * 100, 2),
                        "w": round(w_abs / img_w * 100, 2),
                        "h": round(h_abs / img_h * 100, 2),
                        "confidence": round(float(box.conf[0]), 3),
                        # Absolute pixel coords kept for the crop step
                        "x_abs": x1,
                        "y_abs": y1,
                        "w_abs": w_abs,
                        "h_abs": h_abs,
                    }
                )

        logger.info("YOLO detected %d person(s) in '%s'.", len(detections), image_path.name)
        return detections


# Module-level singleton — imported by other services
yolo_service = YOLOService()
