import json
import requests
import time
import os

def run_evals():
    api_url = "http://127.0.0.1:8000/scan"
    payloads_path = os.path.join(os.path.dirname(__file__), "test_payloads.json")
    
    with open(payloads_path, "r") as f:
        tests = json.load(f)

    print(f"\n🚀 INIT: Firing {len(tests)} automated payloads at PCI Agent...\n")
    
    passed_evals = 0
    total_latency = 0

    for i, test in enumerate(tests):
        print(f"[{i+1}/{len(tests)}] Scanning {test['system_id']}...")
        
        expected = test["expected_status"]
        payload = {
            "system_id": test["system_id"],
            "cloud_provider": test["cloud_provider"],
            "pci_version": test["pci_version"],
            "config_override": test["config_override"]
        }
        
        start_time = time.time()
        response = requests.post(api_url, json=payload)
        latency = time.time() - start_time
        total_latency += latency
        
        if response.status_code == 200:
            actual = response.json().get("status")
            if actual == expected:
                print(f"   ✅ PASS (Agent predicted {actual} correctly in {latency:.2f}s)")
                passed_evals += 1
            else:
                print(f"   ❌ FAIL (Expected {expected}, Got {actual})")
                print(f"      Reasoning: {response.json().get('reasoning')}")
        else:
            print(f"   ⚠️ SERVER ERROR: HTTP {response.status_code}")

    accuracy = (passed_evals / len(tests)) * 100
    avg_latency = total_latency / len(tests)
    
    print("\n" + "="*45)
    print("🏆 FINAL EVALUATION REPORT")
    print("="*45)
    print(f"Total Tests:  {len(tests)}")
    print(f"Accuracy:     {accuracy}%")
    print(f"Avg Latency:  {avg_latency:.2f}s per scan")
    print("="*45 + "\n")

if __name__ == "__main__":
    run_evals()