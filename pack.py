from pathlib import Path
import sys
import struct
import json

def unpack(file_path):
    path = Path(file_path)
    out_dir = path.parent / path.stem
    out_dir.mkdir(exist_ok=True)

    with open(file_path, 'rb') as file:
        # Read the first 4 bytes as a big-endian integer
        header_len = file.read(4)
        if len(header_len) < 4:
            raise ValueError("Truncated header length")

        header_len = struct.unpack('>I', header_len)[0]

        header_bytes = file.read(header_len)
        if len(header_bytes) < header_len:
            raise ValueError("Truncated header")

        header = json.loads(header_bytes.decode('utf-8'), object_pairs_hook=lambda pairs: pairs)

        for (obj_name, obj_len) in header:
            print((obj_name, obj_len))
            if obj_name[0] == "/":
                obj_name = obj_name[1:]
            else:
                print(f"Warning: object '{obj_name}' does not start with '/'!", file=sys.stderr)

            obj_data = file.read(obj_len)
            if len(obj_data) < obj_len:
                raise ValueError(f"Truncated file {obj_name}")

            with open(out_dir / obj_name, "wb") as of:
                of.write(obj_data)

        bytes_read = file.tell()

        if len(file.read(1)) > 0:
            print(f"Extra data following archive, at byte {bytes_read}", file=sys.stderr)

def help(code=1):
    print("Usage: python script.py ...")
    print("    unpack (filename)")
    print("    pack (dirname)")
    sys.exit(code)


if __name__ == '__main__':
    argv = sys.argv

    if len(argv) <= 1:
        help()

    command = argv[1]
    if command == "unpack":
        if len(argv) <= 2:
            help()
        filename = sys.argv[2]
        unpack(filename)

    else:
        help()

