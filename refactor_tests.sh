#!/bin/bash

# 1. Create Directories
echo "📁 Creating directory structure..."
mkdir -p tests/unit
mkdir -p tests/integration

# 2. Move Unit Tests
echo "🚚 Moving Unit Tests..."
# Move all test_snippet_*.py files
mv tests/test_snippet_*.py tests/unit/ 2>/dev/null
# Move core tests
mv tests/test_cli.py tests/unit/ 2>/dev/null
mv tests/test_feature_*.py tests/unit/ 2>/dev/null
mv tests/test_php.py tests/unit/ 2>/dev/null
mv tests/test_schema.py tests/unit/ 2>/dev/null
mv tests/test_template.py tests/unit/ 2>/dev/null

# 3. Create Init files
touch tests/unit/__init__.py
touch tests/integration/__init__.py

# 4. Cleanup
echo "🧹 Cleaning up..."
# Remove the old context.py if it exists
rm -f tests/context.py

echo "✅ Refactor Complete."
echo "   - Unit tests are in tests/unit/"
echo "   - Integration tests are in tests/integration/"