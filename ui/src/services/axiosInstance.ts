import axios from 'axios';

// .envからAPIのURLを取得
const API_URL = process.env.APP_API_URL || 'http://localhost:8080';

// Axiosインスタンスの作成
const axiosInstance = axios.create({
  baseURL: API_URL,
});

// インターセプターの設定
axiosInstance.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 401エラー時の処理: ログアウトしてログイン画面にリダイレクト
      handleLogout();
      window.location.href = '/login'; // ログイン画面にリダイレクト
    }
    return Promise.reject(error);
  }
);

// ログアウト処理
const handleLogout = () => {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('backlog_authenticated');
};

export default axiosInstance;
