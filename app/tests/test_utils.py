# test_utils.py
import pytest, sys, os

# /appディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import verify_password, get_password_hash, contains_keyword, convert_to_tz

def test_verify_password():
    """
    正常系: パスワード検証のテスト

    GIVEN: パスワードとそのハッシュ値
    WHEN: verify_passwordを実行
    THEN: Trueが返る
    """
    password = "securepassword"
    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password) == True

def test_verify_password_invalid():
    """
    異常系: 不正なパスワードの検証

    GIVEN: パスワードと別のパスワードのハッシュ値
    WHEN: verify_passwordを実行
    THEN: Falseが返る
    """
    password = "securepassword"
    wrong_password = "wrongpassword"
    hashed_password = get_password_hash(password)

    assert verify_password(wrong_password, hashed_password) == False

def test_get_password_hash():
    """
    正常系: パスワードハッシュ化のテスト

    GIVEN: 平文パスワード
    WHEN: get_password_hashを実行
    THEN: ハッシュ化されたパスワードが返る
    """
    password = "securepassword"
    hashed_password = get_password_hash(password)

    # ハッシュが生成されていることを確認
    assert hashed_password != password
    assert verify_password(password, hashed_password)

def test_contains_keyword_in_dict():
    """
    正常系: 辞書内のキーワード検索のテスト

    GIVEN: 辞書とキーワード
    WHEN: contains_keywordを実行
    THEN: キーワードが存在する場合はTrue、存在しない場合はFalseが返る
    """
    data = {"key1": "value1", "key2": "value2"}
    keyword = "value1"

    assert contains_keyword(data, keyword) == True

def test_contains_keyword_in_list():
    """
    正常系: リスト内のキーワード検索のテスト

    GIVEN: リストとキーワード
    WHEN: contains_keywordを実行
    THEN: キーワードが存在する場合はTrue、存在しない場合はFalseが返る
    """
    data = ["value1", "value2", "value3"]
    keyword = "value2"

    assert contains_keyword(data, keyword) == True

def test_contains_keyword_in_nested_structure():
    """
    正常系: ネストされた構造内のキーワード検索のテスト

    GIVEN: ネストされた構造とキーワード
    WHEN: contains_keywordを実行
    THEN: キーワードが存在する場合はTrue、存在しない場合はFalseが返る
    """
    data = {"key1": ["value1", {"key2": "value2"}]}
    keyword = "value2"

    assert contains_keyword(data, keyword) == True

def test_contains_keyword_not_found():
    """
    異常系: 存在しないキーワードの検索

    GIVEN: 存在しないキーワード
    WHEN: contains_keywordを実行
    THEN: Falseが返る
    """
    
    data = {"key1": "value1", "key2": "value2"}
    keyword = "notfound"

    assert contains_keyword(data, keyword) == False

def test_contains_keyword_integer_value():
    """
    異常系: 文字列以外の値のみしか存在しないキーワードの検索

    GIVEN: 文字列以外の値のみしか存在しないキーワード
    WHEN: contains_keywordを実行
    THEN: Falseが返る
    """
    data = {"key1": "value1", "key2": "value2", "key3": 3}
    keyword = "3"

    assert contains_keyword(data, keyword) == False

def test_contains_keyword_empty_keyword():
    """
    正常系: キーワードがNoneの場合

    GIVEN: キーワードがNone
    WHEN: contains_keywordを実行
    THEN: Trueが返る
    """
    data = {"key1": "value1", "key2": "value2"}
    keyword = None

    assert contains_keyword(data, keyword) == True

def test_convert_to_tz_jst():
    """
    正常系: UTC日時をJSTに変換するテスト

    GIVEN: UTC形式の日時文字列
    WHEN: convert_to_tzを実行
    THEN: JSTに変換された日時文字列が返る
    """
    date_time_str = "2024-09-07T11:08:06Z"
    
    # 環境変数を設定してテスト（日本標準時）
    os.environ['TZ'] = 'Asia/Tokyo'
    expected_time = "2024-09-07 20:08:06"
    
    assert convert_to_tz(date_time_str) == expected_time

def test_convert_to_tz_other_timezone():
    """
    正常系: UTC日時を別のタイムゾーンに変換するテスト

    GIVEN: UTC形式の日時文字列
    WHEN: convert_to_tzを実行
    THEN: 別のタイムゾーンに変換された日時文字列が返る
    """
    date_time_str = "2024-09-07T11:08:06Z"
    
    # 環境変数を設定してテスト（例: ロンドン時間）
    os.environ['TZ'] = 'Europe/London'
    expected_time = "2024-09-07 12:08:06"
    
    assert convert_to_tz(date_time_str) == expected_time

def test_convert_to_tz_invalid_format():
    """
    異常系: convert_to_tzに無効な日時フォーマットを渡すテスト

    GIVEN: 無効な日時フォーマット
    WHEN: convert_to_tzを実行
    THEN: ValueErrorが発生
    """
    date_time_str = "invalid-date-time-format"
    
    with pytest.raises(ValueError):
        convert_to_tz(date_time_str)

def test_convert_to_tz_no_timezone_env():
    """
    正常系: 環境変数が設定されていない場合のデフォルト動作

    GIVEN: 環境変数が設定されていない
    WHEN: convert_to_tzを実行
    THEN: JSTにデフォルトで変換された日時文字列が返る
    """
    date_time_str = "2024-09-07T11:08:06Z"
    
    # 環境変数をクリアしてテスト（デフォルトはJST）
    if 'TZ' in os.environ:
        del os.environ['TZ']
    
    expected_time = "2024-09-07 20:08:06"  # JSTの変換結果
    assert convert_to_tz(date_time_str) == expected_time
