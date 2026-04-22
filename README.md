# Erdstall Local Pipeline

A lightweight standalone Python pipeline for processing 3D `.ply` meshes locally.  
This version is independent of Django and can be easily shared and executed on any machine.

---

## What this project does

This pipeline enables a simple local workflow for 3D cave / tunnel meshes:

1. Import a raw `.ply` mesh  
2. Generate a repaired mesh using **Screened Poisson Reconstruction**  
3. Detect and export mesh patches  
4. Finalize a clean mesh and generate a lightweight mobile version  

---

## Example Workflow

original.ply → repaired_mesh.ply → patches → mesh.ply + mesh_mobile.ply

---

## Project Structure
After Pipeline run
```text
erdstall_local_pipeline/  
├─ data/  
│  └─ ply/  
│     └─ ERDSTALL_001/  
│        ├─ original.ply  
│        ├─ repaired_mesh.ply  
│        ├─ mesh.ply  
│        ├─ mesh_mobile.ply  
│        ├─ patches.json  
│        └─ patches/  
│           ├─ patch_0.ply  
│           └─ ...  
├─ erdstall_pipeline/  
├─ main.py  
└─ requirements.txt  
```
---

# Installation

## 1. Install Python

You need **Python 3.10 or 3.11**.

### Windows (recommended – using winget)

Open **PowerShell** and run:
```bash
winget install Python.Python.3.11
```

---

## 2. Install Java (Required for Fiji / ImageJ)

You need **Java 17 or newer**.

### Windows (recommended – using winget)

Open **PowerShell** and run:

```bash
winget install EclipseAdoptium.Temurin.17.JDK

## 2. Install Visual Studio Code

Visual Studio Code is recommended for working with this project.

### Install using winget

In PowerShell, run:
```bash
winget install Microsoft.VisualStudioCode
```
---

## 3. Set up the project

### Windows
```bash
py -3.11 -m venv .venv311
```
```bash
.venv311\Scripts\activate  
```
```bash
pip install -r requirements.txt  
```
### macOS / Linux
```bash
python3 -m venv .venv  
```
```bash
source .venv/bin/activate  
```
```bash
pip install -r requirements.txt  
```

---

# Usage

## 1. Initialize a new mesh project
```bash
python main.py init ERDSTALL_001 --input "C:\path\to\your\file.ply" ---textures "C:\path\to\your\texture_folder"
```
This creates:

data/ply/ERDSTALL_001/original.ply  

---

## 2. Generate repaired mesh
```bash
python main.py fill ERDSTALL_001
```
Output:

data/ply/ERDSTALL_001/repaired_mesh.ply  

---

## 3. Detect patches
```bash
python main.py patches ERDSTALL_001
```
Outputs:

data/ply/ERDSTALL_001/patches/  
data/ply/ERDSTALL_001/patches.json  

---

## 4. Finalize mesh

### Without removing patches
```bash
python main.py finalize ERDSTALL_001  
```
### With selected patches removed

python main.py finalize ERDSTALL_001 --unused-patch patch_0.ply --unused-patch patch_3.ply  

Outputs:

data/ply/ERDSTALL_001/mesh.ply  
data/ply/ERDSTALL_001/mesh_mobile.ply  

---

# Important Notes (Cave / Tunnel Scans)

This pipeline uses **Screened Poisson Reconstruction**, which may cause:

- Blobby surfaces  
- Closed tunnels  
- Loss of interior structure  

# Configuration

Configuration file:

erdstall_pipeline/config.py  

### Default parameters:

depth = 9  
samplespernode = 2.0  
pointweight = 2  

These are tuned for safer cave reconstruction.

---

# Faster Workflow (Optional)

If you already have a clean mesh:

1. Place it into the project folder  
2. Rename it to: mesh.ply  
3. Skip reconstruction  
4. Run only mesh reduction  

This significantly reduces processing time.

---

# Requirements

Install dependencies with:

pip install -r requirements.txt  

---

# Tips

- Large `.ply` files (500MB–1GB) can take minutes to hours depending on CPU  
- Fewer CPU cores = slower processing  
- Pre-cleaning meshes in MeshLab can greatly speed up processing  

---