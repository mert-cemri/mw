#!/bin/bash

echo "🔧 Setting up .pypirc for PyPI uploads"
echo "======================================"

# Check if .pypirc already exists
if [ -f ~/.pypirc ]; then
    echo "⚠️  ~/.pypirc already exists"
    echo "Creating backup as ~/.pypirc.backup"
    cp ~/.pypirc ~/.pypirc.backup
fi

echo ""
echo "📝 Please provide your API tokens:"
echo ""
echo "1. Test PyPI Token:"
echo "   - Go to: https://test.pypi.org/manage/account/token/"
echo "   - Create token with 'Entire account' scope"
echo "   - Copy the full token (starts with pypi-)"
echo ""
read -p "Enter your Test PyPI token: " TEST_TOKEN

echo ""
echo "2. Production PyPI Token (optional - press Enter to skip):"
echo "   - Go to: https://pypi.org/manage/account/token/"
echo "   - Create token with 'Entire account' scope"
echo ""
read -p "Enter your Production PyPI token (optional): " PROD_TOKEN

echo ""
echo "📄 Creating ~/.pypirc file..."

# Create the .pypirc file
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = $TEST_TOKEN

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = $PROD_TOKEN
EOF

# Set correct permissions
chmod 600 ~/.pypirc

echo "✅ Created ~/.pypirc with correct permissions"
echo ""

# Verify the file
echo "🔍 Verifying configuration:"
if [ -f ~/.pypirc ]; then
    echo "✅ File exists"
    
    if grep -q "testpypi" ~/.pypirc; then
        echo "✅ Test PyPI configuration found"
    fi
    
    if grep -q "__token__" ~/.pypirc; then
        echo "✅ Token authentication configured"
    fi
    
    if grep -q "pypi-" ~/.pypirc; then
        echo "✅ API token format detected"
    fi
    
    # Check permissions
    PERMS=$(stat -c "%a" ~/.pypirc 2>/dev/null || stat -f "%A" ~/.pypirc 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        echo "✅ Correct file permissions (600)"
    else
        echo "⚠️  File permissions: $PERMS (should be 600)"
    fi
fi

echo ""
echo "🚀 Ready to upload! Try these commands:"
echo ""
echo "For Test PyPI:"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "For Production PyPI:"
echo "  twine upload dist/*"
echo ""
echo "💡 If you still get 403 errors:"
echo "1. Verify your token is from test.pypi.org (not pypi.org)"
echo "2. Make sure token has 'Entire account' scope"
echo "3. Try: twine upload --repository testpypi dist/* --verbose"