#!/usr/bin/env python3
"""
Ollama Setup Helper
Helps verify and setup Ollama for benchmark testing
"""

import subprocess
import sys
import requests
import time
from pathlib import Path

class OllamaSetupHelper:
    """Helper for Ollama setup and verification"""
    
    OLLAMA_API_URL = "http://localhost:11434"
    MISTRAL_MODEL = "mistral"
    
    @staticmethod
    def check_ollama_installed():
        """Check if Ollama is installed"""
        print("🔍 Checking if Ollama is installed...")
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ Ollama installed: {result.stdout.strip()}")
                return True
            else:
                print("❌ Ollama found but version check failed")
                return False
        except FileNotFoundError:
            print("❌ Ollama not found in PATH")
            print("   Install from: https://ollama.ai")
            return False
        except Exception as e:
            print(f"❌ Error checking Ollama: {e}")
            return False
    
    @staticmethod
    def check_ollama_running():
        """Check if Ollama server is running"""
        print("\n🔍 Checking if Ollama server is running...")
        try:
            response = requests.get(
                f"{OllamaSetupHelper.OLLAMA_API_URL}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                print("✅ Ollama server is running")
                return True
            else:
                print(f"❌ Ollama server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama server")
            print("   Start Ollama with: ollama serve")
            return False
        except requests.exceptions.Timeout:
            print("❌ Ollama server not responding (timeout)")
            return False
        except Exception as e:
            print(f"❌ Error checking server: {e}")
            return False
    
    @staticmethod
    def list_available_models():
        """List models available in Ollama"""
        print("\n🔍 Checking available models...")
        try:
            response = requests.get(
                f"{OllamaSetupHelper.OLLAMA_API_URL}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                if models:
                    print(f"✅ Found {len(models)} model(s):")
                    for model in models:
                        name = model.get("name", "Unknown")
                        size = model.get("size", 0)
                        size_gb = size / (1024**3)
                        print(f"   • {name} ({size_gb:.2f} GB)")
                    return models
                else:
                    print("⚠️  No models installed")
                    return []
            else:
                print(f"❌ Failed to list models (status {response.status_code})")
                return []
        except Exception as e:
            print(f"❌ Error listing models: {e}")
            return []
    
    @staticmethod
    def check_mistral_model():
        """Check if Mistral model is available"""
        print(f"\n🔍 Checking for {OllamaSetupHelper.MISTRAL_MODEL} model...")
        try:
            models = OllamaSetupHelper.list_available_models()
            model_names = [m.get("name", "") for m in models]
            
            for model_name in model_names:
                if "mistral" in model_name.lower():
                    print(f"✅ Mistral model found: {model_name}")
                    return True
            
            print(f"❌ Mistral model not found")
            print(f"   Install with: ollama pull mistral")
            return False
        except Exception as e:
            print(f"❌ Error checking for Mistral: {e}")
            return False
    
    @staticmethod
    def test_mistral_query():
        """Test a simple query to Mistral"""
        print("\n🔍 Testing Mistral query...")
        try:
            test_prompt = "What is DSM-5? Answer in one sentence."
            
            response = requests.post(
                f"{OllamaSetupHelper.OLLAMA_API_URL}/api/generate",
                json={
                    "model": OllamaSetupHelper.MISTRAL_MODEL,
                    "prompt": test_prompt,
                    "stream": False,
                    "temperature": 0.1
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()[:100]
                print(f"✅ Query successful!")
                print(f"   Test response: {response_text}...")
                return True
            else:
                print(f"❌ Query failed (status {response.status_code})")
                return False
        except requests.exceptions.Timeout:
            print("❌ Query timeout (Ollama may be slow or model downloading)")
            print("   Please wait for model download to complete")
            return False
        except Exception as e:
            print(f"❌ Query error: {e}")
            return False
    
    @staticmethod
    def run_full_check():
        """Run complete setup verification"""
        print("="*70)
        print("OLLAMA SETUP VERIFICATION")
        print("="*70)
        
        checks = []
        
        # Check 1: Ollama installed
        if OllamaSetupHelper.check_ollama_installed():
            checks.append(True)
        else:
            checks.append(False)
            print("\n❌ Please install Ollama first: https://ollama.ai")
            return False
        
        # Check 2: Ollama running
        if OllamaSetupHelper.check_ollama_running():
            checks.append(True)
        else:
            checks.append(False)
            print("\n⚠️  Start Ollama server to continue:")
            print("   ollama serve")
            return False
        
        # Check 3: Models available
        models = OllamaSetupHelper.list_available_models()
        if models:
            checks.append(True)
        else:
            checks.append(False)
            print("\n⚠️  No models installed. Pull a model:")
            print("   ollama pull mistral")
        
        # Check 4: Mistral available
        if OllamaSetupHelper.check_mistral_model():
            checks.append(True)
        else:
            checks.append(False)
            print("\n⚠️  Installing Mistral model...")
            print("   This may take a few minutes...")
            try:
                subprocess.run(["ollama", "pull", "mistral"], check=True)
                print("✅ Mistral installed!")
                checks.append(True)
            except Exception as e:
                print(f"❌ Failed to install Mistral: {e}")
                checks.append(False)
                return False
        
        # Check 5: Test query
        if OllamaSetupHelper.test_mistral_query():
            checks.append(True)
        else:
            checks.append(False)
            print("\n⚠️  Test query failed - Mistral may need warmup")
        
        # Summary
        print("\n" + "="*70)
        passed = sum(checks)
        total = len(checks)
        print(f"VERIFICATION SUMMARY: {passed}/{total} checks passed")
        print("="*70)
        
        if passed >= 4:
            print("\n✅ Setup looks good! Ready to run benchmarks!")
            print("   python compare_llm_benchmarks.py")
            return True
        elif passed >= 3:
            print("\n⚠️  Minor issues detected, but you can try benchmarking")
            return True
        else:
            print("\n❌ Setup issues detected. Please resolve them and retry.")
            return False

def main():
    """Main entry point"""
    try:
        success = OllamaSetupHelper.run_full_check()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Verification interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
