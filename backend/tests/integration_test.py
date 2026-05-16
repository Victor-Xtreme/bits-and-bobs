
#!/usr/bin/env python3
"""
RepoSense Integration Test Script

This script performs end-to-end testing of the RepoSense API by:
1. Sending a POST request to analyze a local codebase
2. Polling for job status at regular intervals
3. Displaying progress information
4. Handling completion, errors, and edge cases
5. Extracting and displaying final results

Usage:
    python integration_test.py <local_path>
    
Example:
    python integration_test.py /path/to/your/codebase
"""

import sys
import time
import json
import argparse
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

try:
    import requests
    from requests.exceptions import (
        RequestException,
        Timeout,
        ConnectionError,
        HTTPError
    )
except ImportError:
    print("Error: 'requests' library not found. Install it with: pip install requests")
    sys.exit(1)


# Configuration
API_BASE_URL = "http://localhost:8000"
POLL_INTERVAL_SECONDS = 3
REQUEST_TIMEOUT_SECONDS = 30
MAX_POLL_ATTEMPTS = 200  # 10 minutes max (200 * 3 seconds)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(message: str, color: str = Colors.ENDC) -> None:
    """Print colored message to console"""
    print(f"{color}{message}{Colors.ENDC}")


def print_header(message: str) -> None:
    """Print a formatted header"""
    print_colored(f"\n{'=' * 70}", Colors.HEADER)
    print_colored(f"  {message}", Colors.HEADER + Colors.BOLD)
    print_colored(f"{'=' * 70}\n", Colors.HEADER)


def print_progress_step(step: Dict[str, Any]) -> None:
    """Print a single progress step with formatting"""
    name = step.get('name', 'Unknown')
    status = step.get('status', 'pending')
    
    # Status icon and color
    if status == 'done':
        icon = '✓'
        color = Colors.OKGREEN
    elif status == 'active':
        icon = '⟳'
        color = Colors.OKCYAN
    else:  # pending
        icon = '○'
        color = Colors.WARNING
    
    status_str = f"{color}{icon} {name} [{status}]{Colors.ENDC}"
    
    # Add file processing info if available
    files_processed = step.get('files_processed')
    files_total = step.get('files_total')
    current_file = step.get('current_file')
    
    if files_processed is not None and files_total is not None:
        status_str += f" - {files_processed}/{files_total} files"
    
    if current_file:
        status_str += f" (current: {current_file})"
    
    print(f"  {status_str}")


