echo コンテナビルド開始
cd ../
docker compose down -v
docker compose build
docker compose up -v
echo データベースmigration
@REM docker compose exec api alembic revision --autogenerate -m "Create m_user and m_favorites tables"
@REM docker compose exec api alembic upgrade head