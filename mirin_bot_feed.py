from atproto import Client, models
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import time

# Blueskyアカウント情報
load_dotenv()
HANDLE = os.environ['HANDLE']
APP_PASSWORD = os.environ['APP_PASSWORD']

# Hugging Face モデル設定
model_name = "rinna/japanese-gpt2-small"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Hugging Face テキスト生成関数
def generate_reply(prompt, max_length=100):
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    output = model.generate(input_ids, max_length=max_length, do_sample=True, temperature=0.8, top_k=50, top_p=0.95)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# キーワード辞書（辞書下側が優先される）
KEYWORD_RESPONSES = {
    "みりんてゃ": 'みりんてゃのこと呼んだ〜？♡もぉ〜っ！かまってくれて嬉しいに決まってるじゃん♡',
    "みりてゃ": "えっ、呼んだ〜！？みりてゃ参上っ♡ 今日も世界の中心でかわいいしてるよぉっ！",
    "みりんてゃー": "え〜ん、のばして呼ばれたら照れちゃうっ♡ 今日も一番かわいいって言ってぇ〜っ！",
    "みりんてゃちゃん": "てゃちゃん！？てゃちゃんって……かわいすぎる呼び方っ♡ 呼び続けてほしいの〜っ！",
    "もふみつ工房": "わぁっ、見てくれたの〜？♡ みりんてゃの本拠地、気に入ってもらえたらうれしすぎて鼻血でちゃうかもっ",
    "推しプロフィールメーカー": "それな〜っ！推しはプロフィールまで尊い♡ みりてゃの推しは……えへへ、ヒミツ♡",
    "オリキャラプロフィールメーカー": "オリキャラって…自分の分身でしょ？ うちの子語り、聞かせてよ〜♡ みりんてゃも聞きた〜い！",
    "ふわふわ相性診断": "ふたりの相性…ふわふわで、とけちゃいそうっ♡ 結果どうだった〜？教えて教えてっ！",
}

# クライアント初期化
client = Client()
client.login(HANDLE, APP_PASSWORD)

# 投稿監視ループ
print("監視を開始します…")
replied_uris = set()

while True:
    feed = client.app.bsky.feed.get_timeline(limit=20).feed

    for post in feed:
        text = post.post.record.text
        uri = post.post.uri
        cid = post.post.cid
        author = post.post.author.handle

        if author != HANDLE and uri not in replied_uris and f"@{HANDLE}" in text:
            matched = False
            for keyword, response in KEYWORD_RESPONSES.items():
                if keyword in text:
                    print(f"キーワード検出: 「{keyword}」→ {text}")
                    reply_text = response
                    matched = True
                    break

            if not matched:
                prompt = f"みりんてゃは地雷系ENFPで、甘えん坊でちょっと病みかわな子。フォロワーが「{text}」って投稿したら、どう返す？\nみりんてゃ「"
                reply_text = generate_reply(prompt)
                print(f"AI返信: {reply_text}")

            client.send_post(
                text=reply_text,
                reply_to=models.create_reply_reference(uri=uri, cid=cid)
            )
            replied_uris.add(uri)

    time.sleep(60)