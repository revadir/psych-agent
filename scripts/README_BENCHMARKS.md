# Benchmark Scripts Directory

This directory contains all tools and utilities for running LLM benchmark comparisons.

## 📋 Files Overview

### Main Benchmarking Tool
- **`compare_llm_benchmarks.py`** - Main benchmarking engine
  - Loads original questions and Llama 3 results
  - Queries Mistral LLM via Ollama
  - Performs similarity analysis
  - Generates comprehensive reports
  - Exports JSON results

### Execution Scripts
- **`run_benchmark.bat`** - Windows batch script
  - Double-click to run on Windows
  - Handles all setup and execution
  
- **`run_benchmark.sh`** - Unix/Linux/Mac script
  - `chmod +x run_benchmark.sh && ./run_benchmark.sh`

### Setup & Verification
- **`setup_ollama.py`** - Ollama setup verification tool
  - Checks if Ollama is installed
  - Verifies server is running
  - Confirms Mistral model available
  - Tests connectivity
  - Run with: `python setup_ollama.py`

### Interactive Tools
- **`demo_benchmark.py`** - Interactive demo and testing tool
  - Step-by-step examples
  - Test individual components
  - Learn how to use the API
  - Run with: `python demo_benchmark.py`

### Documentation
- **`QUICK_START.md`** - Fast setup guide (5 min)
  - Prerequisites
  - How to run
  - Understanding output
  - Troubleshooting
  
- **`BENCHMARK_GUIDE.md`** - Complete documentation
  - Detailed feature description
  - Installation instructions
  - Advanced usage
  - Performance optimization
  - Citation information
  
- **`BENCHMARK_SUMMARY.md`** - Executive summary
  - What was created
  - Key features
  - Quick start
  - Analysis workflow

- **`README.md`** - This file

## 🚀 Quick Start (30 seconds)

### Prerequisites
```bash
# Install Ollama from https://ollama.ai
ollama pull mistral
ollama serve  # Keep running in background
```

### Run Benchmark

**Windows:**
```cmd
run_benchmark.bat
```

**Mac/Linux:**
```bash
python compare_llm_benchmarks.py
```

**Interactive Demo:**
```bash
python demo_benchmark.py
```

## 📊 What Each Tool Does

### compare_llm_benchmarks.py
**Purpose**: Run complete benchmark comparison workflow

**Features**:
- Loads 60 psychiatric knowledge questions
- Loads Llama 3 pre-computed results
- Queries Mistral LLM in real-time
- Calculates similarity scores
- Extracts and analyzes concepts
- Generates detailed reports
- Exports JSON results

**Usage**:
```bash
python compare_llm_benchmarks.py
```

### setup_ollama.py
**Purpose**: Verify Ollama installation and setup

**Checks**:
- ✓ Ollama installed
- ✓ Ollama server running
- ✓ Models available
- ✓ Mistral model present
- ✓ Can query Mistral successfully

**Usage**:
```bash
python setup_ollama.py
```

### demo_benchmark.py
**Purpose**: Interactive learning and testing

**Demos Available**:
1. Load benchmark data
2. Query Mistral LLM
3. Calculate text similarity
4. Extract concepts
5. Full evaluation workflow

**Usage**:
```bash
python demo_benchmark.py
```

## 📈 Benchmark Structure

60 questions across 6 sections:

| Section | Questions | Topics |
|---------|-----------|--------|
| Psychiatric Knowledge | 1-10 | Disorder definitions, core features |
| Clinical Text Understanding | 11-20 | Symptom interpretation |
| ICD-10 Diagnosis | 21-30 | Diagnostic coding |
| Differential Diagnosis | 31-40 | Distinguishing disorders |
| Medication Knowledge | 41-50 | Psychopharmacology |
| Long-Term Management | 51-60 | Treatment and outcomes |

## 📊 Output & Results

### Console Output
- Section-by-section performance
- Status distribution (EXCELLENT/GOOD/PARTIAL/POOR)
- Overall assessment and recommendations

### JSON Results
Saved as: `../backend/PsychBench-benchmark-mistral-results-{timestamp}.json`

Contains:
- All responses and evaluations
- Similarity scores
- Concept analysis
- Performance metrics

### Sample Output
```
📋 Section: Psychiatric Knowledge
Mistral Average Similarity: 0.78
Status Distribution:
  EXCELLENT: 7 (70%)
  GOOD: 2 (20%)
  PARTIAL: 1 (10%)
```

## 🔧 Troubleshooting

### Issue: "Cannot connect to Ollama"
**Solution**: 
```bash
ollama serve
# Keep running while benchmark executes
```

### Issue: "Mistral model not found"
**Solution**:
```bash
ollama pull mistral
```

### Issue: Very slow responses
**Normal for**: First run, CPU-only systems, model downloading

