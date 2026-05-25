# fix_kernelspec.py
import nbformat
from pathlib import Path

notebook_paths = [
    "notebooks/scriptsEtTests.ipynb",
    "notebooks/coherencedata.ipynb"
]

for path in notebook_paths:
    nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
    nb["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    }
    nbformat.write(nb, path)
    print(f"✅ Kernelspec corrigé dans : {path}")
