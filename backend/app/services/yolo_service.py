import logging
from pathlib import Path
from typing import Any

from ultralytics import YOLOWorld

from app.config import settings

logger = logging.getLogger(__name__)

# Open-vocabulary classes prompted into YOLO-World.
# "helmet" gives much higher detection confidence than "hard hat" on this model.
_CLASSES = ["helmet", "person"]
_PERSON_IDX = _CLASSES.index("person")
_HELMET_IDX = _CLASSES.index("helmet")

# Per-class minimum confidence: persons are detected reliably, helmets less so.
_PERSON_CONF = 0.40
_HELMET_CONF = 0.20


class YOLOService:
    """Singleton wrapper around YOLO-World for open-vocabulary detection.

    On the same image, returns both person bboxes AND helmet bboxes — the
    downstream pipeline matches helmets to persons by spatial overlap.
    """

    def __init__(self) -> None:
        self._model: YOLOWorld | None = None

    def load(self) -> None:
        if self._model is None:
            self._model = YOLOWorld(settings.yolo_model)
            self._model.set_classes(_CLASSES)
            logger.info(
                "YOLO-World loaded — model='%s' classes=%s",
                settings.yolo_model, _CLASSES,
            )

    def is_loaded(self) -> bool:
        return self._model is not None

    def detect(self, image_path: Path) -> dict[str, list[dict[str, Any]]]:
        """
        Run inference and return a dict with 'persons' and 'helmets' lists.

        Each entry has the shape used by the rest of the pipeline:
            {id, x%, y%, w%, h%, confidence, x_abs, y_abs, w_abs, h_abs}
        Helmet entries don't get an "id" field (they're matched to persons later).
        """
        if self._model is None:
            self.load()

        # Run with the lowest threshold; we filter per class below.
        results = self._model(  # type: ignore[misc]
            str(image_path),
            conf=min(_PERSON_CONF, _HELMET_CONF),
            verbose=False,
        )

        persons: list[dict[str, Any]] = []
        helmets: list[dict[str, Any]] = []

        for result in results:
            img_h, img_w = result.orig_shape
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
                w_abs = x2 - x1
                h_abs = y2 - y1
                entry: dict[str, Any] = {
                    "x":          round(x1 / img_w * 100, 2),
                    "y":          round(y1 / img_h * 100, 2),
                    "w":          round(w_abs / img_w * 100, 2),
                    "h":          round(h_abs / img_h * 100, 2),
                    "confidence": round(conf, 3),
                    "x_abs":      x1,
                    "y_abs":      y1,
                    "w_abs":      w_abs,
                    "h_abs":      h_abs,
                }
                if cls_id == _PERSON_IDX and conf >= _PERSON_CONF:
                    persons.append(entry)
                elif cls_id == _HELMET_IDX and conf >= _HELMET_CONF:
                    helmets.append(entry)

        # Assign 1-based IDs to persons in detection order.
        for i, p in enumerate(persons, start=1):
            p["id"] = i

        logger.info(
            "YOLO-World — %d person(s), %d helmet(s) in '%s'",
            len(persons), len(helmets), image_path.name,
        )
        return {"persons": persons, "helmets": helmets}

    # Backwards-compatibility shim — pipeline used to call detect_people().
    def detect_people(self, image_path: Path) -> list[dict[str, Any]]:
        return self.detect(image_path)["persons"]


yolo_service = YOLOService()
