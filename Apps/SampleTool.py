#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: SampleTool.py <old_version> <new_version>")
        sys.exit(1)
    old_version = sys.argv[1]
    new_version = sys.argv[2]
    print(f"[SampleTool] Running sample operations: old={old_version}, new={new_version}")
    import os
    os.makedirs("artifacts", exist_ok=True)
    with open(f"artifacts/SampleTool_{old_version}.txt", "w", encoding="utf-8") as f:
        f.write(f"output from SampleTool {old_version}\n")

if __name__ == "__main__":
    main()
