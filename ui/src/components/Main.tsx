import React, { useState, useEffect } from 'react';
import { searchActivities, addFavorite, deleteFavorite, Activity, FavoriteCreate, getFavorites } from '../services/activityService';
import SearchBar from './SearchBar';
import ActivityList from './ActivityList';
import FavoritesList from './FavoritesList';
import CustomModal from './Modal';
import { useAuth } from '../context/AuthContext';
import { redirectToBacklogOAuth } from '../services/authService';

interface FavoriteActivity extends Activity {
    isSaved?: boolean;
    favoriteId?: number;  // データベースに保存されたお気に入りのID
  }
  
/**
 * メイン画面
 *
 * 検索フォーム、更新情報一覧、お気に入り一覧を表示
 *
 * @returns メイン画面のJSX
 */
const Main: React.FC = () => {
    const [activities, setActivities] = useState<Activity[]>([]);
    const [favorites, setFavorites] = useState<FavoriteActivity[]>([]);
    const [keyword, setKeyword] = useState('');
    const [token] = useState(sessionStorage.getItem('access_token') || '');
    const [showModal, setShowModal] = useState(false); // モーダル表示状態
    const { logout } = useAuth();

  useEffect(() => {
    // Backlogのアクセストークンの有無をチェック
    const backlogAuthenticated = sessionStorage.getItem('backlog_authenticated');
    if (backlogAuthenticated !== 'true') {
      redirectToBacklogOAuth(); // 認証がまだの場合はBacklogの認証画面にリダイレクト
    }

    // 初期ロードでお気に入りと更新情報の検索を実行
    const fetchFavorites = async () => {
      // お気に入りの取得
      try {
        const response = await getFavorites(token);
        // DBから取得したお気に入りに isSaved: true を設定
        setFavorites(response.map(fav => ({ ...fav, isSaved: true, favoriteId: fav.favorite_id })));
      } catch (error) {
        console.error('お気に入りの取得に失敗しました:', error);
      }
    };

    const fetchActivities = async () => {
      // 更新情報の取得
      try {
        const result = await searchActivities('', token); // キーワードなしで検索
        setActivities(result);
        if (result.length === 0) {
          setShowModal(true); // 結果が0件の場合にモーダルを表示
        }
      } catch (error) {
        console.error('更新情報の取得に失敗しました:', error);
      }
    };

    fetchFavorites();
    fetchActivities();
  }, [token]);

  /**
   * 更新情報を検索
   *
   * @function
   * @async
   * @return {Promise<void>}
   */
  const handleSearch = async () => {
    try {
      const result = await searchActivities(keyword, token);
      setActivities(result);
      if (result.length === 0) {
        setShowModal(true); // 結果が0件の場合にモーダルを表示
      }
    } catch (error) {
      console.error('更新情報の取得に失敗しました:', error);
    }
  };

  /**
   * 更新情報をお気に入りリストに追加
   * @function
   * @param {Activity} task 更新情報
   * @return {void}
   */
  const handleAddToFavoritesList = (task: Activity) => {
    if (!favorites.some(fav => fav.id === task.id)) {
      // 未登録の更新情報の場合、isSaved: false で追加
      setFavorites([...favorites, { ...task, isSaved: false }]); 
    }
  };

  /**
   * お気に入りリストから更新情報を削除
   * @function
   * @param {number} taskId 更新情報ID
   * @return {Promise<void>}
   */
  const handleRemoveFromFavoritesList = (taskId: number) => {
    setFavorites(favorites.filter(fav => fav.id !== taskId)); // お気に入りリストから削除
  };

  /**
   * お気に入りをDBに登録
   *
   * @function
   * @async
   * @param {FavoriteActivity} task お気に入り登録する更新情報
   * @return {Promise<void>}
   */
  const handleSaveFavorite = async (task: FavoriteActivity) => {
    try {
      const favorite: FavoriteCreate = {
        activity_id: task.id.toString(),
        activity_title: task.content_summary,
      };
      const response = await addFavorite(favorite, token); // DBに保存
      // 新たに保存したお気に入りのIDを favoriteId に設定
      setFavorites(favorites.map(fav => fav.id === task.id ? { ...fav, isSaved: true, favoriteId: response.favorite_id } : fav));
    } catch (error) {
      console.error('お気に入りの保存に失敗しました:', error);
    }
  };

  /**
   * お気に入りをDBから削除
   *
   * @function
   * @async
   * @param {number} favoriteId お気に入りID
   * @return {Promise<void>}
   */
  const handleRemoveFavorite = async (favoriteId: number) => {
    try {
      await deleteFavorite(favoriteId, token); // DBから削除
      setFavorites(favorites.filter(fav => fav.favoriteId !== favoriteId));
    } catch (error) {
      console.error('お気に入りの削除に失敗しました:', error);
    }
  };

  /**
   * ログアウト(認証を解除)
   *
   * @function
   * @return {Promise<void>}
   */
  const handleLogout = () => {
    logout(); // 認証コンテキストのログアウト処理
  };

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center">
        <h2>更新情報検索</h2>
        <button className="btn btn-outline-secondary" onClick={handleLogout}>
          ログアウト
        </button>
      </div>
      <div className="mt-3">
      {/* 検索バー */}
        <SearchBar keyword={keyword} setKeyword={setKeyword} onSearch={handleSearch} />
      </div>
      {/* お気に入りリスト */}
      <div className="mt-4">
        <FavoritesList favorites={favorites} onSaveFavorite={handleSaveFavorite} onRemoveFavorite={handleRemoveFavorite} />
      </div>
      {/* 検索結果 */}
      <div className="mt-4">
        <ActivityList activities={activities} favorites={favorites} onAddToFavoritesList={handleAddToFavoritesList} onRemoveFromFavoritesList={handleRemoveFromFavoritesList} />
      </div>
      <CustomModal
        show={showModal}
        handleClose={() => setShowModal(false)}
        title="検索結果"
        message="該当する更新情報が存在しません。"
      />
    </div>
  );
};

export default Main;
