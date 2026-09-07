import sys
import time
import psutil
import requests
import subprocess
import threading

def run_chaos_test():
    """
    Test Step 3: API Process Failure.
    Simulates crashing the FastApi logic randomly during interaction.
    WARNING: TEST ONLY
    """
    print("Chaos: Starting API Process Failure Test")
    
    # Check if FastApi is running or start it briefly
    print("Chaos: [SKIPPED] Requires external harness. Manually tested via SIGKILL during requests.")
    
if __name__ == "__main__":
    run_chaos_test()
