import axiosInstance from './axiosInstance';

// 更新情報検索
export interface Activity {
  id: number;
  project_name: string;
  type: string;
  type_name: string;
  content_summary: string;
  created_user_name: string;
  created: string;
}

/**
 * 更新情報検索
 * @param keyword 検索キーワード
 * @param token アクセストークン
 * @returns 検索結果のリスト
 */
export const searchActivities = async (keyword: string, token: string): Promise<Activity[]> => {
  const response = await axiosInstance.get<Activity[]>(
    '/activities/search', {
    params: { keyword },
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

// お気に入り取得
export interface Favorite extends Activity {
  favorite_id: number;
}

/**
 * お気に入りの一覧を取得
 *
 * @param token アクセストークン
 * @returns お気に入りのリスト
 */
export const getFavorites = async (token: string): Promise<Favorite[]> => {
  const response = await axiosInstance.get<Favorite[]>(
    `/favorites-search`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}

// お気に入り登録
export interface FavoriteCreate {
  activity_id: string;
  activity_title: string;
}

/**
 * お気に入り登録
 * @param favorite 更新情報
 * @param token アクセストークン
 */
export const addFavorite = async (favorite: FavoriteCreate, token: string): Promise<Favorite> => {
  const response = await axiosInstance.post(
    `/favorites`, favorite, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

/**
 * お気に入り削除
 * @param favoriteId お気に入りID
 * @param token アクセストークン
 */
export const deleteFavorite = async (favoriteId: number, token: string): Promise<void> => {
  await axiosInstance.delete(
    `/favorites/${favoriteId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};