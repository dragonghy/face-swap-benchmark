import uvicorn

if __name__ == "__main__":
    print("Starting Face Swap Benchmark Web Interface...")
    print("Open your browser to http://localhost:8000")
    print("Press Ctrl+C to exit")
    uvicorn.run("benchmark.web.main:app", host="0.0.0.0", port=8000, reload=True)