import os
import sys
import subprocess

def build():
    print("🚀 Starting TrueFace Desktop App Build...")
    
    # 1. Base command
    cmd = [
        "pyinstaller",
        "--name=TrueFace",
        "--windowed", # No console window
        "--noconfirm", # Overwrite existing dist
        "--clean",
        "--add-data=trueface:trueface", # Include source package
        "main.py"
    ]
    
    # 2. Add icon if it exists (optional)
    # cmd.append("--icon=assets/icon.icns")
    
    print(f"📦 Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build Successful!")
        print(f"📂 You can find your app in: {os.path.abspath('dist/TrueFace')}")
        if sys.platform == 'darwin':
            print(f"📱 macOS App Bundle: {os.path.abspath('dist/TrueFace.app')}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build Failed: {e}")

if __name__ == "__main__":
    build()
