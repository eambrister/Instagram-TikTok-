"""Robust Video Matting (PeterL1n/RobustVideoMatting, GPL-3.0; ONNX model from its GitHub releases) for
clean, temporally stable subject mattes, replacing the 256x256 selfie segmenter for depth titles.

    m = Matte("rvm_mobilenetv3_fp32.onnx")      # or rvm_resnet50_fp32.onnx (sharper, ~3x slower)
    alpha = m(frame)        # frame: H x W x 3 float32/uint8 RGB 0-255 -> H x W float32 0-1
    m.reset()               # call at a hard cut so the recurrent state doesn't smear across shots
"""
import numpy as np
import onnxruntime as ort


class Matte:
    def __init__(self, model, downsample=0.25, threads=4):
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        self.s = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
        self.ds = np.array([downsample], np.float32)
        self.reset()

    def reset(self):
        self.rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4

    def __call__(self, frame):
        x = np.ascontiguousarray(np.asarray(frame, np.float32).transpose(2, 0, 1)[None] / 255.0)
        fgr, pha, *self.rec = self.s.run(None, {"src": x, "r1i": self.rec[0], "r2i": self.rec[1],
                                                "r3i": self.rec[2], "r4i": self.rec[3], "downsample_ratio": self.ds})
        return pha[0, 0]
