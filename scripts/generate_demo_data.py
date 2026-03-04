"""Write synthetic 1925-1935 data to data/ for demo. Replace with real data for research."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.data_prep import generate_synthetic_data, DATA_DIR

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    macro, market = generate_synthetic_data()
    macro.to_csv(DATA_DIR / "macro_1925_1935.csv", index=False)
    market.to_csv(DATA_DIR / "dow_1925_1935.csv", index=False)
    print("Wrote", DATA_DIR / "macro_1925_1935.csv", DATA_DIR / "dow_1925_1935.csv")

if __name__ == "__main__":
    main()
