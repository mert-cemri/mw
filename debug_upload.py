#!/usr/bin/env python3
"""
Debug script to help troubleshoot PyPI upload issues.
"""
import os
import subprocess
import sys

def check_twine_config():
    """Check twine configuration and credentials."""
    print("🔍 Debugging Twine Upload Issues")
    print("=" * 50)
    
    # Check if .pypirc exists
    pypirc_path = os.path.expanduser("~/.pypirc")
    if os.path.exists(pypirc_path):
        print("✅ Found ~/.pypirc file")
        try:
            with open(pypirc_path, 'r') as f:
                content = f.read()
                if '[testpypi]' in content:
                    print("✅ Found [testpypi] section in .pypirc")
                else:
                    print("❌ No [testpypi] section found in .pypirc")
                    
                if '__token__' in content:
                    print("✅ Found __token__ username")
                else:
                    print("❌ No __token__ username found")
                    
                if 'pypi-' in content:
                    print("✅ Found API token (starts with pypi-)")
                else:
                    print("❌ No API token found (should start with pypi-)")
        except Exception as e:
            print(f"❌ Error reading .pypirc: {e}")
    else:
        print("❌ No ~/.pypirc file found")
    
    # Check environment variables
    print("\n🔧 Environment Variables:")
    twine_vars = ['TWINE_USERNAME', 'TWINE_PASSWORD', 'TWINE_REPOSITORY']
    for var in twine_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                print(f"✅ {var} is set (hidden)")
            else:
                print(f"✅ {var} = {value}")
        else:
            print(f"⚠️  {var} not set")
    
    # Check twine version
    print("\n📦 Twine Version:")
    try:
        result = subprocess.run(['twine', '--version'], capture_output=True, text=True)
        print(f"✅ {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Error checking twine version: {e}")
    
    # Check dist files
    print("\n📁 Distribution Files:")
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        files = os.listdir(dist_dir)
        if files:
            print("✅ Found distribution files:")
            for f in files:
                file_path = os.path.join(dist_dir, f)
                size = os.path.getsize(file_path)
                print(f"   - {f} ({size} bytes)")
        else:
            print("❌ No files in dist/ directory")
    else:
        print("❌ No dist/ directory found")

def create_correct_pypirc():
    """Create a correctly formatted .pypirc file."""
    print("\n🛠️  Creating Correct .pypirc File")
    print("-" * 30)
    
    print("Please provide the following information:")
    
    # Get Test PyPI token
    test_token = input("Enter your Test PyPI API token (starts with pypi-): ").strip()
    if not test_token.startswith('pypi-'):
        print("⚠️  Token should start with 'pypi-'")
    
    # Optional: Get production PyPI token
    prod_token = input("Enter your Production PyPI API token (optional, press Enter to skip): ").strip()
    
    pypirc_content = f"""[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = {test_token}
"""
    
    if prod_token:
        pypirc_content += f"""
[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = {prod_token}
"""
    
    pypirc_path = os.path.expanduser("~/.pypirc")
    
    try:
        with open(pypirc_path, 'w') as f:
            f.write(pypirc_content)
        
        # Set correct permissions
        os.chmod(pypirc_path, 0o600)
        
        print(f"✅ Created {pypirc_path}")
        print("✅ Set file permissions to 600")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .pypirc: {e}")
        return False

def test_upload_command():
    """Suggest the correct upload command."""
    print("\n🚀 Recommended Upload Commands")
    print("-" * 30)
    
    print("For Test PyPI:")
    print("twine upload --repository testpypi dist/*")
    print("OR")
    print("twine upload -r testpypi dist/*")
    
    print("\nFor Production PyPI:")
    print("twine upload dist/*")
    
    print("\n💡 Debug Tips:")
    print("1. Make sure you created the token on test.pypi.org (not pypi.org)")
    print("2. Token should have 'Entire account' scope")
    print("3. Try clearing cache: rm -rf ~/.cache/pip/http*")
    print("4. Use --verbose flag to see detailed error messages")

def main():
    """Main debug function."""
    check_twine_config()
    
    print("\n" + "=" * 50)
    response = input("Would you like me to create a correct .pypirc file? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        if create_correct_pypirc():
            print("\n✅ Configuration updated!")
        else:
            print("\n❌ Configuration failed!")
    
    test_upload_command()
    
    print("\n🔍 Next Steps:")
    print("1. Verify your token is from https://test.pypi.org/manage/account/token/")
    print("2. Run: twine upload --repository testpypi dist/* --verbose")
    print("3. If still failing, try: twine upload --repository testpypi dist/* --non-interactive")

if __name__ == "__main__":
    main()