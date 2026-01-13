@echo off
REM Psychiatric Benchmark Comparison Tool for Windows
REM This script runs the LLM benchmark comparison

echo.
echo ================================================================================
echo  PSYCHIATRIC KNOWLEDGE LLM BENCHMARK
echo ================================================================================
echo.
echo This tool will:
echo   1. Load the original PsychBench questions and answers
echo   2. Load Llama 3 benchmark results
echo   3. Query Mistral LLM with the same questions
echo   4. Compare all three sources
echo   5. Generate a detailed benchmark report
echo.
echo Requirements:
echo   - Ollama must be running with 'mistral' model
echo   - Backend directory must contain PsychBench JSON files
echo.
echo Starting benchmark...
echo ================================================================================
echo.

REM Get the directory of this script
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Run the benchmark
python compare_llm_benchmarks.py

REM Check if successful
if errorlevel 1 (
    echo.
    echo Benchmark failed - check errors above
    pause
    exit /b 1
) else (
    echo.
    echo ================================================================================
    echo BENCHMARK COMPLETED SUCCESSFULLY
    echo ================================================================================
    echo.
    echo Results saved to backend directory
    echo Look for: PsychBench-benchmark-mistral-results-*.json
    pause
    exit /b 0
)
