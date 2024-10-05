import React from 'react';

interface SearchBarProps {
  keyword: string;
  setKeyword: (keyword: string) => void;
  onSearch: () => void;
}

/**
 * 検索ボックスコンポーネント
 * @param {string} keyword - 検索キーワード
 * @param {(keyword: string) => void} setKeyword - 検索キーワードを更新する関数
 * @param {() => void} onSearch - 検索を実行する関数
 * @returns {React.ReactElement} - 検索ボックスコンポーネント
 */
const SearchBar: React.FC<SearchBarProps> = ({ keyword, setKeyword, onSearch }) => {
  return (
    <div className="input-group">
      <input
        type="text"
        className="form-control"
        placeholder="Search keyword"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && onSearch()}
      />
      <div className="input-group-append">
        <button className="btn btn-primary" onClick={onSearch}>Search</button>
      </div>
    </div>
  );
};

export default SearchBar;
