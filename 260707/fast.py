import torch.nn as nn
import torch
import pickle
with open("./model_file.pkl", "rb") as f:
    vocab = pickle.load(f)
class SentimentBiLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=128, num_layers=1, dropout=0.3):
        super().__init__()
        self.embedding = self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embed_dim,
            padding_idx=0
        )
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True, #[배치, 길이, 특징]
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, 1) # 양방향 LSTM이므로 은닉 상태를 2배 차원으로 받아 1개의 로짓을 출력


    def forward(self, input_ids):
        embedded = self.embedding(input_ids)
        outputs, (hidden, cell) = self.lstm(embedded)
       
        forward_hidden = hidden[-2] # 마지막 층의 정방향 은닉 상태
        backward_hidden = hidden[-1] # 마지막 층의 역방향 은닉 상태
        final_hidden = torch.cat((forward_hidden, backward_hidden), dim=1)
        final_hidden = self.dropout(final_hidden)
        logits = self.fc(final_hidden).squeeze(1)


        return logits
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SentimentBiLSTM(
    vocab_size=len(vocab),
    embed_dim=128,
    hidden_dim=128,
    num_layers=1,
    dropout=0.3
).to(device)
model.load_state_dict(torch.load("./best_sentiment_bilstm.pt", map_location=device))

total_params = sum(p.numel() for p in model.parameters())


import re
def simple_tokenize(text : str) -> list:
    text = text.lower()
    text = re.sub(r"[^가-힣ㄱ-ㅎㅏ-ㅣa-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text) #raw
    tokens = text.split()
    return tokens


def encode_text(text, vocab, max_len=50):
    tokens = simple_tokenize(text)
    token_ids = [vocab.get(token, vocab["<UNK>"]) for token in tokens]
    if len(token_ids) > max_len:
        token_ids = token_ids[:max_len]
    else:
        token_ids += [vocab["<PAD>"]] * (max_len - len(token_ids))
    return token_ids


def predict_sentiment(text, model, vocab, device, max_len=50):
    model.eval()
    input_ids = encode_text(text, vocab, max_len=max_len)
    input_tensor = torch.tensor([input_ids], dtype=torch.long).to(device)


    with torch.no_grad():
        logits = model(input_tensor)
        prob = torch.sigmoid(logits).item()
    label = 1 if prob >= 0.5 else 0
    return label, prob



from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictRequest(BaseModel):
    text: str

@app.get('/')
def root():
    return {'message': '처음 api 실행'}

@app.post('/predict')
def predict(request: PredictRequest):
    text = request.text
    res = predict_sentiment(text, model=model, vocab=vocab, device=device, max_len=50)

    return {'result': f'result: {res}'}