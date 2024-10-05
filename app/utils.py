# utils.py
from passlib.context import CryptContext
import pytz
from datetime import datetime
import os

# パスワードハッシュ化用の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    パスワードを検証する関数。
    
    :param plain_password: 検証するパスワード
    :param hashed_password: ハッシュ化されたパスワード
    :return: 検証結果
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    パスワードをハッシュ化して返す関数。
    
    :param password: ハッシュ化するパスワード
    :return: ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)

def contains_keyword(data, keyword):
    """
    指定されたキーワードに部分一致するテキスト項目が存在するかを確認する関数。
    
    :param data: APIレスポンスのデータ（辞書またはリスト）
    :param keyword: 検索するキーワード（部分一致）
    :return: テキスト項目が存在すればTrue、存在しなければFalse
    """
    # キーワードが指定されていなければ、Trueを返す
    if keyword is None:
        return True
    
    # 辞書の場合、キーと値を再帰的にチェック
    if isinstance(data, dict):
        for key, value in data.items():
            if contains_keyword(value, keyword):
                return True

    # リストの場合、各要素を再帰的にチェック
    elif isinstance(data, list):
        for item in data:
            if contains_keyword(item, keyword):
                return True

    # テキスト項目の場合、キーワードに部分一致するかをチェック
    elif isinstance(data, str):
        if keyword in data:
            return True

    # 一致する項目が見つからなければFalse
    return False

def convert_to_tz(date_time_str):
    """
    UTC形式の日時を環境変数のタイムゾーンに変換する関数

    :param created: UTC形式の日時文字列（例: "2024-09-07T11:08:06Z"）
    :return: 環境変数のタイムゾーンまたは日本標準時（JST）に変換された日時文字列
    """
    # UTCのタイムゾーンを定義
    utc = pytz.utc

    # 環境変数のタイムゾーンを定義
    tz = pytz.timezone(os.environ.get('TZ', 'Asia/Tokyo'))

    # UTC形式の日時文字列をdatetimeオブジェクトに変換
    utc_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%SZ")

    # UTCのタイムゾーンを設定
    utc_time = utc.localize(utc_time)

    # 変換
    jst_time = utc_time.astimezone(tz)

    # 変換後の日時文字列を返す
    return jst_time.strftime("%Y-%m-%d %H:%M:%S")