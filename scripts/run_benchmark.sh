#!/usr/bin/env python3
"""
Quick benchmark runner script
Run this to start the LLM benchmark comparison
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from compare_llm_benchmarks import BenchmarkComparison

def main():
    """Run benchmark with user-friendly interface"""
    
    print("\n" + "="*80)
    print("🧠 PSYCHIATRIC KNOWLEDGE LLM BENCHMARK")
    print("="*80)
    print("\nThis tool will:")
    print("  1. Load the original PsychBench questions and answers")
    print("  2. Load Llama 3 benchmark results")
    print("  3. Query Mistral LLM with the same questions")
    print("  4. Compare all three sources")
    print("  5. Generate a detailed benchmark report")
    print("\n⚠️  Requirements:")
    print("  - Ollama must be running with 'mistral' model")
    print("  - Backend directory must contain PsychBench JSON files")
    print("\nStarting benchmark in 3 seconds...")
    print("-"*80 + "\n")
    
    # Initialize and run
    benchmark = BenchmarkComparison()
    
    try:
        success = benchmark.run_full_benchmark()
        
        if success:
            print("\n" + "="*80)
            print("✅ BENCHMARK COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"\n📁 Results saved to backend directory")
            print("   Look for: PsychBench-benchmark-mistral-results-*.json")
            return 0
        else:
            print("\n❌ Benchmark failed - check the errors above")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Benchmark interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
