#!/usr/bin/env python3
"""Analyze GuideLLM benchmark results."""

import json
from pathlib import Path

results_dir = Path("./guidellm/results_phi3/pt50_ot100")
json_path = results_dir / "benchmarks.json"

print(f"Reading: {json_path}")
with open(json_path) as f:
    data = json.load(f)

print("\n" + "="*60)
print("          BENCHMARK RESULTS SUMMARY")
print("="*60)

meta = data.get("metadata", {})
print(f"\nGuideLLM Version: {meta.get('guidellm_version', 'N/A')}")
print(f"Python Version: {meta.get('python_version', 'N/A')}")
print(f"Platform: {meta.get('platform', 'N/A')}")

args = data.get("args", {})
print(f"\nTarget: {args.get('target', 'N/A')}")
print(f"Model: {args.get('model', 'N/A')}")
print(f"Profile: {args.get('profile', 'N/A')}")
print(f"Rate: {args.get('rate', 'N/A')} req/sec")
print(f"Max Duration: {args.get('max_seconds', 'N/A')} seconds")

if "benchmarks" in data and len(data["benchmarks"]) > 0:
    bench = data["benchmarks"][0]
    metrics = bench.get("metrics", {})
    scheduler = bench.get("scheduler_state", {})
    
    print("\n" + "-"*60)
    print("REQUEST STATISTICS")
    print("-"*60)
    
    successful = scheduler.get("successful_requests", 0)
    errored = scheduler.get("errored_requests", 0)
    incomplete = scheduler.get("cancelled_requests", 0)
    processed = scheduler.get("processed_requests", 0)
    
    print(f"  Successful:  {successful}")
    print(f"  Errored:     {errored}")
    print(f"  Incomplete:  {incomplete}")
    print(f"  Processed:   {processed}")
    
    total = successful + errored + incomplete
    if total > 0:
        success_rate = (successful / total) * 100
        error_rate = (errored / total) * 100
        print(f"\n  Success Rate: {success_rate:.1f}%")
        print(f"  Error Rate:   {error_rate:.1f}%")
    
    print("\n" + "-"*60)
    print("LATENCY (Successful Requests)")
    print("-"*60)
    
    latency = metrics.get("request_latency", {}).get("successful", {})
    if latency:
        print(f"  Mean:   {latency.get('mean', 0):.2f} sec")
        print(f"  Median: {latency.get('median', 0):.2f} sec")
        print(f"  Std Dev: {latency.get('std_dev', 0):.2f} sec")
        print(f"  Min:    {latency.get('min', 0):.2f} sec")
        print(f"  Max:    {latency.get('max', 0):.2f} sec")
        percs = latency.get('percentiles', {})
        if percs:
            print(f"  P50:    {percs.get('p50', 0):.2f} sec")
            print(f"  P95:    {percs.get('p95', 0):.2f} sec")
            print(f"  P99:    {percs.get('p99', 0):.2f} sec")
    
    print("\n" + "-"*60)
    print("TIME TO FIRST TOKEN (TTFT)")
    print("-"*60)
    
    ttft = metrics.get("time_to_first_token_ms", {}).get("successful", {})
    if ttft:
        print(f"  Mean:   {ttft.get('mean', 0):.2f} ms")
        print(f"  Median: {ttft.get('median', 0):.2f} ms")
        print(f"  Min:    {ttft.get('min', 0):.2f} ms")
        print(f"  Max:    {ttft.get('max', 0):.2f} ms")
    
    print("\n" + "-"*60)
    print("INTER-TOKEN LATENCY (ITL)")
    print("-"*60)
    
    itl = metrics.get("inter_token_latency_ms", {}).get("successful", {})
    if itl:
        print(f"  Mean:   {itl.get('mean', 0):.2f} ms")
        print(f"  Median: {itl.get('median', 0):.2f} ms")
    
    print("\n" + "-"*60)
    print("THROUGHPUT")
    print("-"*60)
    
    out_tps = metrics.get("output_tokens_per_second", {}).get("successful", {})
    if out_tps:
        print(f"  Output Tokens/sec (Mean):   {out_tps.get('mean', 0):.2f}")
        print(f"  Output Tokens/sec (Median): {out_tps.get('median', 0):.2f}")
    
    req_tps = metrics.get("requests_per_second", {}).get("successful", {})
    if req_tps:
        print(f"  Requests/sec (Mean):        {req_tps.get('mean', 0):.4f}")

    print("\n" + "-"*60)
    print("DURATION")
    print("-"*60)
    print(f"  Total Duration: {bench.get('duration', 0):.2f} sec")
    print(f"  Start Time: {bench.get('start_time', 'N/A')}")
    print(f"  End Time: {bench.get('end_time', 'N/A')}")

print("\n" + "="*60)
print("View detailed HTML report:")
print(f"  open {results_dir / 'benchmarks.html'}")
print("="*60)
