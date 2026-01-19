# Zelda CG

## Como rodar

**Python 3.10+** e **pip** necessários.

### Windows

```cmd
cd zelda-cg
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Se der erro com PyOpenGL, comente a linha `os.environ['PYOPENGL_PLATFORM'] = 'x11'` em `main.py`.

### Linux / WSL

```bash
# dependências (Ubuntu/Debian)
sudo apt install python3 python3-venv libglfw3 libgl1-mesa-glx libglu1-mesa

# rodar
cd zelda-cg
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

No WSL: use **WSLg** (Windows 11) ou um servidor X (ex. VcXsrv) no Windows.

---

**Controles:** WASD — mover | ESC — sair
