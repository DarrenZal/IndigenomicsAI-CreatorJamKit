import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]

    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError, ValueError):
        print("error:")
        sys.exit(0)

    layers = data.get("layers", [])
    
    public_count = 0
    steward_count = 0
    private_count = 0
    public_layers = []

    for layer in layers:
        tier = layer.get("consent_tier")
        if tier == "public":
            public_count += 1
            public_layers.append(layer)
        elif tier == "steward-review":
            steward_count += 1
        elif tier == "private":
            private_count += 1

    total_layers = len(layers)
    
    # Header: LAYER BOARD (<P> public / <S> steward-review / <X> private of <N> total layers)
    print(f"LAYER BOARD ({public_count} public / {steward_count} steward-review / {private_count} private of {total_layers} total layers)")
    print("")
    
    print("PUBLIC LAYERS:")
    for layer in public_layers:
        lid = layer.get("layer_id")
        cat = layer.get("category")
        count = layer.get("feature_count")
        print(f"- {lid} [{cat}]: {count} features")
    
    print("")
    # Withheld section: WITHHELD: <S> steward-review + <X> private layers — content not displayed.
    print(f"WITHHELD: {steward_count} steward-review + {private_count} private layers — content not displayed.")

if __name__ == "__main__":
    main()