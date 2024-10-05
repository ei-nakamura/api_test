import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../services/axiosInstance';

const SaveTokens: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tempCode = params.get('temp_code');

    if (tempCode) {
      // サーバーに一時コードを送り、トークンを保存
      axiosInstance.post(
        `/auth/backlog/save_tokens`,
        null, 
        {
          params: { temp_code: tempCode }, // クエリパラメータとして送信
          headers: {
            Authorization: `Bearer ${sessionStorage.getItem('access_token')}`, // JWTトークンを送信して認証
        },
      })
      .then(() => {
        sessionStorage.setItem('backlog_authenticated', 'true');
        navigate('/'); // 保存が成功したらメイン画面へリダイレクト
      })
      .catch((error) => {
        console.error('トークン保存エラー:', error);
        // エラーハンドリング
      });
    }
  }, [navigate]);

  return <div>Saving tokens...</div>;
};

export default SaveTokens;
