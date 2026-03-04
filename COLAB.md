# How to Run This Project on Google Colab

Two options: **Google Drive** (no GitHub) or **GitHub** (if you’ve pushed the repo).

The notebook includes **Section 8 (Advanced):** CUSUM, Newey–West HAC, VAR + Granger + IRF, placebo event study, and DiD. Ensure your project has **`src/data_prep.py`** and **`src/advanced_analysis.py`** so Section 8 runs.

---

## Option 1: Using Google Drive

### 1. Put the project on Drive

1. **Zip** your `Quant` folder. Include:
   - **`src/`** (both `data_prep.py` and `advanced_analysis.py`)
   - **`data/`** (can be empty; synthetic data will be generated)
   - **`notebooks/smoot_hawley_analysis.ipynb`**
   - **`requirements.txt`**
2. **Upload** the zip to **Google Drive** (e.g. **My Drive**).
3. **Unzip** (double‑click zip → “Open with Google Drive” or “Extract”) so you have:
   ```
   My Drive/Quant/
   ├── src/
   │   ├── data_prep.py
   │   └── advanced_analysis.py
   ├── data/
   ├── notebooks/
   │   └── smoot_hawley_analysis.ipynb
   ├── requirements.txt
   ├── README.md
   └── COLAB.md
   ```

### 2. Open in Colab

1. Go to **[colab.research.google.com](https://colab.research.google.com)**.
2. **File → Open notebook → Google Drive**.
3. Open **`Quant/notebooks/smoot_hawley_analysis.ipynb`**.

### 3. Run the first code cell

The **first code cell** (Section 3 – Data) is Colab‑aware. It will:

- Detect Colab and mount Google Drive.
- Ask for Drive access (click **Connect to Google Drive** when prompted).
- Set the project root to `/content/drive/MyDrive/Quant` (or your path).
- Install dependencies with `pip`.

If your project is **not** in `My Drive/Quant`, edit this line in that cell:

```python
ROOT = Path("/content/drive/MyDrive/Quant")  # e.g. .../MyDrive/MyProjects/Quant
```

Then run **Run all** or run each cell from top to bottom. The notebook runs Sections 1–7 (core + discussion) and **Section 8 (Advanced)** — CUSUM, HAC, VAR, placebo, DiD — so keep `src/advanced_analysis.py` in your project.

---

## Option 2: Using GitHub

### 1. Push the project to GitHub

(If you haven’t already.)

```bash
cd Quant
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/Quant.git
git push -u origin main
```

### 2. Open in Colab from GitHub

1. Go to **[colab.research.google.com](https://colab.research.google.com)**.
2. **File → Open notebook → GitHub**.
3. Enter: `YOUR_USERNAME/Quant` and pick the repo (or paste the repo URL).

Or open this URL (replace `USER` and `REPO`):

```
https://colab.research.google.com/github/USER/REPO/blob/main/notebooks/smoot_hawley_analysis.ipynb
```

### 3. Clone the repo in the first cell

When you open from GitHub, Colab only has the **single notebook file**, not `src/` or `data/`. So the first code cell must **clone the repo** and then set the path. Use this as your **first code cell** (replace the existing first code cell with this):

```python
# Clone repo (only needed when opening from GitHub)
!git clone https://github.com/YOUR_USERNAME/Quant.git /content/Quant
import sys
from pathlib import Path
ROOT = Path("/content/Quant")
sys.path.insert(0, str(ROOT))

# Install dependencies
!pip install -q pandas numpy scipy matplotlib seaborn statsmodels

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from src.data_prep import prepare_analysis_dataset, generate_synthetic_data, DATA_DIR
```

Replace `YOUR_USERNAME` with your GitHub username. Then run the rest of the notebook. Data will be generated if `data/` is empty (synthetic data). Section 8 (Advanced) will run because the clone brings `src/advanced_analysis.py`.

---

## Quick reference

| Step | Drive | GitHub |
|------|--------|--------|
| 1 | Upload zip to Drive → unzip to `Quant/` | Push repo to GitHub |
| 2 | Open notebook from Drive in Colab | Open notebook from GitHub in Colab |
| 3 | Run first cell (mount Drive, set `ROOT`) | Run first cell (clone repo, set `ROOT`, pip install) |
| 4 | Run all cells | Run all cells |

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'src'`**  
  Ensure the first code cell has run and `ROOT` points to the folder that contains `src/`. Then `sys.path.insert(0, str(ROOT))` must run before `from src.data_prep import ...`.

- **`ModuleNotFoundError: No module named 'src.advanced_analysis'`**  
  Your project must include **`src/advanced_analysis.py`** (advanced version). Re-zip and upload so `Quant/src/` has both `data_prep.py` and `advanced_analysis.py`. If you opened from GitHub, clone the full repo so Section 8 runs.

- **`FileNotFoundError: ... macro_1925_1935.csv`**  
  The notebook will create **synthetic** data if the file is missing. If you use Drive, ensure `data/` is inside your `Quant` folder so `DATA_DIR` (or `ROOT / "data"`) exists.

- **Drive path different**  
  If your project is in a subfolder (e.g. `My Drive/Projects/Quant`), set:
  `ROOT = Path("/content/drive/MyDrive/Projects/Quant")`.
