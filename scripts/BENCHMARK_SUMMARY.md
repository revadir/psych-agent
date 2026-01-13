# LLM Benchmark Comparison Tool - Summary

## 📋 What Was Created

A complete benchmarking system to compare psychiatric knowledge across three LLMs:

### Core Components

1. **compare_llm_benchmarks.py** (Main Tool)
   - Loads original benchmark questions
   - Loads Llama 3 results
   - Queries Mistral LLM in real-time
   - Compares all three sources
   - Generates detailed reports
   - Exports JSON results

2. **Execution Scripts**
   - `run_benchmark.bat` - Windows runner
   - `run_benchmark.sh` - Unix/Linux runner
   - Direct Python execution supported

3. **Helper Tools**
   - `setup_ollama.py` - Verifies Ollama setup
   - Checks if Mistral model is available
   - Tests connectivity and query capability

4. **Documentation**
   - `QUICK_START.md` - Fast setup guide
   - `BENCHMARK_GUIDE.md` - Comprehensive guide
   - Inline code documentation

## 🎯 Features

### Data Processing
- ✅ Loads PsychBench-benchmark-test.json (60 original Q&A pairs)
- ✅ Reads PsychBench-benchmark-test-results.json (Llama 3 responses)
- ✅ Queries Mistral via Ollama API in real-time
- ✅ Handles long responses with truncation

### Analysis & Metrics
- ✅ **Similarity Scoring**: Semantic similarity calculation (0-1 scale)
- ✅ **Concept Extraction**: Identifies key concepts in responses
- ✅ **Concept Overlap Analysis**: Measures conceptual match between expected and actual
- ✅ **Status Classification**: Rates responses as EXCELLENT/GOOD/PARTIAL/POOR
- ✅ **Section-wise Statistics**: Per-section performance analysis

### Reporting
- ✅ Console output with formatted results
- ✅ Section-by-section comparison
- ✅ Overall performance metrics
- ✅ JSON export for further analysis
- ✅ Performance recommendations

## 📊 Benchmark Structure

The benchmark contains **60 questions** across **6 sections**:

```
1. Psychiatric Knowledge (Q1-10)
   - Core features of disorders
   - Clinical definitions

2. Clinical Text Understanding (Q11-20)
   - Symptom interpretation
   - Clinical assessment

3. Principal Diagnosis ICD-10 (Q21-30)
   - Diagnosis coding
   - Severity assessment

4. Differential Diagnosis (Q31-40)
   - Distinguishing disorders
   - Medical exclusion

5. Medication Knowledge (Q41-50)
   - Drug classifications
   - Side effects

6. Long-Term Course Management (Q51-60)
   - Treatment outcomes
   - Recovery patterns
```

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull Mistral model
ollama pull mistral

# 3. Start Ollama server
ollama serve
```

### Run Benchmark

**Windows:**
```cmd
cd scripts
run_benchmark.bat
```

**Mac/Linux:**
```bash
cd scripts
python compare_llm_benchmarks.py
```

### Output
- Console report with section-by-section analysis
- JSON results saved to `backend/PsychBench-benchmark-mistral-results-{timestamp}.json`

## 📈 Performance Metrics

### Similarity Scores
- **0.0-0.3**: POOR - Significant gaps
- **0.3-0.5**: PARTIAL - Covers key points
- **0.5-0.7**: GOOD - Solid understanding
- **0.7-1.0**: EXCELLENT - Strong knowledge

### Status Distribution
Shows percentage of responses in each category per section.

### Overall Assessment
Final performance rating with recommendations.

## 🔍 Key Differences from Llama 3

The tool enables comparison of:
- Response accuracy (similarity to expected answers)
- Conceptual understanding (key terms mentioned)
- Response quality across different domains
- Overall psychiatric knowledge gaps

## 📁 Generated Files

After running the benchmark:

```
backend/
└── PsychBench-benchmark-mistral-results-2026-01-10T12-34-56.json
    ├── timestamp
    ├── benchmark_name
    ├── mistral_results
    │   ├── Psychiatric Knowledge
    │   ├── Clinical Text Understanding
    │   ├── Principal Diagnosis (ICD-10)
    │   ├── Differential Diagnosis
    │   ├── Medication Knowledge
    │   └── Long-Term Course Management
    ├── comparison_summary
    └── metrics
        ├── overall_similarity
        └── total_questions
