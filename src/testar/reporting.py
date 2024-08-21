def print_test_summary(url, num_runs, length_sequence, errors):
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
