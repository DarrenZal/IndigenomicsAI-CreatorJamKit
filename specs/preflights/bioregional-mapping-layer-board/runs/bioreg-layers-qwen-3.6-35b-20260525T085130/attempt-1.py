import sys
import json

def main():
    if len(sys.argv) < 2:
        print("error: no input file specified")
        sys.exit(0)
    
    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        print("error: invalid input")
        sys.exit(0)
    
    if not isinstance(data, dict) or 'layers' not in data:
        print("error: invalid input")
        sys.exit(0)
    
    layers = data['layers']
    
    if not isinstance(layers, list):
        print("error: invalid input")
        sys.exit(0)
    
    # Count tiers
    public_count = 0
    steward_count = 0
    private_count = 0
    
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        tier = layer.get('consent_tier', '')
        if tier == 'public':
            public_count += 1
        elif tier == 'steward-review':
            steward_count += 1
        elif tier == 'private':
            private_count += 1
    
    total = len(layers)
    
    # Print header
    print(f"LAYER BOARD ({public_count} public / {steward_count} steward-review / {private_count} private of {total} total layers)")
    print()
    
    # Print public layers
    print("PUBLIC LAYERS:")
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        if layer.get('consent_tier') == 'public':
            layer_id = layer.get('layer_id', '')
            category = layer.get('category', '')
            feature_count = layer.get('feature_count', 0)
            print(f"- {layer_id} [{category}]: {feature_count} features")
    
    print()
    
    # Print withheld summary
    print(f"WITHHELD: {steward_count} steward-review + {private_count} private layers — content not displayed.")

if __name__ == '__main__':
    main()