```

## 💡 Usage Examples

### Example 1: Run Full Benchmark
```bash
python compare_llm_benchmarks.py
# Automatically runs full workflow and generates report
```

### Example 2: Python API
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

### Example 3: Custom Analysis
```python
# Calculate similarity for specific question
similarity = benchmark.calculate_similarity(
    "Persistent depressed mood",
    mistral_response
)

# Extract concepts
concepts = benchmark.extract_key_concepts(mistral_response)

# Check concept overlap
overlap = benchmark.check_concept_overlap(expected, response)
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Cannot connect to Ollama" | Start Ollama: `ollama serve` |
| "Mistral model not found" | Install: `ollama pull mistral` |
| "Questions not found" | Verify backend/ has JSON files |
| "Very slow responses" | Normal for CPU or first run |

Run setup verification:
```bash
python setup_ollama.py
```

## 📊 Analysis Workflow

1. **Load Data** (5 sec)
   - Original questions & answers
   - Llama 3 results

2. **Query Mistral** (5-10 min)
   - Send 60 questions
   - Collect responses
   - Track status

3. **Compare** (30 sec)
   - Calculate similarities
   - Extract concepts
   - Analyze patterns

4. **Report** (Instant)
   - Generate console report
   - Export JSON results
   - Show recommendations

## 🎓 Benchmark Coverage

Tests knowledge of:
- ✅ DSM-5-TR diagnostic criteria
- ✅ ICD-10 diagnostic codes
- ✅ Psychiatric symptoms and presentations
- ✅ Differential diagnosis principles
- ✅ Psychopharmacology
- ✅ Treatment and course management

## 🔧 Advanced Features

- **Concept-based evaluation** beyond keyword matching
- **Temporal tracking** (run benchmarks over time)
- **Multi-model comparison** (easily add more models)
- **Batch processing** support
- **Customizable similarity metrics**
- **API-based results export**

## 📝 Output Example

```
================================================================================
PSYCHBENCH LLM COMPARISON REPORT
================================================================================
Generated: 2026-01-10 12:34:56

EXECUTIVE SUMMARY
...

📋 Section: Psychiatric Knowledge
Mistral Average Similarity: 0.78
Status Distribution (Mistral):
  EXCELLENT: 7 (70.0%)
  GOOD: 2 (20.0%)
  PARTIAL: 1 (10.0%)

Mistral Performance Assessment: GOOD
Overall Similarity Score: 0.72
```

## 🎯 Next Steps

1. **Run the benchmark**
   - `run_benchmark.bat` (Windows) or Python command

2. **Review results**
   - Check console output
   - Open JSON results file

3. **Compare performance**
   - Llama 3 vs Mistral
   - Identify strengths/weaknesses

4. **Track improvements**
   - Run periodically
   - Monitor trends
   - Optimize prompt engineering

## 📚 Documentation

- **QUICK_START.md** - Fast setup (5 min read)
- **BENCHMARK_GUIDE.md** - Full documentation (15 min read)
- **compare_llm_benchmarks.py** - Inline code documentation
- **setup_ollama.py** - Setup verification tool

## ✨ Key Achievements

✅ Automated multi-LLM comparison system  
✅ Semantic similarity-based evaluation  
✅ Comprehensive reporting framework  
✅ JSON export for analysis  
✅ Easy-to-use command-line interface  
✅ Cross-platform support (Windows/Mac/Linux)  
✅ Extensive documentation  

## 🚀 Ready to Use!

Everything is set up and ready to run. Just:

1. Ensure Ollama is installed and Mistral model is available
2. Start Ollama server: `ollama serve`
3. Run the benchmark: `python compare_llm_benchmarks.py` or `run_benchmark.bat`
4. Review the generated report and results!

---

**Created**: January 10, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