**Speedup**: Ensure GPU is available, wait for model cache

### Issue: Questions not found
**Solution**: Verify backend/ has:
- PsychBench-benchmark-test.json
- PsychBench-benchmark-test-results.json

### Verify Setup
```bash
python setup_ollama.py
```

## 💡 Python API Usage

### Basic Example
```python
from compare_llm_benchmarks import BenchmarkComparison

benchmark = BenchmarkComparison()
benchmark.load_original_benchmark()
benchmark.load_llama3_results()
benchmark.run_mistral_benchmark()
benchmark.compare_responses()
report = benchmark.generate_report()
benchmark.save_results()
```

### Custom Query
```python
response = benchmark.query_mistral("Your question here")
similarity = benchmark.calculate_similarity(expected, response)
concepts = benchmark.extract_key_concepts(response)
evaluation = benchmark.evaluate_response(q, expected, response)
```

## 📚 Documentation Structure

```
QUICK_START.md
├─ Prerequisites (2 min)
├─ Running (3 min)
├─ Understanding Output (5 min)
└─ Troubleshooting

BENCHMARK_GUIDE.md (Complete Reference)
├─ Overview
├─ Installation
├─ Usage Methods
├─ Benchmark Sections
├─ Performance Metrics
├─ Output Format
├─ Advanced Usage
├─ Optimization
└─ Support

BENCHMARK_SUMMARY.md (Executive Summary)
├─ What Was Created
├─ Features
├─ Quick Start
├─ Performance Metrics
├─ Generated Files
├─ Usage Examples
├─ Troubleshooting
└─ Next Steps
```

## 🎯 Typical Workflow

### 1. Setup (One-time: ~5 min)
```bash
# Install Ollama
# ollama pull mistral
# ollama serve
```

### 2. Verify Setup (~2 min)
```bash
python setup_ollama.py
# Should show all green checkmarks
```

### 3. Run Benchmark (~10-15 min)
```bash
run_benchmark.bat  # Windows
# or
python compare_llm_benchmarks.py  # Any OS
```

### 4. Analyze Results (~5 min)
- Review console output
- Open JSON results in viewer/spreadsheet
- Compare Llama 3 vs Mistral performance

### 5. Track Progress (Ongoing)
- Run periodically
- Monitor performance trends
- Identify improvement areas

## 📊 Performance Expectations

| Component | Time | Notes |
|-----------|------|-------|
| Load data | 2 sec | Reading JSON files |
| Query Mistral | 5-15 min | 60 questions @ 5-15 sec each |
| Analysis | 30 sec | Similarity calculation |
| Report Gen | 10 sec | Formatting and export |
| **Total** | **5-20 min** | Depends on hardware |

## 🔍 Key Metrics Explained

### Similarity Score (0-1)
- Measures how close response is to expected answer
- Uses sequence matching algorithm
- Accounts for phrase ordering and content

### Concept Overlap
- Percentage of key terms from expected answer in response
- Measures conceptual understanding
- Range: 0-100%

### Status Ratings
- **EXCELLENT**: ≥0.7 similarity
- **GOOD**: 0.5-0.7 similarity
- **PARTIAL**: 0.3-0.5 similarity
- **POOR**: <0.3 similarity

## 🎓 Learning Resources

1. **Quick Demo** (10 min)
   ```bash
   python demo_benchmark.py
   ```

2. **Read QUICK_START.md** (5 min)

3. **Explore BENCHMARK_GUIDE.md** (15 min)

4. **Run actual benchmark** (15 min)

5. **Analyze results** (10 min)

## ✨ Advanced Topics

### Custom Similarity Metrics
```python
# Implement custom similarity calculation
def my_similarity(text1, text2):
    # Your implementation
    return score
```

### Batch Testing
```python
models = ['mistral', 'neural-chat']
for model in models:
    # Run benchmark for each
```

### Parallel Queries
```python
from concurrent.futures import ThreadPoolExecutor
# Submit multiple queries simultaneously
```

## 📞 Support

1. **Quick Issue?** → Check QUICK_START.md "Troubleshooting"
2. **Setup Problem?** → Run `python setup_ollama.py`
3. **Want to Learn?** → Run `python demo_benchmark.py`
4. **Need Details?** → Read BENCHMARK_GUIDE.md

## 📝 Version Info

- **Version**: 1.0
- **Created**: January 2026
- **Status**: Production Ready ✅
- **Python**: 3.8+
- **Requirements**: requests library

## 🚀 Next Steps

1. Install Ollama and run `ollama serve`
2. Run `python setup_ollama.py` to verify setup
3. Run `run_benchmark.bat` (Windows) or `python compare_llm_benchmarks.py`
4. Review generated results and report
5. Track improvements over time

---

**Ready to benchmark your LLMs?** Start with QUICK_START.md! 🚀
