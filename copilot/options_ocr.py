"""Read the five answer options (A to E) from the problem image, on the board.

The final test gives the image but not the options, so the board reads them itself,
inside the problem's clock. The reader is the label-anchored one of laptop/option_boxes.py
(arm B1) and laptop/option_rec.py (PP-OCRv6_rec_small with the 2-D split), see
docs/OPTION_READER_GUIDE.md. It is imported from laptop/, not copied.

Files in OCR_DIR (config.env): PP-OCRv6_rec_small.onnx and label_templates.npz. The
templates must match the typeface of the images: the organizers' problems need templates
built from their demo images, not the M3Kang ones. Packages: numpy, opencv-python-headless
and onnxruntime, unpacked from wheels into NMT_SITE like the translation's packages.
Without them, read_options() returns {} and the problem keeps the options it came with.
"""
import os
import re
import sys

from .config import CONFIG, ROOT

OCR_DIR = os.path.expanduser(CONFIG.get("OCR_DIR", "~/models/ocr"))
SITE = os.path.expanduser(CONFIG.get("NMT_SITE", "~/nmt-site"))
THREADS = int(CONFIG.get("OCR_THREADS", "4"))
ARM = ("R1", "I0", "2d")
# Fast label search: the organizers' labels are 33 px high (scale 0.875 of the 40 px template)
# and sit in the last lines. Search the bottom OCR_BAND px at these scales first; if that finds
# no A..E sequence, run the full search of option_boxes.find_labels (21 scales, whole image).
SCALES = [float(x) for x in CONFIG.get("OCR_SCALES", "0.85 0.875 0.9").split()]
BAND = int(CONFIG.get("OCR_BAND", "320"))
# an apostrophe sits raised like an exponent: "L'Oriol" comes out as "L^1 Oriol"
APOSTROPHE = re.compile(r"(?<=[A-Za-zÀ-ÿ])\^1 ?(?=[A-Za-zÀ-ÿ])")
_state = {}


def _load():
    """(option_boxes, option_rec, recognizers), or None if a package or a file is missing."""
    if "mods" not in _state:
        _state["mods"] = None
        try:
            for path in (SITE, os.path.join(ROOT, "laptop")):
                if os.path.isdir(path) and path not in sys.path:
                    sys.path.insert(0, path)
            import option_boxes as ob
            import option_rec as orc
            ob.TEMPLATES = os.path.join(OCR_DIR, "label_templates.npz")
            orc.MODEL_DIR = OCR_DIR
            ob.templates()
            import cv2
            cv2.setNumThreads(THREADS)  # option_boxes sets 1; the model servers idle meanwhile
            full = ob.find_labels

            def fast(g, tpl=None):
                top, saved = max(0, g.shape[0] - BAND), ob.SCALES
                try:
                    ob.SCALES = SCALES
                    found = full(g[top:], tpl)
                finally:
                    ob.SCALES = saved
                if found:
                    return [(x0, y0 + top, x1, y1 + top, sc) for x0, y0, x1, y1, sc in found]
                return full(g, tpl)

            ob.find_labels = fast  # assign() looks it up in its module
            _state["mods"] = (ob, orc, {ARM[0]: orc.Rec(ARM[0], THREADS)})
        except Exception as error:  # noqa: BLE001 - no OCR means the given options stay
            _state["error"] = f"{type(error).__name__}: {error}"
    return _state["mods"]


def available():
    """Load the reader (a few hundred ms): call it before the first problem's clock."""
    return _load() is not None


def read_options(image):
    """{letter: text} for A to E from PNG/JPEG bytes or a file path; {} if not five."""
    mods = _load()
    if mods is None:
        return {}
    _ob, orc, recs = mods
    import cv2
    import numpy as np
    if isinstance(image, (bytes, bytearray)):
        g = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_GRAYSCALE)
    else:
        g = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    if g is None:
        return {}
    options = orc.read_row(recs, g, [ARM])[ARM]["options"]
    if len(options) != 5 or not all(v.strip() for v in options.values()):
        return {}
    return {k: APOSTROPHE.sub("'", v) for k, v in options.items()}
