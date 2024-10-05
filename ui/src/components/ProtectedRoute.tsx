import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * 認証されたユーザーのみにアクセス可能なルート
 *
 * 認証されていない場合はログイン画面にリダイレクト
 *
 * @returns 認証された場合はOutletを返し、認証されていない場合はNavigateを返す
 */
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated } = useAuth();

  // 認証されていない場合はログイン画面にリダイレクト
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;

