import axios from 'axios';

// .envからAPIのURLを取得
const API_URL = process.env.APP_API_URL || 'http://localhost:8080';

// ユーザ登録
export interface RegisterResponse {
  id: number;
  username: string;
}

/**
 * ユーザ登録
 *
 * @param username ユーザ名
 * @param password パスワード
 * @returns レスポンスデータ
 */
export const register = async (username: string, password: string): Promise<RegisterResponse> => {
  // ユーザ登録リクエストを送信
  const response = await axios.post<RegisterResponse>(`${API_URL}/register`, {
    username,
    password,
  });
  return response.data;
};

// ユーザログイン
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * ユーザログイン
 *
 * @param username ユーザ名
 * @param password パスワード
 * @returns レスポンスデータ
 */
export const login = async (username: string, password: string): Promise<LoginResponse> => {
  try {
    // ログインリクエストを送信
    const response = await axios.post<LoginResponse>(`${API_URL}/token`, new URLSearchParams({
      'username': username,
      'password': password,
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // レスポンスのログを出力
    console.log('Login response:', response.data);

    return response.data;
  } catch (error) {
    // エラーログを出力
    console.error('Error during login request:', error);
    throw error; // 例外を再スローして呼び出し元でキャッチ
  }
};

/**
 * Backlogの認証エンドポイントにリダイレクト
 *
 * @function
 * @return {Promise<void>}
 */
export const redirectToBacklogOAuth = async () => {
  // Backlogの認証エンドポイントにリダイレクト
  // 認証後、このアプリ自体のトークンを使用してBacklogの認証トークンをDBに保存するため
  // tokenをクエリパラメータとして渡す
  const token = sessionStorage.getItem('access_token');
  window.location.href = `${API_URL}/auth/backlog?token=${token}`; 
};