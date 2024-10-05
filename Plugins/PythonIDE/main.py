import os
import subprocess
import platform

def find_python():
    system_type = platform.system()

    if system_type == "Windows":
        return find_python_windows()
    elif system_type in ("Linux", "Darwin"):  # macOS == Darwin
        return find_python_unix()
    else:
        return None, None

def find_python_windows():
    paths = os.environ["PATH"].split(os.pathsep)
    for path in paths:
        python_exe = os.path.join(path, "python.exe")
        if os.path.exists(python_exe):
            try:
                version = subprocess.check_output([python_exe, "--version"], stderr=subprocess.STDOUT).decode().strip()
                return python_exe, version
            except subprocess.SubprocessError:
                continue
    return None, None

def find_python_unix():
    try:
        python_path = subprocess.check_output(["which", "python3"]).decode().strip()
        if python_path:
            version = subprocess.check_output([python_path, "--version"]).decode().strip()
            return python_path, version
    except subprocess.CalledProcessError:
        pass

    try:
        python_path = subprocess.check_output(["which", "python"]).decode().strip()
        if python_path:
            version = subprocess.check_output([python_path, "--version"]).decode().strip()
            return python_path, version
    except subprocess.CalledProcessError:
        pass

    return None, None

# Пример использования:
python_path, python_version = find_python()
if python_path:
    print(f"Python найден по пути: {python_path} с версией {python_version}")
else:
    print("Python не найден")
