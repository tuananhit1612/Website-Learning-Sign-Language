import torch
import torch.nn as nn

NUM_HAND_JOINTS = 21
NUM_COORDS = 3
from core.FeatureIsolatedTransformer import FeatureIsolatedTransformer


class SiFormer(nn.Module):
    """
    SiFormer (Sign Isolated Transformer) model for sign language recognition.
    Uses left and right hand landmarks as input features.
    """
    def __init__(self, num_classes=100, num_hid=128, num_enc_layers=3, num_dec_layers=2,
                 patience=1, seq_len=50, device=None):
        super(SiFormer, self).__init__()
        print("Initializing SiFormer model")

        self.seq_len = seq_len
        self.device = device
        self.num_hid = num_hid

        self.l_hand_embedding = nn.Parameter(self.get_encoding_table(NUM_HAND_JOINTS * NUM_COORDS))
        self.r_hand_embedding = nn.Parameter(self.get_encoding_table(NUM_HAND_JOINTS * NUM_COORDS))

        self.class_query = nn.Parameter(torch.randn(1, 1, num_hid))


        self.transformer = FeatureIsolatedTransformer(
            feature_dims=[NUM_HAND_JOINTS * NUM_COORDS] * 2,
            num_layers=[num_enc_layers] * 2,                   
            num_decoder_layers=num_dec_layers,
            inner_classifiers_config=[num_hid, num_classes],
            projections_config=[seq_len, 1],
            device=device,
            patience=patience
        )

        print(f"Encoder layers: {num_enc_layers}, Decoder layers: {num_dec_layers}, Patience: {patience}")
        self.projection = nn.Linear(num_hid, num_classes)

    def forward(self, l_hand, r_hand, training=True):
        batch_size, seq_len, feature_dim = l_hand.shape

        l_hand_flat = l_hand.reshape(batch_size, seq_len, -1)
        r_hand_flat = r_hand.reshape(batch_size, seq_len, -1)

        l_input = l_hand_flat.permute(1, 0, 2).float() + self.l_hand_embedding
        r_input = r_hand_flat.permute(1, 0, 2).float() + self.r_hand_embedding 

        tgt = self.class_query.repeat(1, batch_size, 1)

        output = self.transformer([l_input, r_input], tgt, training=training)
        output = output.transpose(0, 1) 

        logits = self.projection(output.squeeze(1))
        return logits

    @staticmethod
    def get_encoding_table(d_model=63, seq_len=50):
        torch.manual_seed(42)
        table = torch.rand(seq_len, d_model)
        for i in range(seq_len):
            for j in range(1, d_model):
                table[i, j] = table[i, j - 1]
        return table.unsqueeze(1)
