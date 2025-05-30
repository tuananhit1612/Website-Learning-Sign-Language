from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify

siformer_vnsl_bp = Blueprint('siformer_vnsl', __name__)

import torch
import numpy as np
from core.SiFormer import SiFormer
import pickle

MODEL_PATH = "./static/model/best_model.pth"
stats = torch.load("./static/model/normalization_stats.pth")
LABELMAP_PATH = "./static/model/label_map.pkl"

NUM_CLASSES = 99
SEQ_LEN = 50
THRESHOLD = 0.5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

mean = stats["mean"]
std = stats["std"]
mean_l = mean[:63]
mean_r = mean[63:]
std_l = std[:63]
std_r = std[63:]

model = SiFormer(
    num_classes=NUM_CLASSES,
    num_hid=126,
    seq_len=SEQ_LEN,
    num_enc_layers=4,
    num_dec_layers=3,
    device=DEVICE
)

with open(LABELMAP_PATH, "rb") as f:
    label_map = pickle.load(f)
index_to_gloss = {v: k for k, v in label_map.items()}

model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()

sentence = []
predictions = []

@siformer_vnsl_bp.route("/api/predict", methods=["POST"])
def predict():
    global sentence,predictions
    try:
        data = request.get_json()
        left_hand_seq = data.get("left_hand_sequence", [])
        right_hand_seq = data.get("right_hand_sequence", [])

        if not left_hand_seq or len(left_hand_seq) != 50:
            return jsonify({"error": "Sai dữ liệu"}), 400

        with torch.no_grad():
            l_tensor = torch.tensor(left_hand_seq, dtype=torch.float32).unsqueeze(0).to(DEVICE)
            r_tensor = torch.tensor(right_hand_seq, dtype=torch.float32).unsqueeze(0).to(DEVICE)

            l_tensor = l_tensor.view(1, SEQ_LEN, -1)
            r_tensor = r_tensor.view(1, SEQ_LEN, -1)

            mean_l_t = mean_l.view(1, 1, -1).to(DEVICE)
            std_l_t = std_l.view(1, 1, -1).to(DEVICE)
            mean_r_t = mean_r.view(1, 1, -1).to(DEVICE)
            std_r_t = std_r.view(1, 1, -1).to(DEVICE)

            l_tensor = (l_tensor - mean_l_t) / (std_l_t + 1e-6)
            r_tensor = (r_tensor - mean_r_t) / (std_r_t + 1e-6)


            logits = model(l_tensor, r_tensor)
            probs = torch.softmax(logits, dim=-1)
            max_prob, pred = torch.max(probs, dim=-1)

            pred_id = pred.item()
            confidence = max_prob.item()

            gloss = index_to_gloss[pred_id]

            # predictions.append(pred_id)
            # predictions = predictions[-10:]

            # result_gloss = None
            # if len(predictions) == 10 and np.unique(predictions).shape[0] == 1:
            #     if confidence > THRESHOLD:
            #         if len(sentence) == 0 or pred_id != sentence[-1]:
            #             sentence.append(pred_id)
            #             gloss = index_to_gloss[pred_id]
            #             print(f"APPEND: {gloss} (confidence: {confidence:.2f})")
            #             result_gloss = gloss
            #             print(f"Sentence: {sentence}")

            return jsonify({"prediction": gloss, "confidence": confidence}), 200

    except Exception as e:
        print("Lỗi dự đoán:", e)
        return jsonify({"prediction": "Lỗi server", "confidence": 0}), 500