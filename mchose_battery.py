
import os, glob, fcntl, time, json

# Read-only helper: asks the MCHOSE receiver for its status (command f9)
# and prints one line of JSON. It never changes any mouse setting.

def ioc(nr, size):
    return (3 << 30) | (size << 16) | (ord("H") << 8) | nr

def usage_pages(d):
    pages = set()
    i = 0
    while i < len(d):
        b = d[i]
        size = b & 3
        if size == 3:
            size = 4
        if (b & 0xFC) == 0x04:
            pages.add(int.from_bytes(d[i + 1:i + 1 + size], "little"))
        i += 1 + size
    return pages

def find_node():
    for sysdir in sorted(glob.glob("/sys/class/hidraw/hidraw*")):
        try:
            info = open(sysdir + "/device/uevent").read().upper()
            desc = open(sysdir + "/device/report_descriptor", "rb").read()
        except OSError:
            continue
        if ":00003837:" in info and 0xFF01 in usage_pages(desc):
            return "/dev/" + os.path.basename(sysdir)
    return None

def main():
    node = find_node()
    if node is None:
        return {"ok": False, "reason": "no receiver"}
    pad = bytes([0xFF] * 19)
    payload = bytes([0x11, 0xF9]) + pad
    try:
        fd = os.open(node, os.O_RDWR)
    except OSError as e:
        return {"ok": False, "reason": "cannot open: %s" % e}
    try:
        fcntl.ioctl(fd, ioc(0x06, len(payload)), payload)
        for _ in range(40):
            time.sleep(0.05)
            buf = bytearray(21)
            buf[0] = 0x11
            fcntl.ioctl(fd, ioc(0x07, len(buf)), buf)
            raw = bytes(buf)
            if raw[1] == 0xF9 and raw[2:] != pad:
                a = 255 - raw[11]
                b = 255 - raw[13]
                if 1 <= a <= 100 and 1 <= b <= 100:
                    return {"ok": True, "battery": a, "battery2": b}
                return {"ok": False, "reason": "value out of range: %d" % a}
        return {"ok": False, "reason": "no reply"}
    except OSError as e:
        return {"ok": False, "reason": "error: %s" % e}
    finally:
        os.close(fd)

print(json.dumps(main()))

