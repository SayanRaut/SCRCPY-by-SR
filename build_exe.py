"""
Build Script for SCRCPY by Sneak
Creates a clean, production-ready standalone Windows application bundle using PyInstaller.
"""

import os
import sys
import shutil
import subprocess

def main():
    print("=" * 65)
    print("  SCRCPY by Sneak - Automated Windows EXE Builder")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    build_dir = os.path.join(base_dir, "build")
    output_app_dir = os.path.join(dist_dir, "SCRCPY by Sneak")
    exe_target = os.path.join(output_app_dir, "SCRCPY by Sneak.exe")

    # 1. Check PyInstaller
    try:
        import PyInstaller
        print(f"[*] Detected PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("[*] PyInstaller not detected. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        import PyInstaller

    # 2. Verify essential assets
    icon_path = os.path.join(base_dir, "sneak.ico")
    png_path = os.path.join(base_dir, "sneak.png")
    scrcpy_src_dir = os.path.join(base_dir, "scrcpy")

    if not os.path.exists(icon_path):
        print("[-] ERROR: sneak.ico not found!")
        sys.exit(1)
    if not os.path.exists(scrcpy_src_dir):
        print("[-] ERROR: scrcpy/ engine directory not found!")
        sys.exit(1)

    print(f"[*] Base directory: {base_dir}")
    print(f"[*] Using Icon: {icon_path}")

    # 3. Clean prior build artifacts
    if os.path.exists(build_dir):
        print("[*] Cleaning build/ cache...")
        shutil.rmtree(build_dir, ignore_errors=True)

    # 4. Prepare PyInstaller arguments
    pyinstaller_args = [
        os.path.join(base_dir, "app.py"),
        "--name=SCRCPY by Sneak",
        "--onedir",
        "--noconsole",
        "--noconfirm",
        "--clean",
        f"--icon={icon_path}",
        # Add assets to bundle
        f"--add-data={icon_path};.",
        f"--add-data={png_path};.",
        # Hidden imports to prevent missing dependency errors
        "--hidden-import=qtawesome",
        "--hidden-import=PIL",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
    ]

    config_path = os.path.join(base_dir, "scrcpy_config.json")
    if os.path.exists(config_path):
        pyinstaller_args.append(f"--add-data={config_path};.")

    print("\n[*] Running PyInstaller compiler...")
    import PyInstaller.__main__
    PyInstaller.__main__.run(pyinstaller_args)

    # 5. Copy the scrcpy engine binaries and DLLs into dist/SCRCPY by Sneak/scrcpy/
    print("\n[*] Bundling Scrcpy engine binaries (scrcpy.exe, adb.exe, DLLs)...")
    scrcpy_dest_dir = os.path.join(output_app_dir, "scrcpy")
    if os.path.exists(scrcpy_dest_dir):
        shutil.rmtree(scrcpy_dest_dir, ignore_errors=True)

    def ignore_patterns(dir, files):
        # Ignore git, gradle, build scripts, documentation, and unneeded source trees
        ignored = []
        for f in files:
            if f in [".gradle", ".github", "__pycache__", "gradle", "server", "app", "doc", "release", "config", "assets"] or f.endswith((".py", ".gradle", ".sh", ".bat")):
                if f not in ["open_a_terminal_here.bat", "scrcpy-console.bat"]:
                    ignored.append(f)
        return ignored

    shutil.copytree(scrcpy_src_dir, scrcpy_dest_dir, ignore=ignore_patterns)
    print(f"[+] Successfully copied Scrcpy engine to: {scrcpy_dest_dir}")

    # 6. Ensure recordings directory exists
    rec_dest = os.path.join(output_app_dir, "recordings")
    os.makedirs(rec_dest, exist_ok=True)

    # 7. Copy sneak.ico and sneak.png to app root for direct access
    shutil.copy2(icon_path, output_app_dir)
    shutil.copy2(png_path, output_app_dir)
    if os.path.exists(config_path):
        shutil.copy2(config_path, output_app_dir)

    print("\n" + "=" * 65)
    if os.path.exists(exe_target):
        bundle_mb = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(output_app_dir) for f in fs) // (1024 * 1024)
        print("  [+] STANDALONE WINDOWS APP READY!")
        print(f"  Target Executable: {exe_target}")
        print(f"  Total Bundle Size: {bundle_mb} MB")
        print("=" * 65)

        # 8. Compile Inno Setup Installation Wizard (.exe)
        iss_file = os.path.join(base_dir, "installer.iss")
        if os.path.exists(iss_file):
            print("\n[*] Looking for Inno Setup compiler (ISCC)...")
            iscc_exe = shutil.which("iscc") or shutil.which("ISCC.exe")
            if not iscc_exe:
                candidates = [
                    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
                    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
                    r"C:\Program Files\Inno Setup 6\ISCC.exe",
                    r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
                    r"C:\Program Files\Inno Setup 5\ISCC.exe",
                ]
                for c in candidates:
                    if os.path.exists(c):
                        iscc_exe = c
                        break

            if iscc_exe:
                print(f"[+] Found Inno Setup: {iscc_exe}")
                print("[*] Compiling Installation Wizard EXE...")
                res = subprocess.run([iscc_exe, iss_file], cwd=base_dir)
                if res.returncode == 0:
                    out_dir = os.path.join(base_dir, "installer_output")
                    print("\n" + "=" * 65)
                    print("  [+] INSTALLATION WIZARD EXE CREATED SUCCESSFULLY!")
                    if os.path.exists(out_dir):
                        for f in os.listdir(out_dir):
                            if f.endswith(".exe"):
                                f_path = os.path.join(out_dir, f)
                                sz = os.path.getsize(f_path) / (1024 * 1024)
                                print(f"  Installer: {f_path} ({sz:.2f} MB)")
                    print("=" * 65)
                else:
                    print(f"[-] Inno Setup exited with code {res.returncode}")
            else:
                print("[-] Inno Setup compiler (ISCC.exe) not found. Skipping installer exe creation.")
    else:
        print("[-] Build finished but executable was not found at expected location.")
        print(f"[-] Check {output_app_dir}")

if __name__ == "__main__":
    main()

