import cv2
import numpy as np
import onnxruntime as ort
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "models" / "minifasnet_v2.onnx"


class MiniFASNet:

    def __init__(self):
        self.session = ort.InferenceSession(
            str(MODEL_PATH),
            providers=["CPUExecutionProvider"]
        )

        self.input = self.session.get_inputs()[0]
        self.output = self.session.get_outputs()[0]

        print("INPUT NAME :", self.input.name)
        print("INPUT SHAPE:", self.input.shape)
        print("INPUT TYPE :", self.input.type)

        print("OUTPUT NAME :", self.output.name)
        print("OUTPUT SHAPE:", self.output.shape)
        print("OUTPUT TYPE :", self.output.type)

        self.input_name = self.input.name
        self.output_name = self.output.name

    def preprocess(self, face):
        face = cv2.resize(face, (80, 80))
        face = face.astype(np.float32) / 255.0
        face = np.transpose(face, (2, 0, 1))
        face = np.expand_dims(face, 0)
        return face

    def softmax(self, x):
        e = np.exp(x - np.max(x))
        return e / np.sum(e)

    def predict(self, face):

        tensor = self.preprocess(face)

        output = self.session.run(
            [self.output_name],
            {self.input_name: tensor}
        )[0]

        probs = self.softmax(output[0])

        print_attack = float(probs[0])
        replay_attack = float(probs[1])
        live = float(probs[2])

        return {
            "is_live": live > 0.80,
            "live_score": live,
            "spoof_score": max(print_attack, replay_attack),
            "print_score": print_attack,
            "replay_score": replay_attack,
        }


antispoof = MiniFASNet()