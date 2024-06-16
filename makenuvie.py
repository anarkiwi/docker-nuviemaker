import pexpect
import subprocess
import os
import sys
import glob
import shutil
import time

prefix = "aa"
telnet = "telnet"
p = r"\(C:\$.+\)\s+"
wd = "/work"
iod = "/iod"
fl = 768
reusize = 16384
bname = os.path.basename(sys.argv[1])
infile = os.path.join(iod, bname)
reu = os.path.join(iod, bname.split(".")[0] + ".reu")
assert os.path.exists(infile)

commands = [
    (
        [
            "del",
            "bk exec $ffe4 if @default:$c6 == $0",
            "bk load $dc01 if pc < $d000",
            r'keybuf load"n*",8,1\nrun\n',
        ],
        10,
    ),
    (["r a=ef"], 5),  # clear REU
    ([r"keybuf \n"], 60),  # no music
    ([r"keybuf %s\n" % prefix], 5),  # prefix
    ([r"keybuf \n"], 600),  # wrap frames
    ([r"keybuf \x03"], 5),
    ([r"keybuf \x03"], 5),
]


subprocess.check_call(
    [
        "ffmpeg",
        "-i",
        infile,
        "-vf",
        "fps=12",
        "-frames:v",
        str(fl),
        wd + "/" + prefix + "%03d.bmp",
    ]
)
bmps = "\n".join([str(f) for f in glob.glob(wd + "/" + "*bmp")])
subprocess.run(
    [
        "parallel",
        "mufflon",
        "--flibug",
        "-p",
        "--dither",
        "--prep_mode",
        "yuv",
        "--weight_u",
        "1",
        "--weight_v",
        "0.5",
    ],
    input=bmps.encode(),
)
shutil.copy("/nuvie/nuviemaker0.1e.prg", "/work")
subprocess.check_call(
    ["/usr/bin/dd", "if=/dev/zero", "of=%s" % reu, "bs=1024", "count=%u" % reusize]
)
x64 = subprocess.Popen(
    [
        "/usr/local/bin/x64sc",
        "-console",
        "-fs8",
        wd,
        "-remotemonitor",
        "-warp",
        "-device8",
        "1",
        "-virtualdev8",
        "-drive8type",
        "1541",
        "+drive8truedrive",
        "-reu",
        "-reusize",
        str(reusize),
        "-reuimage",
        reu,
        "-reuimagerw",
        "-reu",
    ]
)

mon = None
for i in range(5):
    try:
        mon = pexpect.spawn("%s localhost 6510" % telnet, timeout=30)
        mon.expect("Connected")
        break
    except pexpect.exceptions.EOF:
        time.sleep(1)
mon.sendline("")

for ct in commands:
    c, t = ct
    for i in c:
        result = mon.expect([p, pexpect.TIMEOUT], timeout=t)
        if result != 0:
            raise ValueError
        print(i)
        mon.sendline(i)
        if result != 0:
            raise ValueError
    mon.sendline("exit")
    result = mon.expect([p, pexpect.TIMEOUT], timeout=t)

mon.expect([p, pexpect.TIMEOUT])
mon.sendline("quit")
mon.expect(["closed", pexpect.TIMEOUT])
mon.close()

x64.communicate()
