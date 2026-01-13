"""
LLM Benchmark Comparison Tool
Compares psychiatric knowledge benchmark results from multiple LLMs:
- Original Answers (Source)
- Llama 3 Results
- Mistral LLM Results

Generates detailed benchmark analysis and comparison report.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set UTF-8 encoding for Windows console output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Try to import from the project's services
try:
    from langchain.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("LangChain Ollama not available, will use direct requests")


class BenchmarkComparison:
    """Main class for comparing LLM benchmark results"""

    def __init__(self, base_path: str = None):
        """
        Initialize benchmark comparison tool
        
        Args:
            base_path: Base path for benchmark files (defaults to backend directory)
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent / "backend"
        else:
            base_path = Path(base_path)
        
        self.base_path = base_path
        self.benchmark_test = None
        self.llama3_results = None
        self.mistral_results = {}
        self.comparison_results = {}
        self.metrics = {}
        self.output_files = {}  # Track output file handles for streaming
        self.question_count = 0  # Track total questions processed
        self.failed_questions = []  # Track failed questions for retry
        self.retry_results = []  # Track retry attempts

    def load_original_benchmark(self) -> bool:
        """Load the original benchmark test questions and answers"""
        try:
            filepath = self.base_path / "PsychBench-benchmark-test.json"
            with open(filepath, 'r', encoding='utf-8') as f:
                self.benchmark_test = json.load(f)
            print(f"✅ Loaded original benchmark test from {filepath}")
            return True
        except FileNotFoundError:
            print(f"❌ Original benchmark test not found at {filepath}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding original benchmark: {e}")
            return False

    def load_llama3_results(self) -> bool:
        """Load Llama 3 benchmark results"""
        try:
            filepath = self.base_path / "PsychBench-benchmark-test-results.json"
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                self.llama3_results = json.load(f)
            print(f"✅ Loaded Llama 3 results from {filepath}")
            return True
        except FileNotFoundError:
            print(f"❌ Llama 3 results not found at {filepath}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding Llama 3 results: {e}")
            return False

    def query_mistral(self, question: str, model: str = "mistral", max_retries: int = 3) -> str:
        """
        Query Mistral LLM via Ollama with streaming and comprehensive error handling
        
        Args:
            question: The question to ask
            model: The Ollama model to use
            max_retries: Maximum number of retries on failure
            
        Returns:
            The LLM response text or empty string on failure
        """
        import time
        
        for attempt in range(max_retries):
            try:
                # Add delay between retries to avoid overwhelming the server
                if attempt > 0:
                    time.sleep(2)
                
                # Use streaming API for faster response collection
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": question,
                        "stream": True,
                        "temperature": 0.1
                    },
                    timeout=60,  # 60 seconds timeout
                    stream=True
                )
                
                if response.status_code == 200:
                    # Collect streaming response with better error handling
                    full_response = ""
                    chunk_count = 0
                    try:
                        for line in response.iter_lines(decode_unicode=True):
                            if line:
                                try:
                                    chunk = json.loads(line)
                                    full_response += chunk.get("response", "")
                                    chunk_count += 1
                                    # Check if this is the last chunk
                                    if chunk.get("done", False):
                                        break
                                except json.JSONDecodeError:
                                    # Skip malformed JSON lines
                                    continue
                    except (ConnectionError, OSError) as stream_error:
                        # Connection interrupted during streaming - return what we have
                        if full_response:
                            return full_response.strip()
                        if attempt < max_retries - 1:
                            continue
                        return ""
                    
                    return full_response.strip() if full_response else ""
                else:
                    if attempt < max_retries - 1:
                        continue
                    print(f"⚠️  Ollama returned status {response.status_code}")
                    return ""
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    continue
                print(f"⚠️  Timeout querying Mistral (60s exceeded)")
                return ""
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    continue
                print(f"⚠️  Cannot connect to Ollama at localhost:11434")
                print("   Make sure Ollama is running: ollama serve")
                return ""
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                print(f"⚠️  Error querying Mistral: {type(e).__name__}: {e}")
                return ""
        
        return ""

    def extract_sections(self) -> List[Dict]:
        """Extract sections from benchmark test"""
        if not self.benchmark_test:
            return []
        return self.benchmark_test.get("psychbench_medium_benchmark", {}).get("sections", [])

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using Cosine Similarity with TF-IDF
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        text1_clean = text1.lower().strip()
        text2_clean = text2.lower().strip()
        
        # If texts are identical
        if text1_clean == text2_clean:
            return 1.0
        
        try:
            # Use TF-IDF vectorization with character n-grams for better semantic similarity
            vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3), lowercase=True)
            tfidf_matrix = vectorizer.fit_transform([text1_clean, text2_clean])
            
            # Compute cosine similarity
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(cosine_sim[0][0])
        except Exception as e:
            # Fallback to character-level similarity if TF-IDF fails
            print(f"Warning: TF-IDF similarity calculation failed: {e}")
            # Simple character overlap as fallback
            overlap = sum(1 for a, b in zip(text1_clean, text2_clean) if a == b)
            max_len = max(len(text1_clean), len(text2_clean))
            return overlap / max_len if max_len > 0 else 0.0

    def extract_key_concepts(self, text: str) -> set:
        """Extract key concepts from response text"""
        # Simple keyword extraction
        words = set(re.findall(r'\b[a-z]{4,}\b', text.lower()))
        return words

    def check_concept_overlap(self, expected: str, actual: str) -> Dict[str, Any]:
        """Check if key concepts from expected answer appear in actual response"""
        expected_concepts = self.extract_key_concepts(expected)
        actual_concepts = self.extract_key_concepts(actual)
        
        overlap = expected_concepts.intersection(actual_concepts)
        overlap_ratio = len(overlap) / max(len(expected_concepts), 1)
        
        return {
            "expected_concepts": list(expected_concepts),
            "actual_concepts": list(actual_concepts),
            "overlap": list(overlap),
            "overlap_ratio": overlap_ratio
        }

    def evaluate_response(self, question: str, expected_answer: str, response: str) -> Dict[str, Any]:
        """
        Evaluate a response against expected answer
        
        Args:
            question: The question asked
            expected_answer: The expected/reference answer
            response: The LLM response
            
        Returns:
            Dictionary with evaluation metrics
        """
        if not response:
            return {
                "question": question,
                "expected": expected_answer,
                "response": response,
                "similarity": 0.0,
                "status": "NO_RESPONSE"
            }

        similarity = self.calculate_similarity(expected_answer, response)
        concept_analysis = self.check_concept_overlap(expected_answer, response)
        
        # Determine evaluation status
        if similarity >= 0.7:
            status = "EXCELLENT"
        elif similarity >= 0.5:
            status = "GOOD"
        elif similarity >= 0.3:
            status = "PARTIAL"
        else:
            status = "POOR"
        
        return {
            "question": question,
            "expected": expected_answer,
            "response": response[:500],  # Truncate long responses
            "similarity": round(similarity, 3),
            "concept_overlap": concept_analysis["overlap_ratio"],
            "status": status
        }

    def run_mistral_benchmark(self, stream_output_file: Optional[str] = None) -> bool:
        """Run benchmark tests with Mistral LLM with streaming output and retry logic"""
        print("\n" + "="*80)
        print("🚀 Starting Mistral LLM Benchmark Tests...")
        print("="*80)
        
        # Initialize streaming file if provided
        streaming_data = {
            "timestamp": datetime.now().isoformat(),
            "benchmark_name": "PsychBench Mistral Streaming Results",
            "status": "IN_PROGRESS",
            "round": 1,
            "sections": {},
            "failed_questions": []
        }
        
        if stream_output_file is None:
            stream_output_file = self.base_path / f"PsychBench-benchmark-streaming-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        sections = self.extract_sections()
        total_questions = 0
        answered_questions = 0
        
        try:
            # ROUND 1: Initial benchmark run
            print("\n📍 ROUND 1: Initial Benchmark Run")
            print("="*80)
            
            for section in sections:
                section_name = section.get("name", "Unknown")
                print(f"\n📝 Testing Section: {section_name}")
                print("-" * 60)
                
                self.mistral_results[section_name] = []
                streaming_data["sections"][section_name] = []
                
                for item in section.get("items", []):
                    try:
                        question = item.get("question", "")
                        expected_answer = item.get("answer", "")
                        item_id = item.get("id", 0)
                        
                        total_questions += 1
                        self.question_count += 1
                        
                        print(f"  [Q{item_id}] {question[:60]}...", end=" ", flush=True)
                        
                        response = self.query_mistral(question)
                        
                        if response:
                            answered_questions += 1
                            print("✓")
                        else:
                            print("✗ (No response)")
                            # Track failed question
                            self.failed_questions.append({
                                "section": section_name,
                                "question_id": item_id,
                                "question": question,
                                "expected_answer": expected_answer,
                                "attempts": 1
                            })
                        
                        evaluation = self.evaluate_response(question, expected_answer, response)
                        self.mistral_results[section_name].append(evaluation)
                        
                        # Stream this result to file after each question
                        streaming_result = {
                            "question_id": item_id,
                            "question": question,
                            "ground_truth": expected_answer,
                            "mistral_response": response,
                            "evaluation": evaluation,
                            "timestamp": datetime.now().isoformat(),
                            "round": 1,
                            "status": "success" if response else "failed"
                        }
                        streaming_data["sections"][section_name].append(streaming_result)
                        
                        # Write streaming results to file
                        self._write_streaming_results(stream_output_file, streaming_data)
                        
                    except Exception as e:
                        print(f"\n❌ Error processing Q{item_id}: {e}")
                        # Track failed question
                        self.failed_questions.append({
                            "section": section_name,
                            "question_id": item_id,
                            "question": question,
                            "expected_answer": expected_answer,
                            "error": str(e),
                            "attempts": 1
                        })
                        continue
            
            print(f"\n✅ Round 1 Complete: {answered_questions}/{total_questions} questions answered")
            print(f"⚠️  Failed questions: {len(self.failed_questions)}")
            
            # ROUND 2: Retry failed questions
            if self.failed_questions:
                print("\n" + "="*80)
                print(f"🔄 ROUND 2: Retrying {len(self.failed_questions)} Failed Questions")
                print("="*80)
                
                streaming_data["round"] = 2
                retry_successful = 0
                
                for failed_q in self.failed_questions:
                    try:
                        section_name = failed_q["section"]
                        item_id = failed_q["question_id"]
                        question = failed_q["question"]
                        expected_answer = failed_q["expected_answer"]
                        
                        print(f"\n  🔄 Retrying [Q{item_id}] {question[:60]}...", end=" ", flush=True)
                        
                        response = self.query_mistral(question)
                        
                        if response:
                            retry_successful += 1
                            print("✓ (Recovered)")
                            failed_q["status"] = "recovered"
                        else:
                            print("✗ (Still failed - skip for now)")
                            failed_q["status"] = "persistent_failure"
                        
                        failed_q["retry_response"] = response
                        failed_q["attempts"] = 2
                        
                        # Update the result in mistral_results
                        if section_name in self.mistral_results:
                            section_items = self.mistral_results[section_name]
                            # Find and update the corresponding item
                            for i, item in enumerate(section_items):
                                if item.get("question", "") == question:
                                    evaluation = self.evaluate_response(question, expected_answer, response)
                                    section_items[i] = evaluation
                                    
                                    # Add retry result to streaming
                                    retry_stream_result = {
                                        "question_id": item_id,
                                        "question": question,
                                        "ground_truth": expected_answer,
                                        "mistral_response": response,
                                        "evaluation": evaluation,
                                        "timestamp": datetime.now().isoformat(),
                                        "round": 2,
                                        "status": "success" if response else "failed",
                                        "retry": True
                                    }
                                    streaming_data["sections"][section_name].append(retry_stream_result)
                                    self._write_streaming_results(stream_output_file, streaming_data)
                                    break
                        
                        self.retry_results.append(failed_q)
                        
                    except Exception as e:
                        print(f"\n❌ Error retrying Q{item_id}: {e}")
                        failed_q["retry_error"] = str(e)
                        failed_q["status"] = "retry_error"
                        self.retry_results.append(failed_q)
                        continue
                
                print(f"\n✅ Round 2 Complete: {retry_successful}/{len(self.failed_questions)} recovered")
                
                # Update answered questions count
                answered_questions += retry_successful
                
                # ROUND 3: Third and final retry for persistent failures
                still_failed = [q for q in self.retry_results if q.get("status") == "persistent_failure"]
                if still_failed:
                    print("\n" + "="*80)
                    print(f"🔄 ROUND 3: Final Attempt for {len(still_failed)} Persistent Failures")
                    print("="*80)
                    
                    streaming_data["round"] = 3
                    final_recovery = 0
                    
                    for failed_q in still_failed:
                        try:
                            section_name = failed_q["section"]
                            item_id = failed_q["question_id"]
                            question = failed_q["question"]
                            expected_answer = failed_q["expected_answer"]
                            
                            print(f"\n  🔄 Final Retry [Q{item_id}] {question[:60]}...", end=" ", flush=True)
                            
                            response = self.query_mistral(question)
                            
                            if response:
                                final_recovery += 1
                                print("✓ (Recovered)")
                                failed_q["status"] = "recovered_round3"
                            else:
                                print("✗ (Skipping - will retry later)")
                                failed_q["status"] = "skipped_after_3_retries"
                            
                            failed_q["final_response"] = response
                            failed_q["attempts"] = 3
                            
                            # Update the result in mistral_results
                            if section_name in self.mistral_results and response:
                                section_items = self.mistral_results[section_name]
                                for i, item in enumerate(section_items):
                                    if item.get("question", "") == question:
                                        evaluation = self.evaluate_response(question, expected_answer, response)
                                        section_items[i] = evaluation
                                        
                                        final_stream_result = {
                                            "question_id": item_id,
                                            "question": question,
                                            "ground_truth": expected_answer,
                                            "mistral_response": response,
                                            "evaluation": evaluation,
                                            "timestamp": datetime.now().isoformat(),
                                            "round": 3,
                                            "status": "success",
                                            "retry": True
                                        }
                                        streaming_data["sections"][section_name].append(final_stream_result)
                                        self._write_streaming_results(stream_output_file, streaming_data)
                                        break
                            else:
                                # Write skipped result
                                skip_result = {
                                    "question_id": item_id,
                                    "question": question,
                                    "ground_truth": expected_answer,
                                    "mistral_response": "",
                                    "timestamp": datetime.now().isoformat(),
                                    "round": 3,
                                    "status": "skipped",
                                    "reason": "Failed after 3 retry attempts"
                                }
                                streaming_data["sections"][section_name].append(skip_result)
                                self._write_streaming_results(stream_output_file, streaming_data)
                            
                        except Exception as e:
                            print(f"\n❌ Error in final retry Q{item_id}: {e}")
                            failed_q["final_error"] = str(e)
                            failed_q["status"] = "final_error"
                            continue
                    
                    print(f"\n✅ Round 3 Complete: {final_recovery}/{len(still_failed)} recovered")
                    answered_questions += final_recovery
            
            # Mark as complete
            streaming_data["status"] = "COMPLETED"
            streaming_data["summary"] = {
                "total_questions": total_questions,
                "answered_questions": answered_questions,
                "failed_after_retry": len([q for q in self.retry_results if q.get("status") in ["persistent_failure", "skipped_after_3_retries"]]),
                "completion_percentage": (answered_questions / total_questions * 100) if total_questions > 0 else 0,
                "retry_info": self.retry_results
            }
            self._write_streaming_results(stream_output_file, streaming_data)
            print(f"✅ Streaming results saved to {stream_output_file}")
            
            return answered_questions > 0
        except KeyboardInterrupt:
            print("\n⚠️  Benchmark interrupted by user")
            streaming_data["status"] = "INTERRUPTED"
            self._write_streaming_results(stream_output_file, streaming_data)
            return False
        except Exception as e:
            print(f"\n❌ Critical error in benchmark: {e}")
            streaming_data["status"] = "ERROR"
            streaming_data["error"] = str(e)
            self._write_streaming_results(stream_output_file, streaming_data)
            import traceback
            traceback.print_exc()
            return False

    def compare_responses(self) -> Dict[str, Any]:
        """Compare responses from all three sources: Ground Truth vs Llama 3 vs Mistral"""
        print("\n" + "="*80)
        print("📊 Comparing All Three Sources Against Ground Truth...")
        print("="*80)
        
        comparison_report = {}
        sections = self.extract_sections()
        
        for section in sections:
            section_name = section.get("name", "Unknown")
            print(f"\n📈 Section: {section_name}")
            print("-" * 60)
            
            # Evaluate Llama 3 results against ground truth
            llama3_evaluations = self._evaluate_llama3_section(section)
            
            # Get Mistral results for this section
            mistral_evaluations = self.mistral_results.get(section_name, [])
            
            section_comparison = {
                "total_questions": len(section.get("items", [])),
                "ground_truth_source": "PsychBench-benchmark-test.json",
                "llama3_source": "PsychBench-benchmark-test-results.json",
                "mistral_source": "Real-time Ollama (mistral)",
                "llama3_stats": self._calculate_evaluation_stats(llama3_evaluations),
                "mistral_stats": self._calculate_evaluation_stats(mistral_evaluations),
                "detailed_comparison": []
            }
            
            # Create detailed comparison for each question
            for idx, item in enumerate(section.get("items", [])):
                question = item.get("question", "")
                ground_truth = item.get("answer", "")
                item_id = item.get("id", 0)
                
                # Get evaluations from both LLMs
                llama3_eval = llama3_evaluations[idx] if idx < len(llama3_evaluations) else None
                mistral_eval = mistral_evaluations[idx] if idx < len(mistral_evaluations) else None
                
                comparison_item = {
                    "question_id": item_id,
                    "question": question,
                    "ground_truth_answer": ground_truth,
                    "llama3": {
                        "response": llama3_eval.get("response", "") if llama3_eval else "",
                        "similarity": llama3_eval.get("similarity", 0) if llama3_eval else 0,
                        "status": llama3_eval.get("status", "NO_DATA") if llama3_eval else "NO_DATA"
                    },
                    "mistral": {
                        "response": mistral_eval.get("response", "") if mistral_eval else "",
                        "similarity": mistral_eval.get("similarity", 0) if mistral_eval else 0,
                        "status": mistral_eval.get("status", "NO_DATA") if mistral_eval else "NO_DATA"
                    }
                }
                section_comparison["detailed_comparison"].append(comparison_item)
            
            # Print stats
            print(f"  Llama 3 Avg Similarity: {section_comparison['llama3_stats']['average_similarity']:.3f}")
            print(f"  Mistral Avg Similarity: {section_comparison['mistral_stats']['average_similarity']:.3f}")
            
            comparison_report[section_name] = section_comparison
        
        self.comparison_results = comparison_report
        return comparison_report


    def _evaluate_llama3_section(self, section: Dict) -> List[Dict]:
        """Evaluate Llama 3 responses from a section against ground truth"""
        evaluations = []
        section_name = section.get("name", "Unknown")
        
        # Find corresponding section in Llama 3 results
        llama3_section = None
        if self.llama3_results:
            llama3_sections = self.llama3_results.get("psychbench_medium_benchmark", {}).get("sections", [])
            for sec in llama3_sections:
                if sec.get("name") == section_name:
                    llama3_section = sec
                    break
        
        if not llama3_section:
            # Return empty evaluations if section not found
            return [{"response": "", "similarity": 0, "status": "NOT_FOUND"} for _ in section.get("items", [])]
        
        # Evaluate each question
        for idx, item in enumerate(section.get("items", [])):
            question = item.get("question", "")
            expected_answer = item.get("answer", "")
            
            # Get Llama 3 response
            llama3_items = llama3_section.get("items", [])
            llama3_response = ""
            
            if idx < len(llama3_items):
                llama3_item = llama3_items[idx]
                # Extract response text from Llama 3 result
                if isinstance(llama3_item.get("response"), dict):
                    llama3_response = llama3_item.get("response", {}).get("text", "")
                else:
                    llama3_response = str(llama3_item.get("response", ""))
            
            # Evaluate this response
            evaluation = self.evaluate_response(question, expected_answer, llama3_response)
            evaluations.append(evaluation)
        
        return evaluations

    def _calculate_evaluation_stats(self, evaluations: List[Dict]) -> Dict:
        """Calculate statistics from a list of evaluations"""
        if not evaluations:
            return {
                "total": 0,
                "average_similarity": 0,
                "status_distribution": {}
            }
        
        total = len(evaluations)
        similarities = []
        status_counts = {}
        
        for eval_item in evaluations:
            similarity = eval_item.get("similarity", 0)
            similarities.append(similarity)
            status = eval_item.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        return {
            "total": total,
            "average_similarity": round(avg_similarity, 3),
            "status_distribution": status_counts
        }

    def _get_section_stats(self, results: Dict, section_name: str, is_mistral: bool = False) -> Dict:
        """Extract statistics for a section"""
        if is_mistral:
            items = results.get("mistral", {}).get(section_name, [])
        else:
            sections = results.get("psychbench_medium_benchmark", {}).get("sections", [])
            items = []
            for sec in sections:
                if sec.get("name") == section_name:
                    items = sec.get("items", [])
                    break
        
        if not items:
            return {"total": 0, "average_similarity": 0, "status_distribution": {}}
        
        total = len(items)
        similarities = []
        status_counts = {}
        
        for item in items:
            if isinstance(item, dict):
                status = "UNKNOWN"  # Initialize status with default value
                if is_mistral:
                    similarities.append(item.get("similarity", 0))
                    status = item.get("status", "UNKNOWN")
                else:
                    response = item.get("response", {})
                    if isinstance(response, dict):
                        similarities.append(response.get("similarity", 0))
                    status = item.get("status", "UNKNOWN")
                
                status_counts[status] = status_counts.get(status, 0) + 1
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        return {
            "total": total,
            "average_similarity": round(avg_similarity, 3),
            "status_distribution": status_counts
        }

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive benchmark report with three-way comparison
        
        Args:
            output_file: Optional file to save report to
            
        Returns:
            The generated report as a string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = []
        report.append("="*80)
        report.append("PSYCHBENCH LLM COMPARISON REPORT")
        report.append("="*80)
        report.append(f"Generated: {timestamp}\n")
        
        report.append("EXECUTIVE SUMMARY - THREE-WAY COMPARISON")
        report.append("-"*80)
        report.append(f"Source 1 - Ground Truth: PsychBench-benchmark-test.json")
        report.append(f"Source 2 - Llama 3: PsychBench-benchmark-test-results.json")
        report.append(f"Source 3 - Mistral: Real-time query via Ollama (mistral)")
        report.append("")
        report.append("Comparison Methodology:")
        report.append("  - Llama 3 responses evaluated against Ground Truth answers")
        report.append("  - Mistral responses evaluated against Ground Truth answers")
        report.append("  - Similarity scores calculated using SequenceMatcher (0-1 scale)")
        report.append("")
        
        # Overall statistics
        overall_llama3_sim = self._calculate_overall_similarity_by_source("llama3")
        overall_mistral_sim = self._calculate_overall_similarity()
        
        total_questions = sum(comp.get('total_questions', 0) for comp in self.comparison_results.values())
        
        report.append(f"Total Questions Tested: {total_questions}")
        report.append(f"Llama 3 Overall Similarity Score: {overall_llama3_sim:.3f}")
        report.append(f"Mistral Overall Similarity Score: {overall_mistral_sim:.3f}")
        report.append("")
        
        # Section-by-section comparison
        report.append("\nDETAILED SECTION-BY-SECTION COMPARISON")
        report.append("="*80)
        
        for section_name, comparison in self.comparison_results.items():
            report.append(f"\n📋 Section: {section_name}")
            report.append("-"*80)
            
            llama3_stats = comparison.get("llama3_stats", {})
            mistral_stats = comparison.get("mistral_stats", {})
            
            report.append(f"Total Questions in Section: {comparison.get('total_questions', 0)}")
            report.append("")
            
            # Comparison metrics
            report.append("SIMILARITY SCORES (vs Ground Truth):")
            report.append(f"  Llama 3:  {llama3_stats.get('average_similarity', 0):.3f}")
            report.append(f"  Mistral: {mistral_stats.get('average_similarity', 0):.3f}")
            report.append("")
            
            # Status distribution
            report.append("Llama 3 Status Distribution:")
            for status, count in llama3_stats.get("status_distribution", {}).items():
                percentage = (count / comparison.get('total_questions', 1)) * 100
                report.append(f"  {status}: {count} ({percentage:.1f}%)")
            
            report.append("")
            report.append("Mistral Status Distribution:")
            for status, count in mistral_stats.get("status_distribution", {}).items():
                percentage = (count / comparison.get('total_questions', 1)) * 100
                report.append(f"  {status}: {count} ({percentage:.1f}%)")
            
            # Sample comparisons
            report.append("")
            report.append("SAMPLE RESPONSE COMPARISONS (first 2 questions):")
            for detail in comparison.get("detailed_comparison", [])[:2]:
                report.append(f"\n  Q{detail['question_id']}: {detail['question']}")
                report.append(f"  Ground Truth: {detail['ground_truth_answer'][:80]}...")
                
                llama3_info = detail.get("llama3", {})
                mistral_info = detail.get("mistral", {})
                
                report.append(f"\n  Llama 3:")
                report.append(f"    Similarity: {llama3_info.get('similarity', 0):.3f} | Status: {llama3_info.get('status', 'UNKNOWN')}")
                report.append(f"    Response: {llama3_info.get('response', 'N/A')[:80]}...")
                
                report.append(f"\n  Mistral:")
                report.append(f"    Similarity: {mistral_info.get('similarity', 0):.3f} | Status: {mistral_info.get('status', 'UNKNOWN')}")
                report.append(f"    Response: {mistral_info.get('response', 'N/A')[:80]}...")
        
        # Final metrics and recommendations
        report.append("\n" + "="*80)
        report.append("COMPARATIVE ANALYSIS & RECOMMENDATIONS")
        report.append("="*80)
        
        if overall_llama3_sim >= overall_mistral_sim:
            report.append(f"\n✓ Llama 3 OUTPERFORMS Mistral")
            report.append(f"  - Llama 3 similarity: {overall_llama3_sim:.3f}")
            report.append(f"  - Mistral similarity: {overall_mistral_sim:.3f}")
            report.append(f"  - Difference: +{(overall_llama3_sim - overall_mistral_sim):.3f}")
        else:
            report.append(f"\n✓ Mistral OUTPERFORMS Llama 3")
            report.append(f"  - Mistral similarity: {overall_mistral_sim:.3f}")
            report.append(f"  - Llama 3 similarity: {overall_llama3_sim:.3f}")
            report.append(f"  - Difference: +{(overall_mistral_sim - overall_llama3_sim):.3f}")
        
        # Quality assessment
        if overall_llama3_sim >= 0.7 or overall_mistral_sim >= 0.7:
            report.append("\n📊 Overall Assessment: STRONG - At least one model shows excellent psychiatric knowledge")
        elif overall_llama3_sim >= 0.5 or overall_mistral_sim >= 0.5:
            report.append("\n📊 Overall Assessment: GOOD - At least one model shows solid understanding")
        elif overall_llama3_sim >= 0.3 or overall_mistral_sim >= 0.3:
            report.append("\n📊 Overall Assessment: FAIR - Both models cover key concepts but need improvement")
        else:
            report.append("\n📊 Overall Assessment: POOR - Significant gaps in psychiatric knowledge for both models")
        
        report_text = "\n".join(report)
        
        # Save report if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(report_text)
                print(f"\n✅ Report saved to {output_file}")
            except Exception as e:
                print(f"⚠️  Could not save report: {e}")
        
        return report_text

    def _write_streaming_results(self, filepath: Path, data: Dict) -> bool:
        """
        Write streaming results to file after each question
        
        Args:
            filepath: Output file path
            data: Data to write
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not write streaming results: {e}")
            return False

    def _calculate_overall_similarity(self) -> float:
        """Calculate overall average similarity across all Mistral responses"""
        all_similarities = []
        for section_items in self.mistral_results.values():
            for item in section_items:
                similarity = item.get("similarity", 0)
                all_similarities.append(similarity)
        
        return sum(all_similarities) / len(all_similarities) if all_similarities else 0.0

    def _calculate_overall_similarity_by_source(self, source: str) -> float:
        """Calculate overall average similarity for a specific source"""
        all_similarities = []
        
        for section_name, comparison in self.comparison_results.items():
            if source == "llama3":
                for detail in comparison.get("detailed_comparison", []):
                    llama3_sim = detail.get("llama3", {}).get("similarity", 0)
                    all_similarities.append(llama3_sim)
            elif source == "mistral":
                for detail in comparison.get("detailed_comparison", []):
                    mistral_sim = detail.get("mistral", {}).get("similarity", 0)
                    all_similarities.append(mistral_sim)
        
        return sum(all_similarities) / len(all_similarities) if all_similarities else 0.0

    def save_results(self, output_file: Optional[str] = None, comparison_file: Optional[str] = None, 
                     comprehensive_file: Optional[str] = None) -> bool:
        """
        Save detailed results to JSON files with all three answers and metrics
        
        Args:
            output_file: Mistral results file path
            comparison_file: Comparison analysis file path
            comprehensive_file: Comprehensive benchmark file with all answers
            
        Returns:
            True if successful
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        
        if output_file is None:
            output_file = self.base_path / f"PsychBench-benchmark-mistral-results-{timestamp}.json"
        
        if comparison_file is None:
            comparison_file = self.base_path / f"PsychBench-benchmark-comparison-{timestamp}.json"
        
        if comprehensive_file is None:
            comprehensive_file = self.base_path / f"PsychBench-benchmark-comprehensive-{timestamp}.json"
        
        try:
            # Build comprehensive results with all three answers
            comprehensive_results = self._build_comprehensive_results()
            
            # Save comprehensive file with all three answers and metrics
            with open(comprehensive_file, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Comprehensive benchmark (all 3 answers + metrics) saved to {comprehensive_file}")
            
            # Save detailed Mistral results only
            mistral_data = {
                "timestamp": datetime.now().isoformat(),
                "benchmark_name": "PsychBench Mistral Results",
                "mistral_results": self.mistral_results,
                "metrics": {
                    "overall_similarity": self._calculate_overall_similarity(),
                    "total_questions": sum(len(items) for items in self.mistral_results.values())
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(mistral_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Mistral results saved to {output_file}")
            
            # Save comparison analysis
            comparison_data = {
                "timestamp": datetime.now().isoformat(),
                "benchmark_name": "PsychBench Three-Way Comparison Analysis",
                "description": "Detailed comparison metrics for Llama 3 and Mistral against ground truth",
                "comparison_analysis": self.comparison_results,
                "summary_metrics": {
                    "llama3_overall_similarity": self._calculate_overall_similarity_by_source("llama3"),
                    "mistral_overall_similarity": self._calculate_overall_similarity(),
                    "total_sections": len(self.comparison_results),
                    "total_questions": sum(comp.get('total_questions', 0) for comp in self.comparison_results.values())
                }
            }
            
            with open(comparison_file, 'w', encoding='utf-8') as f:
                json.dump(comparison_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Comparison analysis saved to {comparison_file}")
            
            return True
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return False

    def _build_comprehensive_results(self) -> Dict[str, Any]:
        """
        Build comprehensive results with all three answers and complete metrics
        
        Returns:
            Dictionary with structured three-way comparison
        """
        comprehensive = {
            "timestamp": datetime.now().isoformat(),
            "benchmark_name": "PsychBench Complete Three-Way Comparison",
            "description": "All 60 questions with: Question | Ground Truth Answer | Llama 3 Answer | Mistral Answer + Full Similarity Metrics",
            "sources": {
                "1_ground_truth": "PsychBench-benchmark-test.json",
                "2_llama3": "PsychBench-benchmark-test-results.json",
                "3_mistral": "Real-time Ollama (mistral)"
            },
            "metrics_summary": {
                "llama3_overall_similarity_to_ground_truth": self._calculate_overall_similarity_by_source("llama3"),
                "mistral_overall_similarity_to_ground_truth": self._calculate_overall_similarity(),
                "llama3_vs_mistral_average_difference": 0,
                "total_questions": 0,
                "completed_questions": 0
            },
            "sections": []
        }
        
        # Get sections from original benchmark
        sections = self.extract_sections()
        total_questions = 0
        completed_questions = 0
        all_llama3_scores = []
        all_mistral_scores = []
        
        for section in sections:
            section_name = section.get("name", "Unknown")
            
            # Get comparison data for this section
            section_comparison = self.comparison_results.get(section_name, {})
            detailed_comps = section_comparison.get("detailed_comparison", [])
            
            section_metrics = section_comparison.get("llama3_stats", {})
            mistral_metrics = section_comparison.get("mistral_stats", {})
            
            section_data = {
                "section_name": section_name,
                "section_metrics": {
                    "total_questions_in_section": len(section.get("items", [])),
                    "llama3_average_similarity_to_ground_truth": section_metrics.get("average_similarity", 0),
                    "mistral_average_similarity_to_ground_truth": mistral_metrics.get("average_similarity", 0),
                    "llama3_status_distribution": section_metrics.get("status_distribution", {}),
                    "mistral_status_distribution": mistral_metrics.get("status_distribution", {})
                },
                "questions": []
            }
            
            # Process each question in this section
            for detail_comp in detailed_comps:
                question_id = detail_comp.get("question_id", 0)
                question = detail_comp.get("question", "")
                ground_truth_answer = detail_comp.get("ground_truth_answer", "")
                
                llama3_data = detail_comp.get("llama3", {})
                mistral_data = detail_comp.get("mistral", {})
                
                llama3_response = llama3_data.get("response", "")
                mistral_response = mistral_data.get("response", "")
                
                llama3_sim = llama3_data.get("similarity", 0)
                mistral_sim = mistral_data.get("similarity", 0)
                
                # Calculate Llama 3 vs Mistral comparison
                llama3_vs_mistral_sim = self.calculate_similarity(llama3_response, mistral_response)
                
                total_questions += 1
                
                # Check if both have responses
                if llama3_response or mistral_response:
                    completed_questions += 1
                
                all_llama3_scores.append(llama3_sim)
                all_mistral_scores.append(mistral_sim)
                
                question_entry = {
                    "question_id": question_id,
                    "question": question,
                    "answers": {
                        "1_ground_truth": {
                            "answer": ground_truth_answer,
                            "source": "PsychBench-benchmark-test.json"
                        },
                        "2_llama3": {
                            "answer": llama3_response,
                            "source": "PsychBench-benchmark-test-results.json"
                        },
                        "3_mistral": {
                            "answer": mistral_response,
                            "source": "Real-time Ollama (mistral)"
                        }
                    },
                    "metrics": {
                        "llama3_vs_ground_truth": {
                            "similarity_score": round(llama3_sim, 3),
                            "interpretation": self._interpret_similarity(llama3_sim),
                            "status": llama3_data.get("status", "UNKNOWN")
                        },
                        "mistral_vs_ground_truth": {
                            "similarity_score": round(mistral_sim, 3),
                            "interpretation": self._interpret_similarity(mistral_sim),
                            "status": mistral_data.get("status", "UNKNOWN")
                        },
                        "llama3_vs_mistral": {
                            "similarity_score": round(llama3_vs_mistral_sim, 3),
                            "interpretation": self._interpret_similarity(llama3_vs_mistral_sim)
                        },
                        "rankings": {
                            "best_match_to_ground_truth": self._get_best_match(llama3_sim, mistral_sim),
                            "similarity_gap_from_ground_truth": {
                                "llama3_gap": round(1 - llama3_sim, 3),
                                "mistral_gap": round(1 - mistral_sim, 3)
                            }
                        }
                    }
                }
                
                section_data["questions"].append(question_entry)
            
            comprehensive["sections"].append(section_data)
        
        # Calculate average difference between Llama 3 and Mistral
        avg_llama3 = sum(all_llama3_scores) / len(all_llama3_scores) if all_llama3_scores else 0
        avg_mistral = sum(all_mistral_scores) / len(all_mistral_scores) if all_mistral_scores else 0
        
        # Update summary metrics
        comprehensive["metrics_summary"]["total_questions"] = total_questions
        comprehensive["metrics_summary"]["completed_questions"] = completed_questions
        comprehensive["metrics_summary"]["llama3_vs_mistral_average_difference"] = round(avg_llama3 - avg_mistral, 3)
        comprehensive["metrics_summary"]["average_scores"] = {
            "llama3_avg_vs_ground_truth": round(avg_llama3, 3),
            "mistral_avg_vs_ground_truth": round(avg_mistral, 3),
            "better_overall_model": "Llama 3" if avg_llama3 > avg_mistral else ("Mistral" if avg_mistral > avg_llama3 else "Tie")
        }
        
        return comprehensive

    def _get_best_match(self, llama3_sim: float, mistral_sim: float) -> str:
        """Determine which model has best match to ground truth"""
        if llama3_sim > mistral_sim:
            return f"Llama 3 (+{round(llama3_sim - mistral_sim, 3)})"
        elif mistral_sim > llama3_sim:
            return f"Mistral (+{round(mistral_sim - llama3_sim, 3)})"
        else:
            return "Tie"

    def _interpret_similarity(self, score: float) -> str:
        """Interpret similarity score"""
        if score >= 0.7:
            return "EXCELLENT - Strong match to ground truth"
        elif score >= 0.5:
            return "GOOD - Solid match to ground truth"
        elif score >= 0.3:
            return "PARTIAL - Some relevant content"
        elif score > 0:
            return "WEAK - Minimal relevant content"
        else:
            return "NO_MATCH - No response or completely different"

    def run_full_benchmark(self) -> bool:
        """Run complete benchmark workflow with error handling"""
        print("\n🔍 Starting Full Benchmark Comparison Workflow...")
        
        try:
            # Load original benchmark
            if not self.load_original_benchmark():
                return False
            
            # Load Llama 3 results
            if not self.load_llama3_results():
                print("⚠️  Continuing without Llama 3 results")
            
            # Run Mistral benchmark with streaming output
            if not self.run_mistral_benchmark():
                print("⚠️  Mistral benchmark returned no results")
            
            # Compare results
            self.compare_responses()
            
            # Generate and display report
            report = self.generate_report()
            print("\n" + report)
            
            # Save all results
            self.save_results()
            
            return True
        except KeyboardInterrupt:
            print("\n⚠️  Benchmark interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Benchmark error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    print("\n🧠 Psychiatric Benchmark LLM Comparison Tool")
    print("="*80)
    
    # Initialize benchmark comparison
    benchmark = BenchmarkComparison()
    
    # Run full benchmark
    success = benchmark.run_full_benchmark()
    
    if success:
        print("\n✅ Benchmark completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Benchmark failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
