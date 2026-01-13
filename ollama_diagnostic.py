#!/usr/bin/env python
"""Diagnostic script to test Mistral model connectivity and response"""

import requests
import json
import time

print("=" * 80)
print("OLLAMA & MISTRAL DIAGNOSTIC TEST")
print("=" * 80)

# Test 1: Check Ollama connectivity
print("\n1. Testing Ollama Server Connectivity...")
try:
    resp = requests.get('http://localhost:11434/api/tags', timeout=5)
    if resp.status_code == 200:
        models = resp.json().get('models', [])
        print(f"   ✓ Ollama server is running")
        print(f"   ✓ Available models: {len(models)}")
        for model in models:
            print(f"     - {model.get('name', 'Unknown')}")
    else:
        print(f"   ✗ Unexpected status code: {resp.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 2: Test Mistral with non-streaming request (faster)
print("\n2. Testing Mistral Model (non-streaming, 10s timeout)...")
try:
    start = time.time()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": "What is depression in one sentence?",
            "stream": False,
        },
        timeout=10  # Short timeout to see if it responds
    )
    elapsed = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        answer = result.get('response', '')[:100]
        print(f"   ✓ Mistral responded in {elapsed:.1f}s")
        print(f"   ✓ Response preview: {answer}...")
    else:
        print(f"   ✗ Status code: {response.status_code}")
except requests.exceptions.Timeout:
    print(f"   ✗ Timeout after 10 seconds - Mistral is too slow or not responding")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

# Test 3: Test with streaming request
print("\n3. Testing Mistral Model (streaming, 30s timeout)...")
try:
    start = time.time()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": "What is depression?",
            "stream": True,
            "temperature": 0.1
        },
        timeout=30,
        stream=True
    )
    
    if response.status_code == 200:
        full_response = ""
        chunk_count = 0
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    chunk = json.loads(line)
                    full_response += chunk.get("response", "")
                    chunk_count += 1
                    if chunk.get("done", False):
                        break
                except:
                    continue
        
        elapsed = time.time() - start
        print(f"   ✓ Streaming succeeded in {elapsed:.1f}s")
        print(f"   ✓ Received {chunk_count} chunks")
        print(f"   ✓ Total response: {len(full_response)} characters")
        print(f"   ✓ Response preview: {full_response[:100]}...")
    else:
        print(f"   ✗ Status code: {response.status_code}")
except requests.exceptions.Timeout:
    print(f"   ✗ Timeout after 30 seconds")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
