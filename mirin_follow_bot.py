from atproto import Client
import time
import os
from dotenv import load_dotenv
# アカウント情報
load_dotenv()
HANDLE = os.environ['HANDLE']
APP_PASSWORD = os.environ['APP_PASSWORD']

# ログイン
client = Client()
client.login(HANDLE, APP_PASSWORD)

# 怪しいアカウントを判定する関数
def is_suspicious(user):
    sus_words = ['sex', 'xxx', 'adult', '18', 'エロ', 'love', '援交', 'fwb']
    handle = user['handle'].lower()
    display_name = (user.get('displayName') or '').lower()
    description = (user.get('description') or '').lower()

    if any(word in handle for word in sus_words):
        return True
    if any(word in display_name for word in sus_words):
        return True
    if not description.strip():
        return True
    return False

# フォロバ処理（怪しい垢はスルー）
def auto_follow_back():
    print("【フォロバチェック中…】")
    followers = client.app.bsky.graph.get_followers(actor=HANDLE).followers
    following = client.app.bsky.graph.get_follows(actor=HANDLE).follows

    followed_dids = set(f['did'] for f in following)
    for user in followers:
        if user['did'] not in followed_dids:
            if is_suspicious(user):
                print(f"スルー（怪しい）→ {user['handle']}")
                continue
            client.app.bsky.graph.follow.create(
                repo=HANDLE,
                record={"subject": user['did'], "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            )
            print(f"フォロバしたよ♡：{user['handle']}")

# 片思い状態の相手をフォロー解除
def auto_unfollow():
    print("【リムバチェック中…】")
    followers = client.app.bsky.graph.get_followers(actor=HANDLE).followers
    following = client.app.bsky.graph.get_follows(actor=HANDLE).follows

    follower_dids = set(f['did'] for f in followers)
    for user in following:
        if user['did'] not in follower_dids:
            # フォロー解除には rkey（uriの最後の部分）が必要
            rkey = user['uri'].split('/')[-1]
            client.app.bsky.graph.follow.delete(
                repo=HANDLE,
                rkey=rkey
            )
            print(f"リムバしたよ：{user['handle']}")

# 定期実行（30分に1回）
while True:
    try:
        auto_follow_back()
        auto_unfollow()
    except Exception as e:
        print(f"エラー：{e}")
    time.sleep(1800)  # 30分