def send_analyze_request(local_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Send POST request to /analyze endpoint.
    
    Args:
        local_path: Path to the local codebase to analyze
        
    Returns:
        Tuple of (job_id, error_message)
        job_id is None if request failed
    """
    print_header("STEP 1: Initiating Analysis")
    print_colored(f"Local path: {local_path}", Colors.OKBLUE)
    print_colored(f"API endpoint: {API_BASE_URL}/analyze", Colors.OKBLUE)
    
    try:
        payload = {"local_path": local_path}
        print_colored(f"\nSending POST request...", Colors.OKCYAN)
        
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        job_id = data.get('job_id')
        
        if not job_id:
            return None, "Response missing 'job_id' field"
        
        print_colored(f"✓ Analysis started successfully!", Colors.OKGREEN)
        print_colored(f"Job ID: {job_id}", Colors.OKGREEN + Colors.BOLD)
        
        # Display initial progress
        progress = data.get('progress', [])
        if progress:
            print_colored("\nInitial progress:", Colors.OKBLUE)
            for step in progress:
                print_progress_step(step)
        
        return job_id, None
        
    except Timeout:
        error_msg = f"Request timed out after {REQUEST_TIMEOUT_SECONDS} seconds"
        print_colored(f"✗ {error_msg}", Colors.FAIL)
        return None, error_msg
        
    except ConnectionError as e:
        error_msg = f"Connection failed: {str(e)}"
        print_colored(f"✗ {error_msg}", Colors.FAIL)
        print_colored("  Is the API server running at http://localhost:8000?", Colors.WARNING)
        return None, error_msg
        
    except HTTPError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        print_colored(f"✗ {error_msg}", Colors.FAIL)
        return None, error_msg
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON response: {str(e)}"
        print_colored(f"✗ {error_msg}", Colors.FAIL)
        return None, error_msg
        
    except RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        print_colored(f"✗ {error_msg}", Colors.FAIL)
        return None, error_msg


def poll_job_status(job_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Poll job status until completion or failure.
    
    Args:
        job_id: The job ID to poll
        
    Returns:
        Tuple of (final_response, error_message)
        final_response is None if polling failed
    """
    print_header("STEP 2: Polling for Results")
    print_colored(f"Job ID: {job_id}", Colors.OKBLUE)
    print_colored(f"Poll interval: {POLL_INTERVAL_SECONDS} seconds", Colors.OKBLUE)
    print_colored(f"Endpoint: {API_BASE_URL}/jobs/{job_id}\n", Colors.OKBLUE)
    
    attempt = 0
    last_progress_hash = None
    
    while attempt < MAX_POLL_ATTEMPTS:
        attempt += 1
        
        try:
            # Send GET request
            response = requests.get(
                f"{API_BASE_URL}/jobs/{job_id}",
                timeout=REQUEST_TIMEOUT_SECONDS
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Extract key fields
            response_type = data.get('type')
            progress = data.get('progress', [])
            payload = data.get('payload')
            
            # Create a hash of progress to detect changes
            progress_hash = json.dumps(progress, sort_keys=True)
            
            # Only print progress if it changed
            if progress_hash != last_progress_hash:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print_colored(f"\n[{timestamp}] Poll #{attempt} - Status Update:", Colors.OKCYAN)
                
                for step in progress:
                    print_progress_step(step)
                
                last_progress_hash = progress_hash
            else:
                # Just print a dot to show we're still polling
                print(".", end="", flush=True)
            
            # Check if job is complete
            if response_type == 'result':
                print_colored(f"\n\n✓ Job completed successfully!", Colors.OKGREEN + Colors.BOLD)
                return data, None
            
            # Check if job failed
            elif response_type == 'error':
                print_colored(f"\n\n✗ Job failed!", Colors.FAIL + Colors.BOLD)
                return data, None
            
            # Job still running, wait before next poll
            time.sleep(POLL_INTERVAL_SECONDS)
            
        except Timeout:
            error_msg = f"Poll request timed out after {REQUEST_TIMEOUT_SECONDS} seconds"
            print_colored(f"\n✗ {error_msg}", Colors.FAIL)
            return None, error_msg
            
        except ConnectionError as e:
            error_msg = f"Connection failed during polling: {str(e)}"
            print_colored(f"\n✗ {error_msg}", Colors.FAIL)
            return None, error_msg
            
        except HTTPError as e:
            if e.response.status_code == 404:
                error_msg = f"Job not found (404). It may have been cleaned up."
                print_colored(f"\n✗ {error_msg}", Colors.FAIL)
                return None, error_msg
            else:
                error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
                print_colored(f"\n✗ {error_msg}", Colors.FAIL)
                return None, error_msg
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response during polling: {str(e)}"
            print_colored(f"\n✗ {error_msg}", Colors.FAIL)
            return None, error_msg
            
        except RequestException as e:
            error_msg = f"Request failed during polling: {str(e)}"
            print_colored(f"\n✗ {error_msg}", Colors.FAIL)
            return None, error_msg
    
    # Max attempts reached
    error_msg = f"Maximum poll attempts ({MAX_POLL_ATTEMPTS}) reached. Job may still be running."
    print_colored(f"\n✗ {error_msg}", Colors.FAIL)
    return None, error_msg


def display_results(response: Dict[str, Any]) -> None:
    """
    Display the final results or error from the response.
    
    Args:
        response: The final API response
    """
    print_header("STEP 3: Final Results")
    
    response_type = response.get('type')
    payload = response.get('payload')
    
    if not payload:
        print_colored("✗ No payload in response", Colors.FAIL)
        return
    
    if response_type == 'result':
        # Success case - extract and display score and grade
        try:
            score_data = payload.get('score', {})
            
            if not score_data:
                print_colored("✗ No score data in result", Colors.FAIL)
                return
            
            # Extract key metrics
            score = score_data.get('score')
            grade = score_data.get('grade')
            breakdown = score_data.get('breakdown', {})
            summary = score_data.get('summary', '')
            top_priorities = score_data.get('top_priorities', [])
            
            # Display overall score
            print_colored("HEALTH SCORE", Colors.BOLD + Colors.OKGREEN)
            print_colored(f"  Score: {score}/100", Colors.OKGREEN)
            print_colored(f"  Grade: {grade}", Colors.OKGREEN)
            
            # Display breakdown
            if breakdown:
                print_colored("\nSCORE BREAKDOWN", Colors.BOLD + Colors.OKBLUE)
                print_colored(f"  Quality:        {breakdown.get('quality', 'N/A')}/25", Colors.OKBLUE)
                print_colored(f"  Security:       {breakdown.get('security', 'N/A')}/25", Colors.OKBLUE)
                print_colored(f"  Documentation:  {breakdown.get('documentation', 'N/A')}/25", Colors.OKBLUE)
                print_colored(f"  Architecture:   {breakdown.get('architecture', 'N/A')}/25", Colors.OKBLUE)
            
            # Display summary
            if summary:
                print_colored("\nSUMMARY", Colors.BOLD + Colors.OKCYAN)
                print_colored(f"  {summary}", Colors.OKCYAN)
            
            # Display top priorities
            if top_priorities:
                print_colored("\nTOP PRIORITIES", Colors.BOLD + Colors.WARNING)
                for i, priority in enumerate(top_priorities, 1):
                    print_colored(f"  {i}. {priority}", Colors.WARNING)
            
            # Display additional analysis sections
            print_colored("\nADDITIONAL ANALYSIS AVAILABLE", Colors.BOLD + Colors.OKBLUE)
            
            if payload.get('architecture'):
                arch = payload['architecture']
                node_count = len(arch.get('nodes', []))
                edge_count = len(arch.get('edges', []))
                print_colored(f"  • Architecture Graph: {node_count} nodes, {edge_count} edges", Colors.OKBLUE)
            
            if payload.get('review'):
                findings = payload['review'].get('findings', [])
                print_colored(f"  • Code Review: {len(findings)} findings", Colors.OKBLUE)
            
            if payload.get('docs'):
                docs = payload['docs']
                doc_count = len(docs.get('docs', []))
                test_count = len(docs.get('tests', []))
                print_colored(f"  • Documentation: {doc_count} entries, {test_count} test entries", Colors.OKBLUE)
            
            if payload.get('security'):
                security = payload['security']
                security_issues = len(security.get('security', []))
                modernization = len(security.get('modernization', []))
                print_colored(f"  • Security: {security_issues} issues, {modernization} modernization items", Colors.OKBLUE)
            
            print_colored("\n✓ Analysis completed successfully!", Colors.OKGREEN + Colors.BOLD)
            
        except Exception as e:
            print_colored(f"✗ Error parsing result payload: {str(e)}", Colors.FAIL)
            print_colored("\nRaw payload:", Colors.WARNING)
            print(json.dumps(payload, indent=2))
    
    elif response_type == 'error':
        # Error case - display error details
        try:
            error_code = payload.get('code', 'UNKNOWN')
            error_message = payload.get('message', 'No error message provided')
            error_stage = payload.get('stage', 'Unknown stage')
            
            print_colored("ERROR DETAILS", Colors.BOLD + Colors.FAIL)
            print_colored(f"  Code:    {error_code}", Colors.FAIL)
            print_colored(f"  Stage:   {error_stage}", Colors.FAIL)
            print_colored(f"  Message: {error_message}", Colors.FAIL)
            
            print_colored("\n✗ Analysis failed!", Colors.FAIL + Colors.BOLD)
            
        except Exception as e:
            print_colored(f"✗ Error parsing error payload: {str(e)}", Colors.FAIL)
            print_colored("\nRaw payload:", Colors.WARNING)
            print(json.dumps(payload, indent=2))
    
    else:
        print_colored(f"✗ Unexpected response type: {response_type}", Colors.FAIL)
        print_colored("\nRaw response:", Colors.WARNING)
        print(json.dumps(response, indent=2))


def main():
    """Main entry point for the integration test script"""
    global API_BASE_URL, POLL_INTERVAL_SECONDS, MAX_POLL_ATTEMPTS
    
    parser = argparse.ArgumentParser(
        description='RepoSense Integration Test - Test the analysis API end-to-end',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python integration_test.py /path/to/codebase
  python integration_test.py C:\\Users\\username\\projects\\myapp
  python integration_test.py ./relative/path/to/code
        """
    )
    
    parser.add_argument(
        'local_path',
        help='Path to the local codebase directory to analyze'
    )
    
    parser.add_argument(
        '--url',
        default=API_BASE_URL,
        help=f'API base URL (default: {API_BASE_URL})'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=POLL_INTERVAL_SECONDS,
        help=f'Polling interval in seconds (default: {POLL_INTERVAL_SECONDS})'
    )
    
    parser.add_argument(
        '--max-attempts',
        type=int,
        default=MAX_POLL_ATTEMPTS,
        help=f'Maximum polling attempts (default: {MAX_POLL_ATTEMPTS})'
    )
    
    args = parser.parse_args()
    
    # Update global configuration
    API_BASE_URL = args.url
    POLL_INTERVAL_SECONDS = args.interval
    MAX_POLL_ATTEMPTS = args.max_attempts
    
    # Print test configuration
    print_colored("\n" + "=" * 70, Colors.HEADER)
    print_colored("  RepoSense Integration Test", Colors.HEADER + Colors.BOLD)
    print_colored("=" * 70, Colors.HEADER)
    print_colored(f"\nConfiguration:", Colors.OKBLUE)
    print_colored(f"  API URL:        {API_BASE_URL}", Colors.OKBLUE)
    print_colored(f"  Local Path:     {args.local_path}", Colors.OKBLUE)
    print_colored(f"  Poll Interval:  {POLL_INTERVAL_SECONDS}s", Colors.OKBLUE)
    print_colored(f"  Max Attempts:   {MAX_POLL_ATTEMPTS}", Colors.OKBLUE)
    
    start_time = time.time()
    
    try:
        # Step 1: Send analyze request
        job_id, error = send_analyze_request(args.local_path)
        
        if not job_id:
            print_colored(f"\n✗ Test failed: {error}", Colors.FAIL + Colors.BOLD)
            return 1
        
        # Step 2: Poll for results
        response, error = poll_job_status(job_id)
        
        if not response:
            print_colored(f"\n✗ Test failed: {error}", Colors.FAIL + Colors.BOLD)
            return 1
        
        # Step 3: Display results
        display_results(response)
        
        # Calculate and display total time
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        print_colored(f"\nTotal time: {minutes}m {seconds}s", Colors.OKBLUE)
        
        # Return appropriate exit code
        if response.get('type') == 'result':
            return 0  # Success
        else:
            return 1  # Failed analysis
        
    except KeyboardInterrupt:
        print_colored("\n\n✗ Test interrupted by user", Colors.WARNING)
        return 130
    
    except Exception as e:
        print_colored(f"\n✗ Unexpected error: {str(e)}", Colors.FAIL)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())