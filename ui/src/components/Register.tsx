import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { register } from '../services/authService';

/**
 * ユーザー登録コンポーネント
 * @returns {React.ReactElement} - ユーザー登録フォーム
 */
const Register: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  /**
   * ユーザー登録フォームを送信
   * @param e React.FormEvent
   * @returns {Promise<void>}
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await register(username, password);
      setSuccess(`User ${data.username} 登録完了しました。ログイン画面に遷移します...`);
      setError('');
      // 登録後にログイン画面にリダイレクト
      setTimeout(() => navigate('/login'), 2000);
    } catch (error) {
      setError('登録エラー: 入力内容を確認してください。');
      setSuccess('');
      console.error('登録エラー:', error);
    }
  };

  return (
    <div className="container mt-5">
      <h2>ユーザ登録</h2>
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
        {success && <div className="alert alert-success mt-3">{success}</div>}
        <button type="submit" className="btn btn-primary mt-3">登録</button>
      </form>
    </div>
  );
};

export default Register;
