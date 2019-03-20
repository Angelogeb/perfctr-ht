import os

dir_name = "data/"

def process_stderr(stderr_files, marker):
    for f in stderr_files:
        with open(f,"r+") as fd:
            lines = fd.readlines()
            fd.seek(0)
            for line in lines:
                if marker not in line:
                    fd.write(line)
            fd.truncate()


def process_stdout(stdout_files):
    for f in stdout_files:
        with open(f,"r+") as fd:
            header = f.replace(".stdout", ".header")
            with open(header, "w") as h:
                lines = fd.readlines()
                fd.seek(0)
                for line in lines:
                    if not line.startswith("# "):
                        fd.write(line)
                    else:
                        h.write(line)
                fd.truncate()



files = os.listdir(dir_name)
stdout_files = [os.path.join(dir_name, f) for f in files if f.endswith(".stdout")]
stderr_files = [os.path.join(dir_name, f) for f in files if f.endswith(".stderr")]

process_stdout(stdout_files)
process_stderr(stderr_files, "Marker")