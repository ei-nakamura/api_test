import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Main from './components/Main';
import Login from './components/Login';
import Register from './components/Register';
import SaveTokens from './components/SaveTokens';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';

/**
 * ルーティングの設定
 * - /login: ログイン画面
 * - /register: ユーザー登録画面
 * - /: 認証が必要なメイン画面
 * - ProtectedRoute: 認証が必要なルート
 * - AuthProvider: 認証状態を共有するためのContext Provider
 */
const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* ログイン画面 */}
          <Route path="/login" element={<Login />} /> 
          {/* ユーザー登録画面 */}
          <Route path="/register" element={<Register />} />
          <Route path="/save-tokens" element={<SaveTokens />} />
          {/* 認証が必要なルート */}
          <Route element={<ProtectedRoute />}>
            {/* メイン画面 */}
            <Route path="/" element={<Main />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
