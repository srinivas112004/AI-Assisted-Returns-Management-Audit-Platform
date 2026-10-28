import hashlib
import json
import sys
from pathlib import Path

# Add backend directory
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.generator.generate import generate_dataset
from app.core.config import DATA_DIR

def get_dir_hashes(directory: Path):
    hashes = {}
    for f in sorted(directory.glob("*.*")):
        if f.suffix in [".csv", ".json"]:
            hasher = hashlib.sha256()
            with open(f, "rb") as fh:
                hasher.update(fh.read())
            hashes[f.name] = hasher.hexdigest()
    return hashes

def main():
    print("[*] --- REPRODUCIBILITY ACCEPTANCE TEST ---")
    starter_dir = DATA_DIR / "starter"
    
    print("[*] Pass 1: Generating starter dataset with seed 20261022...")
    res1 = generate_dataset(profile="starter", seed=20261022, export_files=True, save_to_db=True)
    hashes1 = get_dir_hashes(starter_dir)

    print("[*] Pass 2: Re-generating starter dataset with seed 20261022...")
    res2 = generate_dataset(profile="starter", seed=20261022, export_files=True, save_to_db=True)
    hashes2 = get_dir_hashes(starter_dir)

    print("\nComparing SHA-256 checksums across runs:")
    all_match = True
    for fname, h1 in hashes1.items():
        h2 = hashes2.get(fname)
        matches = (h1 == h2)
        if not matches:
            all_match = False
        status = "[MATCH]" if matches else "[MISMATCH]"
        print(f" {status} {fname}: {h1[:16]}... == {h2[:16] if h2 else 'MISSING'}...")

    if all_match:
        print("\n[SUCCESS] Deterministic reproducibility verified: 100% identical outputs and hashes!")
        sys.exit(0)
    else:
        print("\n[FAILURE] File checksum mismatch detected across identical seed runs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
