#!/bin/bash
set -e

export PYTHONPATH=$PYTHONPATH:$(pwd)
CMD="python3 -m mage2gen.app"
MODULE_NAME="ConfigFullSpec"
TEST_OUTPUT="test_config_spec"

# 1. Cleanup
echo "🧹 Cleaning up..."
rm -rf "$TEST_OUTPUT"
mkdir "$TEST_OUTPUT"

# 2. Init Module
echo "🚀 Creating Module..."
$CMD module --package Mage2Gen --name "$MODULE_NAME" --description "Full System Config Spec" --output-dir "$TEST_OUTPUT"

# 3. Test Field with Tooltip and Frontend Class
echo "⚙️  Generating Field 1: Tooltip & CSS Class"
$CMD system \
    --package Mage2Gen --module "$MODULE_NAME" \
    --tab general --section spec --group features --field feature_a \
    --type text \
    --create-tab \
    --tooltip "This is a helpful tooltip" \
    --frontend-class "custom-css-class" \
    --output-dir "$TEST_OUTPUT"

# 4. Test Field with canRestore and custom Config Path
echo "⚙️  Generating Field 2: canRestore & Config Path"
$CMD system \
    --package Mage2Gen --module "$MODULE_NAME" \
    --tab general --section spec --group features --field feature_b \
    --type select \
    --can-restore \
    --config-path "custom/path/to/value" \
    --output-dir "$TEST_OUTPUT"

# 5. Test Field with if_module_enabled
echo "⚙️  Generating Field 3: Module Dependency"
$CMD system \
    --package Mage2Gen --module "$MODULE_NAME" \
    --tab general --section spec --group features --field feature_c \
    --type text \
    --if-module-enabled "Magento_Checkout" \
    --output-dir "$TEST_OUTPUT"

# 6. Verify Output
echo ""
echo "🔍 Verifying generated XML..."
XML_FILE="$TEST_OUTPUT/Mage2Gen/$MODULE_NAME/etc/adminhtml/system.xml"

if [ ! -f "$XML_FILE" ]; then
    echo "❌ Error: system.xml not found!"
    exit 1
fi

# Function to check string in file
check_str() {
    if grep -q "$1" "$XML_FILE"; then
        echo "✅ Found: $1"
    else
        echo "❌ Missing: $1"
        # Print file content for debugging if check fails
        echo "--- FILE CONTENT ---"
        cat "$XML_FILE"
        echo "--------------------"
        exit 1
    fi
}

check_str '<tooltip>This is a helpful tooltip</tooltip>'
check_str 'frontend_class="custom-css-class"'
check_str 'canRestore="1"'
check_str 'config_path="custom/path/to/value"'
check_str '<if_module_enabled>Magento_Checkout</if_module_enabled>'

echo ""
echo "🎉 All Store Config specifications verified successfully!"