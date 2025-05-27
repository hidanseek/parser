import os
import subprocess
import sys
import csv

# Powered by GPT-4o!
# KNU COMP0321: Compiler Design

def run_test(minic_path, test_input_path):
    try:
        result = subprocess.run(
            [sys.executable, minic_path, test_input_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip().splitlines()
    except Exception as e:
        return [f"[ERROR] Failed to run {minic_path} with {test_input_path}: {str(e)}"]

def load_expected_output(output_path):
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            return f.read().strip().splitlines()
    except Exception as e:
        return [f"[ERROR] Failed to load expected output: {str(e)}"]

def compare_outputs(expected, actual):
    return expected == actual

def count_differences(expected, actual):
    count = 0
    max_len = max(len(expected), len(actual))
    for i in range(max_len):
        exp = expected[i] if i < len(expected) else "<no line>"
        act = actual[i] if i < len(actual) else "<no line>"
        if exp != act:
            count += 1
    return count

def show_differences(expected, actual):
    print("{:<6} {:<50} | {:<50}".format("Line", "Expected", "Actual"))
    print("-" * 110)
    max_len = max(len(expected), len(actual))
    for i in range(max_len):
        exp = expected[i] if i < len(expected) else "<no line>"
        act = actual[i] if i < len(actual) else "<no line>"
        if exp != act:
            print(f"{i+1:<6} {exp:<50} | {act:<50}")

def grade_all_tests(minic_path, testcase_dir='tst/base/testcases', solution_dir='tst/base/solutions'):
    total = 0
    passed = 0
    results = []

    # You can set the size of testcases (default: 80)
    for i in range(1, 75):
        test_filename = f'c{i}.txt'
        solution_filename = f's_c{i}.txt'

        test_file = os.path.join(testcase_dir, test_filename)
        solution_file = os.path.join(solution_dir, solution_filename)

        if not os.path.exists(test_file) or not os.path.exists(solution_file):
            print(f"⚠️  Test #{i}: Skipped (file missing)")
            print(f"  → 🔍 Looking for: {os.path.abspath(test_file)}  → Exists? {os.path.exists(test_file)}")
            print(f"  → 🔍 Looking for: {os.path.abspath(solution_file)}  → Exists? {os.path.exists(solution_file)}")
            continue

        student_output = run_test(minic_path, test_file)
        expected_output = load_expected_output(solution_file)

        if compare_outputs(expected_output, student_output):
            print(f"✅ Test #{i}: Passed")
            passed += 1
            results.append([test_filename, 'Passed', 0])
        else:
            diff_count = count_differences(expected_output, student_output)
            print(f"❌ Test #{i}: Failed ({diff_count} differences)")
            show_differences(expected_output, student_output)
            results.append([test_filename, 'Failed', diff_count])
            print()

        total += 1

    # CSV 저장
    csv_path = os.path.join(os.getcwd(), 'grading_results.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Test Case', 'Result', 'Difference Count'])
        writer.writerows(results)

    print(f"\n📄 Grading results saved to {csv_path}")
    print(f"📊 Final Score: {passed} / {total} tests passed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-grader for MiniC Scanner")
    parser.add_argument("--minic", type=str, default="MiniC.py", help="Path to MiniC.py")
    parser.add_argument("--testcase_dir", type=str, default="tst/base/testcases", help="Path to test case inputs")
    parser.add_argument("--solution_dir", type=str, default="tst/base/solutions", help="Path to expected outputs")
    args = parser.parse_args()

    grade_all_tests(args.minic, args.testcase_dir, args.solution_dir)
