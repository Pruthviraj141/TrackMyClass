#!/bin/bash
echo "Terminating any existing process on port 8000..."
pid=$(lsof -t -i:8000)
if [ ! -z "$pid" ]; then
    kill -9 $pid
    echo "Killed PID $pid"
fi
sleep 2

source venv/bin/activate
echo "Starting FastAPI Real Server..."
export PYTHONPATH=$(pwd)
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend_real.log 2>&1 &
UVICORN_PID=$!
echo $UVICORN_PID > uvicorn_real.pid

echo "Waiting 10 seconds for Uvicorn bindings and PyTorch model loading..."
sleep 15
echo "Uvicorn available, running concurrency test!"
python benchmarks/concurrency_test.py

kill -9 $UVICORN_PID
echo "Server terminated."
