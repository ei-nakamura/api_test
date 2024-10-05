import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as apiLogin, redirectToBacklogOAuth } from '../services/authService';
import { useAuth } from '../context/AuthContext';

/**
 * ログインコンポーネント
 * - ユーザ名とパスワードを入力するフォーム
 * - ログインボタンをクリックすると、apiLoginを呼び出し、認証に成功したらisAuthenticatedをtrueに設定
 * - ログイン状態になったら自動的にメイン画面にリダイレクト
 * - エラーが起きたら、エラーメッセージを表示
 * - 登録画面へ遷移するボタンもあり
 */
const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  /**
   * ログインフォームを送信
   * @param e React.FormEvent
   * @returns {Promise<void>}
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await apiLogin(username, password);
      if (data && data.access_token) {  // レスポンスのトークンが存在するかチェック
        login(data.access_token);      // 認証成功時にコンテキストのログイン関数を呼び出し
        redirectToBacklogOAuth();       // backlog OAuthへ遷移
      } else {
        setError('Failed to receive token');
      }
    } catch (error) {
      setError('Login failed: Please check your username and password.');
      console.error('Error during login:', error);
    }
  };

  /**
   * 登録画面へ遷移
   *
   * @function
   */
  const handleRegist = () => {
    navigate('/register');
  }

  return (
    <div className="container mt-5">
      <h2>ログイン</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            className="form-control"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            className="form-control"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <div className="alert alert-danger mt-3">{error}</div>}
        <button type="submit" className="btn btn-primary mt-3">ログイン</button>
        <button className="btn btn-danger mt-3" onClick={handleRegist}>ユーザ登録</button>
      </form>
    </div>
  );
};

export default Login;
