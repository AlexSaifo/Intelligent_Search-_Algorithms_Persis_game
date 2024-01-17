import sys

# Get the current recursion limit
current_limit = sys.getrecursionlimit()
print(f"Current recursion limit: {current_limit}")

# Set a new recursion limit
sys.setrecursionlimit(1000000000)

# Verify the new recursion limit
new_limit = sys.getrecursionlimit()
print(f"New recursion limit: {new_limit}")
