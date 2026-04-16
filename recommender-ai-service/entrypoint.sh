#!/bin/bash
set -e

echo "[AI Service] Running Django migrations..."
python manage.py migrate --noinput 2>&1 || echo "Migration warning (non-fatal)"

echo "[AI Service] Training LSTM behavior model (if not exists)..."
if [ ! -f "artifacts/lstm_behavior_model.pt" ]; then
    python scripts/train_model.py && echo "LSTM model trained." || echo "Model training skipped."
fi

echo "[AI Service] Loading KB + FAISS index..."
python manage.py shell -c "
from app.services.kb_ingestion import kb_service
from app.services.rag_retrieval import rag_service
c = kb_service.load_from_disk()
ok = rag_service.load_index()
if not ok and c > 0:
    rag_service.build_index()
print(f'KB entries: {c}, faiss_loaded: {ok}')
" || echo "KB/FAISS load warning (non-fatal)"

echo "[AI Service] Starting FastAPI + uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info
