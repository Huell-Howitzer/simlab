import sys
import gc

# Helper function to print refcount cleanly (accounting for +1 in getrefcount)
def print_refcount(label, obj):
    count = sys.getrefcount(obj) - 1  # subtract the temp reference from the argument
    print(f"Refcount for {label}: {count}")

print("\n--- Checking built-in objects ---")
n = 42
lst = [1, 2, 3]

print_refcount("integer 42", n)
print_refcount("list [1, 2, 3]", lst)

print("\n--- Creating custom objects ---")

class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None

    def __del__(self):
        print(f"{self.name} is being deleted")

a = Node('A')
b = Node('B')

print_refcount("Node A", a)
print_refcount("Node B", b)

print("\n--- Linking objects into a cycle ---")
a.ref = b
b.ref = a

print_refcount("Node A (after linking)", a)
print_refcount("Node B (after linking)", b)

print("\n--- Removing external references ---")
a = None
b = None

print("At this point, the only references are from the cycle itself.")

print("\n--- Running garbage collection ---")
unreachable = gc.collect()
print(f"Garbage collector collected {unreachable} unreachable objects.")

print("\n--- Done ---")