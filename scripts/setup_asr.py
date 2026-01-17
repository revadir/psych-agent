#!/usr/bin/env python3
"""
Setup script for ASR integration with AssemblyAI
"""

import os
import sys
from pathlib import Path

def main():
    print("🎤 Setting up ASR Integration with AssemblyAI")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path("backend/.env")
    
    print("\n1. AssemblyAI API Key Setup")
    print("-" * 30)
    print("To use ASR features, you need an AssemblyAI API key.")
    print("📝 Steps to get your free API key:")
    print("   1. Go to https://www.assemblyai.com/")
    print("   2. Sign up for a free account")
    print("   3. Get $50 in free credits (~3,700 minutes)")
    print("   4. Copy your API key from the dashboard")
    
    api_key = input("\n🔑 Enter your AssemblyAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Read existing .env or create new one
        env_content = ""
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # Add or update ASSEMBLYAI_API_KEY
        if "ASSEMBLYAI_API_KEY" in env_content:
            # Replace existing key
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('ASSEMBLYAI_API_KEY'):
                    lines[i] = f'ASSEMBLYAI_API_KEY={api_key}'
                    break
            env_content = '\n'.join(lines)
        else:
            # Add new key
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f'ASSEMBLYAI_API_KEY={api_key}\n'
        
        # Write back to .env
        env_file.parent.mkdir(exist_ok=True)
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ API key saved to {env_file}")
    else:
        print("⏭️  Skipped API key setup. You can add it later to backend/.env")
    
    print("\n2. Cost Information")
    print("-" * 20)
    print("💰 AssemblyAI Pricing:")
    print("   • Free tier: $50 credits (~3,700 minutes)")
    print("   • After free tier: $0.0025/minute ($0.15/hour)")
    print("   • Medical vocabulary support included")
    print("   • Speaker diarization included")
    
    print("\n3. Features Enabled")
    print("-" * 18)
    print("🎯 ASR Features:")
    print("   • Real-time audio recording")
    print("   • File upload transcription")
    print("   • Medical vocabulary optimization")
    print("   • Clinical report generation")
    print("   • Structured diagnostic analysis")
    
    print("\n4. Usage Instructions")
    print("-" * 20)
    print("🚀 To use ASR features:")
    print("   1. Start the backend: cd backend && python -m app.main")
    print("   2. Start the frontend: cd frontend && npm run dev")
    print("   3. Navigate to Clinical Recording tab")
    print("   4. Record audio or upload files")
    print("   5. Generate clinical reports from transcripts")
    
    if not api_key:
        print("\n⚠️  Note: ASR features will not work without an API key")
        print("   Add ASSEMBLYAI_API_KEY=your_key_here to backend/.env")
    
    print("\n✅ ASR setup complete!")
    print("📚 For more info: https://docs.assemblyai.com/")

if __name__ == "__main__":
    main()
