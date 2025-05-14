from atproto import Client
import time

# 認証情報
load_dotenv()
HANDLE = os.environ['HANDLE']
APP_PASSWORD = os.environ['APP_PASSWORD']

# ハッシュタグとキーワードのターゲット
TARGET_HASHTAGS = [
    '#地雷女', '#病みかわ', '#メンヘラ', '#地雷系', '#量産系',
    '#推しキャラプロフィールメーカー', '#オリキャラプロフィールメーカー',
    '#もふみつ工房', '#ふわふわ相性診断', '#ふわふわ相性診断メーカー'
]

TARGET_KEYWORDS = [
    '地雷', '量産', '病みかわ', 'メンヘラ', '相性診断', 'プロフィールメーカー',
    'ふわふわ', 'もふみつ', '推し紹介', 'ツインテール', '闇かわ', '黒リボン',
    '推しキャラ', 'オリキャラ', '創作垢', '絵描きさん', 'かわいい', '可愛い',
]

# クライアント初期化＆ログイン
client = Client()
client.login(HANDLE, APP_PASSWORD)
self_did = client.me.did  # 自分のDID（投稿除外用）

def auto_like_by_tags_and_keywords():
    """タイムラインからタグ・キーワードでいいね"""
    print("タグ＆キーワード巡回中...")
    try:
        feed = client.app.bsky.feed.get_timeline().feed
        for item in feed:
            post = item.post
            author_did = post.author.did
            text = post.record.text
            uri = post.uri
            cid = post.cid

            if author_did == self_did:
                continue  # 自分の投稿はスキップ

            if any(tag in text for tag in TARGET_HASHTAGS) or any(kw in text for kw in TARGET_KEYWORDS):
                client.app.bsky.feed.like.create(
                    repo=HANDLE,
                    record={
                        "subject": {"uri": uri, "cid": cid},
                        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }
                )
                print(f"いいね: {text[:50]}...")
    except Exception as e:
        print(f"タイムライン処理中エラー: {e}")

def auto_like_mentions():
    """メンションされた投稿にいいね"""
    print("メンションチェック中...")
    try:
        notifications = client.app.bsky.notification.list_notifications().notifications
        for note in notifications:
            if note.reason == "mention":
                uri = note.uri
                cid = note.cid
                client.app.bsky.feed.like.create(
                    repo=HANDLE,
                    record={
                        "subject": {"uri": uri, "cid": cid},
                        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }
                )
                print(f"メンションにいいね: {note.record.text[:50]}...")
    except Exception as e:
        print(f"メンション処理中エラー: {e}")

def auto_like_back():
    """自分にいいねしてくれた人の最新投稿にいいね返し"""
    print("いいね返し中...")
    try:
        notifications = client.app.bsky.notification.list_notifications().notifications
        for note in notifications:
            if note.reason == "like":
                user_did = note.author.did
                if user_did == self_did:
                    continue  # 自分からのいいねはスキップ

                feed = client.app.bsky.feed.get_author_feed(actor=user_did).feed
                if feed:
                    post = feed[0].post
                    uri = post.uri
                    cid = post.cid
                    client.app.bsky.feed.like.create(
                        repo=HANDLE,
                        record={
                            "subject": {"uri": uri, "cid": cid},
                            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                        }
                    )
                    print(f"いいね返し: {post.record.text[:50]}...")
    except Exception as e:
        print(f"いいね返しエラー: {e}")

# メインループ（30分ごと）
while True:
    auto_like_by_tags_and_keywords()
    auto_like_mentions()
    auto_like_back()
    print("30分おやすみちゅ〜♡")
    time.sleep(1800)