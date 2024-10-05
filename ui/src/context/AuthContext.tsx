import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextProps {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

/**
 * AuthProviderは、認証状態を管理するためのContext Providerです。
 *
 * children propsには、認証状態に応じて表示するコンポーネントを指定します。
 *
 * 認証状態は、isAuthenticatedという値で管理されます。
 * true:認証済み、false:未認証状態
 *
 * loginという関数で、認証トークンをsessionStorageに保存し、isAuthenticatedをtrueに設定します。
 *
 * logoutという関数で、sessionStorageから認証トークンを削除し、isAuthenticatedをfalseに設定します。
 *
 * 認証チェック中には、`Loading...`というコンポーネントを表示します。
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);  // ロード中の状態を追加

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);  // 認証チェックが完了したらロード終了
  }, []);

  /**
   * 認証トークンをsessionStorageに保存し、isAuthenticatedをtrueに設定
   *
   * @param token 認証トークン
   */
  const login = (token: string) => {
    sessionStorage.setItem('access_token', token);
    setIsAuthenticated(true);
  };

  /**
   * 認証トークンをsessionStorageから削除し、isAuthenticatedをfalseに設定
   *
   * @function
   * @return {void}
   */
  const logout = () => {
    // セッションストレージから認証トークンを削除
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('backlog_authenticated');
    // 認証状態をfalseに設定
    setIsAuthenticated(false);
  };

  if (loading) {
    return <div>Loading...</div>; 
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * 認証状態を取得するためのhooks
 * AuthProvider コンポーネント内で使用する
 * @returns 認証状態を表す AuthContextProps
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
