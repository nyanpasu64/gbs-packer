from pathlib import Path
import os.path
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

def pack(dirname, out_name):
    dirname = Path(dirname)
    filenames = dirname.iterdir()

    objects = []

    for name in filenames:
        print(name)
        if not name.is_file():
            continue
        with name.open('rb') as f:
            objects.append(('/' + name.name, f.read()))

    header_dict = {obj_name: len(obj_data) for (obj_name, obj_data) in objects}
    header = json.dumps(header_dict).encode("utf-8")
    print(header)

    with open(out_name, "wb") as of:
        of.write(struct.pack(">I", len(header)))
        of.write(header)
        for (_, obj_data) in objects:
            of.write(obj_data)

def help(code=1):
    print("Usage: python script.py ...")
    print("    unpack (filename)")
    print("    pack (dirname) (new filename)")
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

    elif command == "pack":
        if len(argv) <= 3:
            help()
        dirname = sys.argv[2]
        out_name = sys.argv[3]
        pack(dirname, out_name)


    else:
        help()

