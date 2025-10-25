#!/usr/bin/env python3.11
"""
Python Version Checker for Resume Builder Backend
This script checks if Python 3.11+ is available and provides installation guidance
"""

import sys
import subprocess
import platform

def check_python_version():
    """Check if Python 3.11+ is available"""
    print("🐍 Python Version Checker for Resume Builder Backend")
    print("=" * 60)
    
    # Check current Python version
    current_version = sys.version_info
    print(f"Current Python version: {current_version.major}.{current_version.minor}.{current_version.micro}")
    
    if current_version >= (3, 11):
        print("✅ Python 3.11+ detected! You're good to go.")
        return True
    else:
        print("❌ Python 3.11+ is required for this project.")
        print(f"   Current version: {current_version.major}.{current_version.minor}.{current_version.micro}")
        return False

def check_python_311_available():
    """Check if python3.11 command is available"""
    try:
        result = subprocess.run(['python3.11', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ python3.11 command available: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ python3.11 command not found")
    return False

def get_installation_instructions():
    """Provide installation instructions based on the operating system"""
    system = platform.system().lower()
    
    print("\n📥 Installation Instructions:")
    print("=" * 40)
    
    if system == "windows":
        print("Windows:")
        print("1. Download Python 3.11+ from: https://www.python.org/downloads/")
        print("2. During installation, check 'Add Python to PATH'")
        print("3. Or use Windows Store: 'python' in Microsoft Store")
        print("4. Or use Chocolatey: choco install python311")
        
    elif system == "darwin":  # macOS
        print("macOS:")
        print("1. Using Homebrew: brew install python@3.11")
        print("2. Using pyenv: pyenv install 3.11.0 && pyenv global 3.11.0")
        print("3. Download from: https://www.python.org/downloads/macos/")
        
    elif system == "linux":
        print("Linux:")
        print("Ubuntu/Debian:")
        print("  sudo apt update")
        print("  sudo apt install python3.11 python3.11-venv python3.11-pip")
        print("\nCentOS/RHEL/Fedora:")
        print("  sudo dnf install python3.11 python3.11-pip")
        print("\nArch Linux:")
        print("  sudo pacman -S python311")
        
    else:
        print("Unknown operating system. Please visit:")
        print("https://www.python.org/downloads/")

def main():
    """Main function"""
    has_correct_version = check_python_version()
    
    if not has_correct_version:
        print("\n" + "=" * 60)
        check_python_311_available()
        get_installation_instructions()
        
        print("\n💡 After installing Python 3.11+:")
        print("   1. Restart your terminal/command prompt")
        print("   2. Run this script again to verify")
        print("   3. Then proceed with backend setup")
        
        return False
    
    print("\n🎉 Python version check passed!")
    print("   You can now proceed with the backend setup:")
    print("   cd backend && python -m venv venv && source venv/bin/activate")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
