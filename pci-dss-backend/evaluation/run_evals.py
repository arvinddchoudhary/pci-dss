import json
import requests
import time
import os
from collections import defaultdict

def run_evals():
    api_url = "http://127.0.0.1:8000/scan"
    payloads_path = os.path.join(os.path.dirname(__file__), "test_payloads.json")
    
    with open(payloads_path, "r") as f:
        tests = json.load(f)

    print(f"\n🚀 PCI DSS Agent Evaluation Suite — {len(tests)} test cases\n")
    print("=" * 70)
    
    passed_evals = 0
    failed_evals = 0
    total_latency = 0
    results_by_category = defaultdict(lambda: {"pass": 0, "fail": 0})
    false_positives = 0
    false_negatives = 0
    detailed_failures = []

    for i, test in enumerate(tests):
        system_id = test["system_id"]
        description = test.get("description", "")
        expected = test["expected_status"]
        
        print(f"\n[{i+1}/{len(tests)}] {system_id}")
        print(f"   📋 {description}")
        
        payload = {
            "system_id": test["system_id"],
            "cloud_provider": test["cloud_provider"],
            "pci_version": test["pci_version"],
            "config_override": test["config_override"]
        }
        
        start_time = time.time()
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            latency = time.time() - start_time
            total_latency += latency
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  CONNECTION ERROR: {e}")
            failed_evals += 1
            continue
        
        if response.status_code == 200:
            actual = response.json().get("status")
            rule = response.json().get("violated_rule", "N/A")
            score = response.json().get("risk_score", "N/A")
            reasoning = response.json().get("reasoning", "")
            ticket = response.json().get("ticket_id", "N/A")
            
            if actual == expected:
                print(f"   ✅ CORRECT — Predicted: {actual} | Rule: {rule} | Risk: {score} | Ticket: {ticket} | {latency:.2f}s")
                passed_evals += 1
            else:
                print(f"   ❌ WRONG  — Expected: {expected}, Got: {actual} | {latency:.2f}s")
                print(f"      Rule: {rule} | Reasoning: {reasoning[:100]}...")
                failed_evals += 1
                detailed_failures.append({
                    "system_id": system_id,
                    "expected": expected,
                    "actual": actual,
                    "reasoning": reasoning
                })
                
                # Track false positive / false negative
                if expected == "PASS" and actual == "VIOLATION":
                    false_positives += 1
                elif expected == "VIOLATION" and actual == "PASS":
                    false_negatives += 1
            
            # Categorize by system type
            if "db" in system_id or "database" in system_id:
                cat = "Infrastructure/DB"
            elif "iam" in system_id or "user" in system_id:
                cat = "Identity/IAM"
            elif "net" in system_id or "fw" in system_id:
                cat = "Network"
            elif "encrypt" in system_id or "tls" in system_id or "ssl" in system_id:
                cat = "Encryption"
            else:
                cat = "Other"
            
            if actual == expected:
                results_by_category[cat]["pass"] += 1
            else:
                results_by_category[cat]["fail"] += 1
        else:
            print(f"   ⚠️  SERVER ERROR: HTTP {response.status_code}")
            failed_evals += 1

    total = passed_evals + failed_evals
    accuracy = (passed_evals / total * 100) if total > 0 else 0
    avg_latency = total_latency / total if total > 0 else 0
    fp_rate = (false_positives / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 70)
    print("🏆 PCI DSS AGENT — EVALUATION REPORT")
    print("=" * 70)
    print(f"\n📊 Overall Results:")
    print(f"   Total Tests:       {total}")
    print(f"   Passed:            {passed_evals}")
    print(f"   Failed:            {failed_evals}")
    print(f"   Accuracy:          {accuracy:.1f}%     {'✅ MEETS 95% TARGET' if accuracy >= 95 else '❌ BELOW 95% TARGET'}")
    print(f"   False Positive Rate: {fp_rate:.1f}%   {'✅ BELOW 5% TARGET' if fp_rate < 5 else '❌ ABOVE 5% TARGET'}")
    print(f"   False Negatives:   {false_negatives}")
    print(f"   Avg Latency:       {avg_latency:.2f}s per scan")
    
    print(f"\n📂 Results by Category:")
    for cat, counts in sorted(results_by_category.items()):
        cat_total = counts["pass"] + counts["fail"]
        cat_acc = (counts["pass"] / cat_total * 100) if cat_total > 0 else 0
        print(f"   {cat:20s} — {counts['pass']}/{cat_total} correct ({cat_acc:.0f}%)")
    
    if detailed_failures:
        print(f"\n❌ Detailed Failures:")
        for f in detailed_failures:
            print(f"   [{f['system_id']}] Expected {f['expected']}, Got {f['actual']}")
            print(f"      → {f['reasoning'][:120]}")
    
    print("\n" + "=" * 70)
    
    # Also test other endpoints
    print("\n🔍 Testing Additional Endpoints...\n")
    _test_endpoint("GET", "http://127.0.0.1:8000/health", "Health Check")
    _test_endpoint("GET", "http://127.0.0.1:8000/dashboard", "Dashboard")
    _test_endpoint("GET", "http://127.0.0.1:8000/remediation", "Remediation Workplan")
    _test_endpoint("GET", "http://127.0.0.1:8000/report", "QSA Report")
    _test_endpoint("GET", "http://127.0.0.1:8000/evidence", "Evidence Packages")
    _test_endpoint("GET", "http://127.0.0.1:8000/evidence/completeness", "Evidence Completeness")
    _test_endpoint("GET", "http://127.0.0.1:8000/approvals", "Approval Queue")
    _test_endpoint("GET", "http://127.0.0.1:8000/audit-log?limit=5", "Audit Log")
    _test_endpoint("GET", "http://127.0.0.1:8000/audit-log/verify", "Hash Chain Verification")
    _test_endpoint("GET", "http://127.0.0.1:8000/agent-activity?limit=5", "Agent Activity Log")
    
    print("\n" + "=" * 70)
    print("✅ Evaluation complete.")
    print("=" * 70 + "\n")


def _test_endpoint(method, url, name):
    try:
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                print(f"   ✅ {name:25s} — HTTP 200 ({len(data)} keys)")
            elif isinstance(data, list):
                print(f"   ✅ {name:25s} — HTTP 200 ({len(data)} items)")
            else:
                print(f"   ✅ {name:25s} — HTTP 200")
        else:
            print(f"   ❌ {name:25s} — HTTP {resp.status_code}")
    except Exception as e:
        print(f"   ⚠️  {name:25s} — Error: {e}")


if __name__ == "__main__":
    run_evals()