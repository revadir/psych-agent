# 📋 LLM Benchmark Comparison Tool - Index

## 🎯 Overview

A complete system for benchmarking and comparing psychiatric knowledge across multiple LLMs (Llama 3 and Mistral).

---

## 📁 New Files Created

### Main Benchmarking Tool
```
scripts/
├── compare_llm_benchmarks.py      ⭐ MAIN TOOL
│   • 500+ line comprehensive benchmarking engine
│   • Loads original questions and Llama 3 results
│   • Queries Mistral LLM via Ollama
│   • Calculates similarity and concept analysis
│   • Generates detailed reports
│   • Exports JSON results
```

### Execution Scripts
```
├── run_benchmark.bat              💻 WINDOWS RUNNER
│   • Double-click to run on Windows
│   • Handles all setup automatically
│   
├── run_benchmark.sh               🐧 UNIX RUNNER  
│   • For Mac/Linux systems
│   • chmod +x && ./run_benchmark.sh
```

### Utility Tools
```
├── demo_benchmark.py              🎓 INTERACTIVE DEMO
│   • Learn how to use the tool
│   • Test individual features
│   • Step-by-step examples
│   • Interactive menu
│
├── setup_ollama.py                🔧 SETUP VERIFICATION
│   • Checks Ollama installation
│   • Verifies Mistral model
│   • Tests connectivity
│   • Recommends fixes
```

### Documentation
```
├── QUICK_START.md                 ⚡ FAST GUIDE (5 min)
│   • Prerequisites
│   • How to run
│   • Understanding output
│   • Quick troubleshooting
│
├── BENCHMARK_GUIDE.md             📖 COMPLETE REFERENCE
│   • Detailed features
│   • Installation steps
│   • Advanced usage
│   • Performance optimization
│   • Citation info
│
├── BENCHMARK_SUMMARY.md           📊 EXECUTIVE SUMMARY
│   • What was created
│   • Feature list
│   • Usage examples
│   • Analysis workflow
│
├── README_BENCHMARKS.md           📚 DIRECTORY GUIDE
│   • File overview
│   • Tool descriptions
│   • Usage patterns
│   • Troubleshooting
```

### Main Documentation
```
root/
├── INSTALLATION_COMPLETE.md       ✅ COMPLETION SUMMARY
    • What was created
    • Quick start guide
    • Feature overview
    • Next steps
```

---

## 🚀 Quick Start

### Step 1: Prerequisites (One-time setup)
```bash
# Install Ollama from https://ollama.ai
ollama pull mistral
```

### Step 2: Start Ollama Server
```bash
ollama serve
```
Keep this running in background!

### Step 3: Run Benchmark
```bash
cd c:\Users\sushm\psych-agent\scripts

# Windows:
run_benchmark.bat

# Mac/Linux:
python compare_llm_benchmarks.py
```

### Step 4: Review Results
- Read console output for summary
- Check JSON file in backend/ for detailed results

---

## 📊 What Each Tool Does

### compare_llm_benchmarks.py (MAIN)
**The Core Benchmarking Engine**

Features:
- Load 60 psychiatric questions with expected answers
- Load Llama 3 pre-computed responses
- Query Mistral LLM with same questions
- Calculate similarity (0-1 scale)
- Extract and analyze concepts
- Compare all three sources
- Generate detailed reports
- Export JSON results

Usage:
```bash
python compare_llm_benchmarks.py
```

### demo_benchmark.py (LEARNING)
**Interactive Learning Tool**

Run demos for:
1. Loading benchmark data
2. Querying Mistral
3. Calculating similarity
4. Concept extraction
5. Full evaluation workflow

Usage:
```bash
python demo_benchmark.py
# Choose demos from interactive menu
```

### setup_ollama.py (VERIFICATION)
**Setup Verification & Troubleshooting**

Checks:
- ✓ Ollama installed
- ✓ Ollama server running
- ✓ Models available
- ✓ Mistral model installed
- ✓ Can query Mistral

Usage:
```bash
python setup_ollama.py
```

### run_benchmark.bat / .sh (EXECUTION)
**One-Click Benchmark Running**

Windows:
```cmd
run_benchmark.bat
```

Unix/Linux:
```bash
./run_benchmark.sh
```

---

## 📈 Benchmark Details

### Questions Covered
- **60 Total Questions** across 6 sections
- **Sections**:
  1. Psychiatric Knowledge (Q1-10)
  2. Clinical Understanding (Q11-20)
  3. ICD-10 Diagnosis (Q21-30)
  4. Differential Diagnosis (Q31-40)
  5. Medications (Q41-50)
  6. Long-term Management (Q51-60)

### Sources Compared
1. **Original Answers** - Reference/source answers
2. **Llama 3** - Pre-computed results
3. **Mistral** - Real-time queries via Ollama

### Metrics Calculated
- **Similarity Score** (0-1 scale)
- **Concept Overlap** (% of key terms)
- **Status Rating** (EXCELLENT/GOOD/PARTIAL/POOR)
- **Section Performance** (per section)
- **Overall Assessment** (final score)

---

## 📖 Documentation Guide

| Document | Read Time | Purpose | Audience |
|----------|-----------|---------|----------|
| **QUICK_START.md** | 5 min | Get running | Everyone |
| **demo_benchmark.py** | 10 min | Learn tool | Developers |
| **BENCHMARK_GUIDE.md** | 15 min | Deep dive | Analysts |
| **Code comments** | 20 min | Advanced | Developers |

### Reading Path

**For Quick Setup (15 min):**
1. Read INSTALLATION_COMPLETE.md
2. Read QUICK_START.md
3. Run setup_ollama.py
4. Run compare_llm_benchmarks.py

