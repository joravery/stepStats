import brotli

def compress_string(blob: str):
    return brotli.compress(blob.encode())

def decompress_string(blob: bytes):
    return brotli.decompress(blob).decode()

if __name__ == "__main__":
    import sys
    try:
        file_path = sys.argv[1]
        if file_path is None or file_path == '':
            print("You must provide a file path when calling directly")
            sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)
    with open(file_path, 'r') as f:
        contents = f.read()
    compressed = compress_string(contents)

    with open(f"{file_path}.br", "wb") as out:
        out.write(compressed)
