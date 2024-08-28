from logging_actions import *

def report_element_coverage(visited, discovered):
    visited_ids = {x for (x,y,z) in visited}
    discovered_ids = {x for (x,y) in discovered}
    print(len(visited_ids), visited_ids)
    print(len(discovered_ids), discovered_ids)
    if discovered_ids:
        coverage = (len(visited_ids) / len(discovered_ids)) * 100
        print(f"Element Coverage: {coverage:.2f}%")
    else:
        print("No actionable elements discovered during testing.")


def print_test_summary(url, num_runs, length_sequence, errors, visited, discovered):
    print("="*30)
    print("TEST SUMMARY REPORT")
    print("="*30)
    print(f"Tested URL: {url}")
    print(f"Number of Runs: {num_runs}")
    print(f"Sequence Length per Run: {length_sequence}")
    print("="*30)
    
    if not errors:
        print("RESULT: All tests passed successfully! 🎉")
    else:
        print(f"RESULT: {len(errors)} errors were found 🚨")
        print("-"*30)
        print("ERROR DETAILS:")
        print("-"*30)
        for e in errors:
            print(f"{e}")
    
    print("="*30)
    
    report_element_coverage(visited, discovered)
