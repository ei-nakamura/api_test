import React from 'react';
import { Activity } from '../services/activityService';

interface FavoriteActivity extends Activity {
  isSaved?: boolean;
  favoriteId?: number;  // お気に入りIDを保持
}

interface FavoritesListProps {
  favorites: FavoriteActivity[];
  onSaveFavorite: (task: FavoriteActivity) => void;
  onRemoveFavorite: (favoriteId: number) => void;
}

/**
 * お気に入りのリストを表示
 *
 * @param favorites お気に入りのリスト
 * @param onSaveFavorite 更新情報をお気に入りDBに保存
 * @param onRemoveFavorite 更新情報をお気に入りDBから削除
 * @return コンポーネント
 */
const FavoritesList: React.FC<FavoritesListProps> = ({ favorites, onSaveFavorite, onRemoveFavorite }) => {
  return (
    <div>
      <h5>お気に入りリスト</h5>
      <table className="table table-hover">
        <thead>
          <tr>
            <th scope="col"></th>
            <th scope="col">ID</th>
            <th scope="col">Project Name</th>
            <th scope="col">Type</th>
            <th scope="col">Type Name</th>
            <th scope="col">Summary</th>
            <th scope="col">Created User</th>
            <th scope="col">Created</th>
          </tr>
        </thead>
        <tbody>
          {favorites.length === 0 ? (
            <tr>
              <td colSpan={7} className="text-center">お気に入りはありません</td>
            </tr>
          ) : (
            favorites.map((fav) => (
              <tr key={fav.id}>
                <td>
                  <input
                    type="checkbox"
                    role="button"
                    checked={fav.isSaved || false}
                    onChange={() => {
                      if (fav.isSaved && fav.favoriteId) {
                        onRemoveFavorite(fav.favoriteId); // DBから削除
                      } else {
                        onSaveFavorite(fav); // DBに保存
                      }
                    }}
                  />
                </td>
                <td>{fav.id}</td>
                <td>{fav.project_name}</td>
                <td>{fav.type}</td>
                <td>{fav.type_name}</td>
                <td>{fav.content_summary}</td>
                <td>{fav.created_user_name}</td>
                <td>{fav.created}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default FavoritesList;
