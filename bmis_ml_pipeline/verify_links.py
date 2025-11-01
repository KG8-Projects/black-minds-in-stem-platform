"""
Link Verification Script for BMIS Dataset

This script tests all URLs in the BMIS dataset to identify broken links.
Uses parallel requests for faster processing.

Usage:
    python verify_links.py
"""

import pandas as pd
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time


def test_url(url, timeout=10):
    """
    Test if a URL is accessible.

    Args:
        url: URL to test
        timeout: Request timeout in seconds

    Returns:
        dict with url, status_code, accessible, error message
    """
    result = {
        'url': url,
        'status_code': None,
        'accessible': False,
        'error': None,
        'response_time': None
    }

    if pd.isna(url) or not url or url == 'N/A':
        result['error'] = 'Invalid URL'
        return result

    try:
        start_time = time.time()
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        response_time = time.time() - start_time

        result['status_code'] = response.status_code
        result['response_time'] = round(response_time, 2)

        # Consider 2xx and 3xx as successful
        if 200 <= response.status_code < 400:
            result['accessible'] = True
        else:
            result['error'] = f'HTTP {response.status_code}'

    except requests.exceptions.Timeout:
        result['error'] = 'Timeout'
    except requests.exceptions.ConnectionError:
        result['error'] = 'Connection Error'
    except requests.exceptions.TooManyRedirects:
        result['error'] = 'Too Many Redirects'
    except requests.exceptions.RequestException as e:
        result['error'] = f'Request Error: {str(e)[:50]}'
    except Exception as e:
        result['error'] = f'Unknown Error: {str(e)[:50]}'

    return result


def verify_all_links(dataset_path, max_workers=10, timeout=10):
    """
    Verify all links in the dataset.

    Args:
        dataset_path: Path to CSV file
        max_workers: Number of parallel workers
        timeout: Request timeout in seconds

    Returns:
        DataFrame with verification results
    """
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)

    # Get all unique URLs
    if 'url' not in df.columns:
        print("Error: 'url' column not found in dataset")
        return None

    urls = df['url'].dropna().unique().tolist()
    total_urls = len(urls)

    print(f"\nFound {total_urls:,} unique URLs to verify")
    print(f"Using {max_workers} parallel workers with {timeout}s timeout")
    print("\nStarting verification...\n")

    results = []
    completed = 0

    # Test URLs in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(test_url, url, timeout): url for url in urls}

        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)
            completed += 1

            # Progress indicator
            if completed % 50 == 0 or completed == total_urls:
                accessible = sum(1 for r in results if r['accessible'])
                print(f"Progress: {completed}/{total_urls} ({100*completed/total_urls:.1f}%) - "
                      f"{accessible} accessible ({100*accessible/completed:.1f}%)")

    results_df = pd.DataFrame(results)
    return results_df


def generate_report(results_df, output_path):
    """
    Generate a summary report and save results.

    Args:
        results_df: DataFrame with verification results
        output_path: Path to save report CSV
    """
    # Calculate statistics
    total = len(results_df)
    accessible = results_df['accessible'].sum()
    inaccessible = total - accessible

    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"Total URLs tested: {total:,}")
    print(f"Accessible: {accessible:,} ({100*accessible/total:.1f}%)")
    print(f"Inaccessible: {inaccessible:,} ({100*inaccessible/total:.1f}%)")
    print()

    # Error breakdown
    print("Error Breakdown:")
    error_counts = results_df[~results_df['accessible']]['error'].value_counts()
    for error, count in error_counts.items():
        print(f"  {error}: {count} ({100*count/total:.1f}%)")
    print()

    # Response time stats for accessible URLs
    accessible_df = results_df[results_df['accessible']]
    if len(accessible_df) > 0:
        avg_response = accessible_df['response_time'].mean()
        median_response = accessible_df['response_time'].median()
        max_response = accessible_df['response_time'].max()

        print("Response Time Statistics (accessible URLs):")
        print(f"  Average: {avg_response:.2f}s")
        print(f"  Median: {median_response:.2f}s")
        print(f"  Max: {max_response:.2f}s")
        print()

    # Save results
    results_df.to_csv(output_path, index=False)
    print(f"Detailed results saved to: {output_path}")
    print("="*60)


def main():
    """Main function"""
    # Paths
    base_dir = Path(__file__).parent
    dataset_path = base_dir / 'data' / 'bmis_final_ml_ready_dataset_cs_refined.csv'
    output_dir = base_dir / 'logs'
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'link_verification_{timestamp}.csv'

    # Check if dataset exists
    if not dataset_path.exists():
        print(f"Error: Dataset not found at {dataset_path}")
        return

    print("="*60)
    print("BMIS Link Verification Script")
    print("="*60)
    print(f"Dataset: {dataset_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Verify links
    start_time = time.time()
    results_df = verify_all_links(dataset_path, max_workers=10, timeout=10)

    if results_df is not None:
        # Generate report
        generate_report(results_df, output_path)

        elapsed = time.time() - start_time
        print(f"\nTotal time: {elapsed/60:.1f} minutes")

        # Save broken links separately
        broken_df = results_df[~results_df['accessible']]
        if len(broken_df) > 0:
            broken_path = output_dir / f'broken_links_{timestamp}.csv'
            broken_df.to_csv(broken_path, index=False)
            print(f"Broken links saved to: {broken_path}")


if __name__ == "__main__":
    main()
