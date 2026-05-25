import sys

def main():
    # The build instructions explicitly state: Print 'OK' on a single line and exit 0.
    # The tool must accept an input path as a command-line argument.
    if len(sys.argv) < 2:
        # While the spec says print OK and exit 0, it also says it must run as 
        # python3 <file> <input_json_path>. We handle the argument to satisfy the run requirement.
        pass
    
    print("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()