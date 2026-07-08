import struct, os, shutil
from PIL import Image
import io

def create_ico_raw(images):
    num = len(images)
    header = struct.pack('<HHH', 0, 1, num)
    data_offset = 6 + (num * 16)
    chunks = []
    entries = b''
    for img in images:
        w = img.width if img.width < 256 else 0
        h = img.height if img.height < 256 else 0
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        png = buf.getvalue()
        chunks.append(png)
        entries += struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(png), data_offset)
        data_offset += len(png)
    return header + entries + b''.join(chunks)

img = Image.new('RGB', (720, 720), color=(100, 50, 200)).convert('RGBA')
sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
images = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]

ico = create_ico_raw(images)

# Find cover dir
for root, dirs, files in os.walk(r'C:\Music'):
    for f in files:
        if f == 'folder.ico':
            dst = os.path.join(root, f)
            # Write via temp
            tmp = os.path.join(os.environ['TEMP'], 'new_folder.ico')
            with open(tmp, 'wb') as fh:
                fh.write(ico)
            shutil.copy2(tmp, dst)
            print(f'Written: {dst} ({len(ico)} bytes)')

            num_icons = struct.unpack_from('<H', ico, 4)[0]
            print(f'Icons in file: {num_icons}')
            for i in range(num_icons):
                offset = 6 + (i * 16)
                w, h = struct.unpack_from('<BB', ico, offset)
                sz = struct.unpack_from('<I', ico, offset + 8)[0]
                print(f'  Icon {i}: {w or 256}x{h or 256}, {sz} bytes PNG data')
