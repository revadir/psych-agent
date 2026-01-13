#!/usr/bin/env python3
"""Run PsychBench questions against the local psych-agent and save responses.

Usage:
  python run_benchmark.py [input_json] [output_json]

Defaults:
  input_json: backend/PsychBench-benchmark-test.json
  output_json: backend/PsychBench-benchmark-test-results.json

The script logs in as admin@example.com (allowlist) to obtain a JWT, creates a chat session,
and posts each question to `/api/chat/sessions/{session_id}/messages` (non-streaming) and
saves agent responses.
"""
import sys
import time
import json
from datetime import datetime
from pathlib import Path
import requests
from requests.exceptions import ReadTimeout, RequestException
import socket
import signal

BASE_URL = "http://127.0.0.1:8001/api"
ADMIN_EMAIL = "admin@example.com"


def load_input(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_output(data, path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def login(email: str, timeout=10):
    url = f"{BASE_URL}/auth/login"
    print(f"DEBUG: POST {url} with email={email}")
    r = requests.post(url, json={"email": email}, timeout=timeout)
    r.raise_for_status()
    return r.json()["access_token"]


def create_session(token: str, title: str = None, timeout=10):
    url = f"{BASE_URL}/chat/sessions"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": title} if title is not None else {}
    print(f"DEBUG: POST {url} payload={payload} headers=Authorization:Bearer <token>")
    r = requests.post(url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()["id"]


def ask_question_streaming(token: str, session_id: int, question: str, timeout=300):
    """Use the streaming endpoint and collect SSE events until response_complete."""
    url = f"{BASE_URL}/chat/sessions/{session_id}/messages/stream"
    headers = {"Authorization": f"Bearer {token}", "Accept": "text/event-stream"}
    payload = {"content": question}

    # Use POST with stream=True to receive SSE
    print(f"DEBUG: POST stream {url}")
    full_response = ""
    citations = None
    disclaimer = None
    start_time = time.time()
    max_wait = 180  # Maximum wait time for a response (increased for agent processing)
    
    try:
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=timeout) as r:
            try:
                r.raise_for_status()
            except Exception as e:
                print(f"HTTP error: {e}")
                return {"agent_response": {"response": f"HTTP ERROR: {str(e)}", "citations": None, "disclaimer": None}}

            # Iterate over lines and parse SSE 'data: ' lines
            try:
                for raw_line in r.iter_lines(decode_unicode=True):
                    # Check for timeout
                    elapsed = time.time() - start_time
                    if elapsed > max_wait:
                        print(f"Streaming timeout after {elapsed:.1f}s. Using partial response.")
                        break
                    
                    if raw_line is None:
                        continue
                    line = raw_line.strip()
                    if not line:
                        continue
                    if line.startswith("data:"):
                        payload_text = line[len("data:"):].strip()
                        try:
                            obj = json.loads(payload_text)
                        except Exception:
                            # ignore malformed event
                            continue

                        etype = obj.get("type")
                        data = obj.get("data")
                        if etype == "response_chunk":
                            chunk = data.get("chunk", "")
                            full_response += (chunk + " ")
                            print(f"  [chunk] {chunk[:50]}...")
                        elif etype == "response_complete":
                            # data contains 'full_response' and 'citations'
                            full_response = data.get("full_response", full_response)
                            citations = data.get("citations")
                            print("  [complete]")
                            break
                        elif etype == "citations":
                            citations = data
                            print(f"  [citations]")
                        elif etype == "error":
                            # stop on error
                            full_response = data.get("message", full_response)
                            print(f"  [error] {full_response[:50]}...")
                            break
            except (socket.timeout, socket.error, ConnectionError, OSError) as e:
                print(f"Socket error: {type(e).__name__}. Partial response: {full_response[:100]}...")
            except Exception as se:
                print(f"Stream error: {type(se).__name__}: {se}")
                
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        print(f"Request error: {type(e).__name__}")
        return {"agent_response": {"response": f"CONNECTION ERROR", "citations": None, "disclaimer": None}}
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return {"agent_response": {"response": f"ERROR: {str(e)}", "citations": None, "disclaimer": None}}
        
    return {"agent_response": {"response": full_response.strip(), "citations": citations, "disclaimer": disclaimer}}


def ask_question(token: str, session_id: int, question: str, timeout=30, retries=1):
    """Try streaming endpoint with robust error handling.

    Returns the same structure as the non-streaming endpoint (dict).
    """
    print(f'Directly trying the streaming endpoint...')
    try:
        return ask_question_streaming(token, session_id, question, timeout=300)
    except KeyboardInterrupt:
        # Re-raise KeyboardInterrupt to allow user to stop
        raise
    except Exception as e:
        print(f"Error in streaming endpoint: {type(e).__name__}: {e}")
        # Return error response instead of crashing
        return {"agent_response": {"response": f"ERROR: {str(e)}", "citations": None, "disclaimer": None}}


def run(input_path: Path, output_path: Path, limit: int = None):
    print(f"Loading questions from {input_path}")
    data = load_input(input_path)

    print(f"Logging in as {ADMIN_EMAIL}")
    token = login(ADMIN_EMAIL)
    print("Login OK")

    title = f"PsychBench run {datetime.utcnow().isoformat()}"
    print(f"Creating chat session: {title}")
    session_id = create_session(token, title)
    print(f"Session created: {session_id}")

    out = {"psychbench_medium_benchmark": {"sections": []}}

    try:
        for section in data.get("psychbench_medium_benchmark", {}).get("sections", []):
            section_out = {"name": section.get("name"), "items": []}
            for item in section.get("items", []):
                if limit is not None:
                    if isinstance(limit, int) and limit <= 0:
                        break
                qid = item.get("id")
                question = item.get("question")
                print(f"Asking ({qid}): {question}")

                # Ask with error handling
                try:
                    resp = ask_question(token, session_id, question)
                    agent_resp = resp.get("agent_response") or {}
                    response_text = agent_resp.get("response") or agent_resp.get("text") or ""
                    citations = agent_resp.get("citations")
                    disclaimer = agent_resp.get("disclaimer")
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"Error asking question {qid}: {type(e).__name__}: {e}")
                    response_text = f"ERROR: {str(e)}"
                    citations = None
                    disclaimer = None

                item_out = dict(item)  # copy original fields
                item_out["response"] = {
                    "text": response_text,
                    "citations": citations,
                    "disclaimer": disclaimer,
                }
                section_out["items"].append(item_out)

                # polite pause to avoid overwhelming the agent
                time.sleep(0.5)

            out["psychbench_medium_benchmark"]["sections"].append(section_out)
            if limit is not None:
                # decrement limit by number of items added in this section
                added = len(section_out["items"])
                if isinstance(limit, int):
                    limit -= added
                if limit is not None and isinstance(limit, int) and limit <= 0:
                    break
    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving partial results...")
    except Exception as e:
        print(f"\nError during benchmark: {type(e).__name__}: {e}")
    finally:
        print(f"Saving results to {output_path}")
        save_output(out, output_path)
        print("Done")


def main():
    # optional third arg: limit number of items to process
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "PsychBench-benchmark-test.json"
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / "PsychBench-benchmark-test-results.json"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    run(input_path, output_path, limit=limit)


if __name__ == "__main__":
    main()
