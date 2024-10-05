import React, { useState } from 'react';
import { Activity } from '../services/activityService';

interface FavoriteActivity extends Activity {
    isSaved?: boolean;   // DB登録済みフラグ
    favoriteId?: number; // DBのお気に入りテーブルID
  }

interface ActivityListProps {
    activities: Activity[];
    favorites: FavoriteActivity[];
    onAddToFavoritesList: (task: Activity) => void;
    onRemoveFromFavoritesList: (taskId: number) => void;
}
  
  type SortConfig = {
    key: keyof Activity;
    direction: 'ascending' | 'descending';
  };

const ActivityList: React.FC<ActivityListProps> = ({ activities, favorites, onAddToFavoritesList, onRemoveFromFavoritesList }) => {
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null);

  // ソート後の更新情報リスト
  const sortedActivities = React.useMemo(() => {
    let sortableActivities = [...activities];
    if (sortConfig !== null) {
      sortableActivities.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableActivities;
  }, [activities, sortConfig]);

  /**
   * 更新情報の一覧をソートする
   * @param key ソートするキー
   * @returns なし
   */
  const requestSort = (key: keyof Activity) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (
      sortConfig &&
      sortConfig.key === key &&
      sortConfig.direction === 'ascending'
    ) {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  /**
   * ソートの方向を示すインジケータを取得
   * @param name ソートするキー
   * @returns ソートの方向を示すインジケータ（↑:昇順 or ↓:降順）or null
   */
  const getSortIndicator = (name: keyof Activity) => {
    if (!sortConfig || sortConfig.key !== name) {
      return null;
    }
    return sortConfig.direction === 'ascending' ? '↑' : '↓';
  };

  /**
   * 更新情報がお気に入り登録されているかをチェック
   * @param taskId 更新情報ID
   * @returns 更新情報がお気に入り登録されているか
   */
  const isFavorite = (taskId: number) => {
    return favorites.some(fav => fav.id === taskId);
  };

  /**
   * 更新情報がお気に入りリストにある　かつ、DBに保存されているかをチェック
   * @param taskId 更新情報ID
   * @returns 更新情報がお気に入りリストにある　かつ、DBに保存されているか
   */
  const isSaved = (taskId: number) => {
    const favorite = favorites.find(fav => fav.id === taskId);
    return favorite ? favorite.isSaved : false;
  };

  return (
    <div>
      <h5>検索結果</h5>
      <table className="table table-hover">
        <thead>
          <tr>
            <th scope="col"></th>
            <th scope="col" onClick={() => requestSort('id')} className="sortable" role="button">
              ID {getSortIndicator('id')}
            </th>
            <th scope="col" onClick={() => requestSort('project_name')} className="sortable" role="button">
              Project Name {getSortIndicator('project_name')}
            </th>
            <th scope="col" onClick={() => requestSort('type')} className="sortable" role="button">
              Type {getSortIndicator('type')}
            </th>
            <th scope="col" onClick={() => requestSort('type_name')} className="sortable" role="button">
              Type Name {getSortIndicator('type_name')}
            </th>
            <th scope="col" onClick={() => requestSort('content_summary')} className="sortable" role="button">
              Summary {getSortIndicator('content_summary')}
            </th>
            <th scope="col" onClick={() => requestSort('created_user_name')} className="sortable" role="button">
              Created User {getSortIndicator('created_user_name')}
            </th>
            <th scope="col" onClick={() => requestSort('created')} className="sortable" role="button">
              Created {getSortIndicator('created')}
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedActivities.map((task) => (
            <tr key={task.id}>
              <td>
                <input
                  type="checkbox"
                  role="button"
                  checked={isFavorite(task.id)}
                  onChange={() => {
                    if (isFavorite(task.id)) {
                      if (!isSaved(task.id)) {
                        onRemoveFromFavoritesList(task.id); // データベース未保存の場合、お気に入りリストから削除
                      }
                    } else {
                      onAddToFavoritesList(task); // お気に入りリストに追加
                    }
                  }}
                />
              </td>
              <td>{task.id}</td>
              <td>{task.project_name}</td>
              <td>{task.type}</td>
              <td>{task.type_name}</td>
              <td>{task.content_summary}</td>
              <td>{task.created_user_name}</td>
              <td>{task.created}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ActivityList;
