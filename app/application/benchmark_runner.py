import sys
from pathlib import Path
sys.path.append(str(Path(r"c:\Users\divay\adk-project")))

import argparse
import time
from collections import defaultdict
from app.application.demo2_e2e import run_demo2

def run_benchmark(prompt_path: str, iterations: int):
    print(f"Starting benchmark for {prompt_path} ({iterations} iterations)")
    
    results = {
        "successes": 0,
        "failures": 0,
        "total_latency": 0.0,
        "total_tokens": 0,
        "total_execution_duration": 0.0,
        "failure_reasons": defaultdict(int)
    }
    
    start_time = time.time()
    
    for i in range(iterations):
        print(f"\n--- Iteration {i+1}/{iterations} ---")
        try:
            metrics = run_demo2(prompt_path)
            
            if metrics["success"]:
                results["successes"] += 1
                results["total_latency"] += metrics["latency_ms"]
                results["total_tokens"] += metrics["total_tokens"]
                results["total_execution_duration"] += metrics["execution_duration"]
            else:
                results["failures"] += 1
                results["failure_reasons"][metrics["failure_stage"]] += 1
                
        except Exception as e:
            print(f"Benchmark iteration failed critically: {e}")
            results["failures"] += 1
            results["failure_reasons"]["CRITICAL_EXCEPTION"] += 1
            
    end_time = time.time()
    
    print("\n=============================================")
    print(f" BENCHMARK REPORT: {prompt_path}")
    print(f" Total Runs: {iterations} | Time Elapsed: {end_time - start_time:.2f}s")
    print("=============================================")
    
    success_rate = (results["successes"] / iterations) * 100
    print(f"Success Rate: {success_rate:.1f}% ({results['successes']} / {iterations})")
    
    if results["successes"] > 0:
        avg_latency = results["total_latency"] / results["successes"]
        avg_tokens = results["total_tokens"] / results["successes"]
        avg_duration = results["total_execution_duration"] / results["successes"]
        
        print("\nAverages (Successful Runs Only):")
        print(f"  Latency:            {avg_latency:.2f} ms")
        print(f"  Token Usage:        {avg_tokens:.0f} tokens")
        print(f"  Execution Duration: {avg_duration:.2f} s")
        
    if results["failures"] > 0:
        print("\nFailure Breakdown:")
        for reason, count in results["failure_reasons"].items():
            print(f"  {reason}: {count} failures")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ADK Demo 2 Benchmark")
    parser.add_argument("--iterations", type=int, default=5, help="Number of times to run the benchmark")
    parser.add_argument("--prompt", type=str, default=r"c:\Users\divay\adk-project\app\prompts\demo2_prompt.txt", 
                        help="Path to the prompt file to use")
    
    args = parser.parse_args()
    
    run_benchmark(args.prompt, args.iterations)
