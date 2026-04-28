#!/bin/bash
set -e

echo "[AI Service] Running Django migrations..."
python manage.py migrate --noinput 2>&1 || echo "Migration warning (non-fatal)"

echo "[AI Service] Ensuring AI-service-2 model artifacts (if not exists)..."
if [ ! -f "data/data_user500.csv" ]; then
    python scripts/generate_data_user500.py && echo "Generated data_user500.csv" || echo "Dataset generation skipped."
fi

if [ ! -f "artifacts/model_best.pt" ]; then
    python -m app.ml.evaluate_models && \
    python -m app.ml.select_best_model && \
    echo "RNN/LSTM/biLSTM trained and model_best selected." || \
    echo "Model pipeline skipped."
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