**For Learning (45 min):**
1. Read QUICK_START.md
2. Run demo_benchmark.py
3. Read BENCHMARK_GUIDE.md
4. Run benchmark and analyze

**For Deep Understanding (2 hours):**
1. Read all docs
2. Run all demos
3. Review source code
4. Create custom analysis

---

## ⚡ Performance Guide

| Task | Time | Notes |
|------|------|-------|
| Load data | ~2 sec | File I/O |
| Query Mistral | 5-15 min | 60 questions |
| Analysis | ~30 sec | Calculations |
| Report generation | ~10 sec | Formatting |
| **Total** | **6-20 min** | Hardware dependent |

Factors affecting speed:
- First run slower (model cache)
- GPU faster than CPU
- Ollama memory usage
- Network latency

---

## 🛠️ Troubleshooting Flow

```
Issue: Cannot connect to Ollama
└─> Fix: ollama serve

Issue: Mistral not found
└─> Fix: ollama pull mistral

Issue: Very slow
└─> Fix: Wait (first run) or check GPU

Issue: Questions not found
└─> Fix: Verify backend/ files exist

Issue: Still stuck?
└─> Run: python setup_ollama.py
```

---

## 💡 Usage Examples

### Example 1: One-Click (Easiest)
```cmd
run_benchmark.bat
```
Done! Check results.

### Example 2: Python Direct
```bash
python compare_llm_benchmarks.py
```

### Example 3: Interactive Learning
```bash
python demo_benchmark.py
```
Choose demos to explore.

### Example 4: Setup Verification
```bash
python setup_ollama.py
```
Verify everything working.

### Example 5: Python API
```python
from compare_llm_benchmarks import BenchmarkComparison

benchmark = BenchmarkComparison()
benchmark.run_full_benchmark()
```

---

## 📊 Expected Output

### Console Report Example
```
================================================================================
PSYCHBENCH LLM COMPARISON REPORT
================================================================================

📋 Section: Psychiatric Knowledge
Mistral Average Similarity: 0.78
Status Distribution (Mistral):
  EXCELLENT: 7 (70.0%)
  GOOD: 2 (20.0%)
  PARTIAL: 1 (10.0%)

Mistral Performance Assessment: GOOD
Overall Similarity Score: 0.72
```

### Files Generated
```
backend/
└── PsychBench-benchmark-mistral-results-2026-01-10T12-34-56.json
```

---

## ✅ System Requirements

**Required:**
- Python 3.8+
- Ollama (https://ollama.ai)
- 8 GB RAM minimum
- 20 GB disk (for Mistral)
- Internet (initial download)

**Recommended:**
- Python 3.10+
- 16 GB RAM
- 50 GB disk
- NVIDIA GPU with CUDA

---

## 🎯 Next Steps

### Immediate (Now)
1. [ ] Verify Ollama installed
2. [ ] Run `ollama pull mistral`
3. [ ] Start `ollama serve`

### Short-term (Today)
1. [ ] Run `python setup_ollama.py`
2. [ ] Run `run_benchmark.bat` or Python version
3. [ ] Review results

### Medium-term (This Week)
1. [ ] Run `python demo_benchmark.py`
2. [ ] Read BENCHMARK_GUIDE.md
3. [ ] Analyze results by section
4. [ ] Identify improvement areas

### Long-term (Ongoing)
1. [ ] Run benchmarks periodically
2. [ ] Track performance trends
3. [ ] Test new models
4. [ ] Optimize prompts

---

## 🔍 File Locations

### Scripts Directory
```
scripts/
├── compare_llm_benchmarks.py      [MAIN TOOL]
├── demo_benchmark.py              [LEARNING]
├── setup_ollama.py                [VERIFICATION]
├── run_benchmark.bat              [WINDOWS]
├── run_benchmark.sh               [UNIX]
├── QUICK_START.md                 [5-MIN GUIDE]
├── BENCHMARK_GUIDE.md             [FULL DOCS]
├── BENCHMARK_SUMMARY.md           [SUMMARY]
└── README_BENCHMARKS.md           [DIRECTORY]
```

### Root Directory
```
root/
└── INSTALLATION_COMPLETE.md       [THIS INDEX]
```

### Backend Directory (Generated)
```
backend/
└── PsychBench-benchmark-mistral-results-*.json
```

---

## 📞 Getting Help

1. **Setup Issues** → Run `python setup_ollama.py`
2. **How to Use** → Read `QUICK_START.md`
3. **Learn Features** → Run `python demo_benchmark.py`
4. **Deep Dive** → Read `BENCHMARK_GUIDE.md`
5. **Troubleshooting** → Check QUICK_START.md section

---

## ✨ Key Features Summary

- ✅ Automated multi-LLM comparison
- ✅ Semantic similarity analysis
- ✅ Concept extraction & overlap
- ✅ Comprehensive reporting
- ✅ JSON export for analysis
- ✅ Easy-to-use interface
- ✅ Cross-platform (Windows/Mac/Linux)
- ✅ Extensive documentation
- ✅ Interactive learning tools
- ✅ Setup verification

---

## 📝 Version Info

- **Version**: 1.0
- **Created**: January 10, 2026
- **Status**: Production Ready ✅
- **Python Required**: 3.8+
- **Ollama Required**: Latest version

---

## 🚀 You're Ready!

Everything is installed and documented. 

**Start here:**
```bash
# Step 1: Verify setup
python scripts/setup_ollama.py

# Step 2: Run benchmark  
cd scripts
run_benchmark.bat  # Windows
# or
python compare_llm_benchmarks.py  # Any OS
```

**Questions?**
- Quick questions → QUICK_START.md
- How-to questions → demo_benchmark.py
- Technical questions → BENCHMARK_GUIDE.md

**Time needed:** 15 minutes to first results!

---

**Happy benchmarking! 🧠**
