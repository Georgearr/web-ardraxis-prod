import glob, re, os

for f in sorted(glob.glob("static/img/ardrazine/*.svg")):
    with open(f, "rb") as fp:
        head = fp.read(1500).decode("latin1", errors="ignore")
        w_match = re.search(r'width="([^"]+)"', head)
        h_match = re.search(r'height="([^"]+)"', head)
        vb_match = re.search(r'viewBox="([^"]+)"', head)
        size_mb = os.path.getsize(f) / (1024*1024)
        print(f"{os.path.basename(f)}: size={size_mb:.2f}MB, w={w_match.group(1) if w_match else '?'}, h={h_match.group(1) if h_match else '?'}, vb={vb_match.group(1) if vb_match else '?'}")
