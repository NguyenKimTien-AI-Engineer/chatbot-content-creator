#!/usr/bin/env python3
"""
Test Streaming API
Usage: python test_streaming.py
"""

import requests
import json
import time
import sys
from typing import Optional

# ANSI Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def test_streaming_api(
    url: str,
    payload: dict,
    timeout: int = 30
) -> tuple[bool, Optional[str]]:
    """
    Test streaming API endpoint
    
    Returns:
        tuple: (success, error_message)
    """
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored("🚀 Testing Streaming API", Colors.BOLD)
    print_colored(f"{'='*60}", Colors.CYAN)
    
    print_colored(f"\n📍 URL: {url}", Colors.BLUE)
    print_colored(f"📦 Payload:", Colors.BLUE)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    
    print_colored(f"\n📋 Headers:", Colors.BLUE)
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    print_colored(f"\n⏳ Connecting...", Colors.YELLOW)
    
    try:
        start_time = time.time()
        
        with requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=timeout
        ) as response:
            
            # Check status code
            elapsed = time.time() - start_time
            print_colored(f"\n✅ Connected! (took {elapsed:.2f}s)", Colors.GREEN)
            print_colored(f"📊 Status Code: {response.status_code}", Colors.GREEN)
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print_colored(f"\n❌ Error: {error_msg}", Colors.RED)
                return False, error_msg
            
            # Check response headers
            print_colored(f"\n📋 Response Headers:", Colors.BLUE)
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
            # Read streaming response
            print_colored(f"\n📡 Streaming Response:", Colors.MAGENTA)
            print_colored(f"{'-'*60}", Colors.CYAN)
            
            chunk_count = 0
            total_content = ""
            line_buffer = ""
            
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    chunk_count += 1
                    line_buffer += chunk
                    
                    # Process complete lines
                    while '\n' in line_buffer:
                        line, line_buffer = line_buffer.split('\n', 1)
                        
                        if line.strip():
                            # Print chunk with color
                            print_colored(f"📦 Chunk {chunk_count}: {line}", Colors.GREEN)
                            
                            # Try to parse JSON content
                            if line.startswith('data: '):
                                data_str = line[6:].strip()
                                if data_str and data_str != '[DONE]':
                                    try:
                                        data = json.loads(data_str)
                                        if 'content' in data:
                                            content = data['content']
                                            total_content += content
                                            print_colored(f"  → Content: {content}", Colors.CYAN)
                                    except json.JSONDecodeError:
                                        pass
            
            # Process remaining buffer
            if line_buffer.strip():
                print_colored(f"📦 Chunk {chunk_count + 1}: {line_buffer}", Colors.GREEN)
            
            elapsed_total = time.time() - start_time
            
            print_colored(f"\n{'-'*60}", Colors.CYAN)
            print_colored(f"✅ Streaming completed!", Colors.GREEN)
            print_colored(f"📊 Statistics:", Colors.BLUE)
            print(f"  - Total chunks: {chunk_count}")
            print(f"  - Total time: {elapsed_total:.2f}s")
            print(f"  - Content length: {len(total_content)} chars")
            
            if total_content:
                print_colored(f"\n📝 Full Response:", Colors.MAGENTA)
                print_colored(f"{'-'*60}", Colors.CYAN)
                print(total_content)
                print_colored(f"{'-'*60}", Colors.CYAN)
                
                return True, None
            else:
                print_colored(f"\n⚠️  Warning: No content received!", Colors.YELLOW)
                return False, "No content in response"
                
    except requests.exceptions.Timeout:
        error_msg = f"Request timeout after {timeout}s"
        print_colored(f"\n❌ {error_msg}", Colors.RED)
        return False, error_msg
        
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error: {str(e)}"
        print_colored(f"\n❌ {error_msg}", Colors.RED)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print_colored(f"\n❌ {error_msg}", Colors.RED)
        return False, error_msg

def main():
    """Main function"""
    
    # Configuration
    configs = [
        {
            "name": "VPS (localhost)",
            "url": "http://127.0.0.1:1979/api/v1/chatbot-custom-prompt-stream",
            "payload": {
                "user_id": "default_user",
                "query": "bạn biết gì về kát",
                "collections": [],
                "session_id": "demo",
                "history_id": "demo",
                "system_instruction_user": "",
                "include_products": True
            }
        },
        {
            "name": "VPS (public IP)",
            "url": "http://144.91.113.233:1979/api/v1/chatbot-custom-prompt-stream",
            "payload": {
                "user_id": "default_user",
                "query": "xin chào",
                "collections": [],
                "session_id": "demo",
                "history_id": "demo",
                "system_instruction_user": "",
                "include_products": True
            }
        }
    ]
    
    # Test each configuration
    results = []
    
    for i, config in enumerate(configs, 1):
        print_colored(f"\n{'='*60}", Colors.MAGENTA)
        print_colored(f"Test {i}/{len(configs)}: {config['name']}", Colors.BOLD)
        print_colored(f"{'='*60}", Colors.MAGENTA)
        
        success, error = test_streaming_api(
            url=config['url'],
            payload=config['payload'],
            timeout=30
        )
        
        results.append({
            'name': config['name'],
            'success': success,
            'error': error
        })
        
        # Wait between tests
        if i < len(configs):
            print_colored(f"\n⏳ Waiting 2s before next test...", Colors.YELLOW)
            time.sleep(2)
    
    # Print summary
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored("📊 Test Summary", Colors.BOLD)
    print_colored(f"{'='*60}", Colors.CYAN)
    
    for result in results:
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        color = Colors.GREEN if result['success'] else Colors.RED
        print_colored(f"\n{status} - {result['name']}", color)
        if result['error']:
            print_colored(f"  Error: {result['error']}", Colors.RED)
    
    # Exit code
    all_passed = all(r['success'] for r in results)
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored(f"\n\n⚠️  Test interrupted by user", Colors.YELLOW)
        sys.exit(1)