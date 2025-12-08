#!/bin/bash
set -e # Exit on error

# Ensure we are using the local code
export PYTHONPATH=$PYTHONPATH:$(pwd)

CMD="python3 -m mage2gen.app"
MODULE_NAME="ComprehensiveTest"
TEST_OUTPUT="test_output_comprehensive"

# 1. Cleanup
echo "🧹 Cleaning up previous test output..."
rm -rf "$TEST_OUTPUT"
mkdir "$TEST_OUTPUT"

echo "🚀 Starting Comprehensive Test Module Generation..."

# 2. Initialize Module
echo "📦 [1/30] Creating Module..."
$CMD module \
    --package Mage2Gen \
    --name "$MODULE_NAME" \
    --description "Comprehensive Test Module for Mage2Gen 3.2 - Testing all features" \
    --output-dir "$TEST_OUTPUT"

# 3. Generate Admin CRUD (The Meta-Snippet)
echo "🛠️ [2/30] Generating Admin CRUD (Product)..."
$CMD admin-crud \
    --package Mage2Gen \
    --module "$MODULE_NAME" \
    --name Product \
    --fields "name:text,sku:text,price:decimal,qty:int,is_active:boolean" \
    --output-dir "$TEST_OUTPUT"

# 4. Generate Advanced System Config
echo "⚙️ [3/30] Generating System Configuration..."

# 4a. Boolean Toggle with Tab Creation
$CMD system \
    --package Mage2Gen --module "$MODULE_NAME" \
    --tab general_config --section general --group settings --field enabled \
    --type select --default 1 --create-tab \
    --output-dir "$TEST_OUTPUT"

# 4b. Color Picker
$CMD system \
    --package Mage2Gen --module "$MODULE_NAME" \
    --tab general_config --section general --group design --field primary_color \
    --type color \
    --output-dir "$TEST_OUTPUT"

# 4c. Image Upload
$CMD system \
    --package Mage2Gen --module "$MODULE_NAME" \
    --tab general_config --section general --group design --field logo \
    --type image \
    --output-dir "$TEST_OUTPUT"

# 4d. Email Template Field
$CMD system \
    --package Mage2Gen --module "$MODULE_NAME" \
    --tab general_config --section email --group notifications --field welcome_email \
    --type email \
    --output-dir "$TEST_OUTPUT"

# 5. Generate Dynamic Row
echo "📊 [4/30] Generating Dynamic Rows..."
$CMD system-dynamic \
    --package Mage2Gen --module "$MODULE_NAME" \
    --tab general_config --section social --group links --field social_links \
    --columns "network:Network Name,url:Profile URL,icon:Icon Class" \
    --output-dir "$TEST_OUTPUT"

# 6. Generate API Endpoint
echo "🔌 [5/30] Generating REST API..."
$CMD api \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name GetProducts \
    --method GET \
    --output-dir "$TEST_OUTPUT"

# 7. Generate Observer
echo "👀 [6/30] Generating Observer..."
$CMD observer \
    --package Mage2Gen --module "$MODULE_NAME" \
    --event catalog_product_save_after \
    --scope frontend \
    --output-dir "$TEST_OUTPUT"

# 8. Generate Plugin
echo "🔌 [7/30] Generating Plugin..."
$CMD plugin \
    --package Mage2Gen --module "$MODULE_NAME" \
    --target-class "Magento\\Catalog\\Model\\Product" \
    --method getName \
    --type after \
    --sort-order 10 \
    --output-dir "$TEST_OUTPUT"

# 9. Generate Console Command
echo "💻 [8/30] Generating Console Command..."
$CMD console \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name "mage2gen:test:run" \
    --description "Test console command" \
    --output-dir "$TEST_OUTPUT"

# 10. Generate Cron Job
echo "⏰ [9/30] Generating Cron Job..."
$CMD cronjob \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name "cleanup_logs" \
    --schedule "0 2 * * *" \
    --group default \
    --output-dir "$TEST_OUTPUT"

# 11. Generate Helper
echo "🛠️ [10/30] Generating Helper..."
$CMD helper \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name Data \
    --output-dir "$TEST_OUTPUT"

# 12. Generate Logger
echo "📝 [11/30] Generating Logger..."
$CMD logger \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name TestLogger \
    --filename "test_module.log" \
    --output-dir "$TEST_OUTPUT"

# 13. Generate Widget
echo "🎯 [12/30] Generating Widget..."
$CMD widget \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name FeaturedProducts \
    --field limit \
    --type text \
    --output-dir "$TEST_OUTPUT"

# 14. Generate Unit Test
echo "🧪 [13/30] Generating Unit Test..."
$CMD unit-test \
    --package Mage2Gen --module "$MODULE_NAME" \
    --suite Product \
    --name testSave \
    --output-dir "$TEST_OUTPUT"

# 15. Generate GraphQL Endpoint
echo "🕸️ [14/30] Generating GraphQL Endpoint..."
$CMD graphql \
    --package Mage2Gen --module "$MODULE_NAME" \
    --type Query \
    --name getTestData \
    --output-dir "$TEST_OUTPUT"

# 16. Generate Product Attribute
echo "🏷️ [15/30] Generating Product Attribute..."
$CMD product-attribute \
    --package Mage2Gen --module "$MODULE_NAME" \
    --code "test_attribute" \
    --label "Test Attribute" \
    --input-type "select" \
    --sort-order 100 \
    --output-dir "$TEST_OUTPUT"

# 17. Generate Category Attribute
echo "🗂️ [16/30] Generating Category Attribute..."
$CMD category-attribute \
    --package Mage2Gen --module "$MODULE_NAME" \
    --code "test_category_attr" \
    --label "Test Category Attribute" \
    --input-type "text" \
    --output-dir "$TEST_OUTPUT"

# 18. Generate Customer Attribute
echo "👤 [17/30] Generating Customer Attribute..."
$CMD customer-attribute \
    --package Mage2Gen --module "$MODULE_NAME" \
    --code "test_customer_attr" \
    --label "Test Customer Attribute" \
    --input-type "text" \
    --customer-forms "adminhtml_customer,customer_account_create" \
    --output-dir "$TEST_OUTPUT"

# 19. Generate Product Type
echo "📦 [18/30] Generating Product Type..."
$CMD product-type \
    --package Mage2Gen --module "$MODULE_NAME" \
    --code "test_product_type" \
    --label "Test Product Type" \
    --output-dir "$TEST_OUTPUT"

# 20. Generate Payment Method
echo "💳 [19/30] Generating Payment Method..."
$CMD payment \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name "Test Payment" \
    --output-dir "$TEST_OUTPUT"

# 21. Generate Shipping Method
echo "🚚 [20/30] Generating Shipping Method..."
$CMD shipping \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name "Test Shipping" \
    --output-dir "$TEST_OUTPUT"

# 22. Generate EAV Entity
echo "🏗️ [21/30] Generating EAV Entity..."
$CMD eav-entity \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name TestEntity \
    --output-dir "$TEST_OUTPUT"

# 23. Generate Controller (Frontend)
# FIX: Removed '--admin false'. Default is false, simply omitting it works.
echo "🎮 [22/30] Generating Frontend Controller..."
$CMD controller \
    --package Mage2Gen --module "$MODULE_NAME" \
    --frontname "test" \
    --section "index" \
    --action "index" \
    --output-dir "$TEST_OUTPUT"

# 24. Generate Controller (Admin)
# FIX: Changed '--admin true' to just '--admin' flag.
echo "👔 [23/30] Generating Admin Controller..."
$CMD controller \
    --package Mage2Gen --module "$MODULE_NAME" \
    --frontname "test" \
    --section "admin" \
    --action "index" \
    --admin \
    --output-dir "$TEST_OUTPUT"

# 25. Generate Block with Template
echo "🧱 [24/30] Generating Block with Template..."
$CMD block \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name TestBlock \
    --layout-handle "test_index_index" \
    --reference "content" \
    --output-dir "$TEST_OUTPUT"

# 26. Generate Schema Patch
echo "🗃️ [25/30] Generating Schema Patch..."
$CMD schemapatch \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name "AddTestColumn" \
    --operation "custom" \
    --table "mage2gen_comprehensivetest_product" \
    --output-dir "$TEST_OUTPUT"

# 27. Generate Model (Separate from Admin CRUD)
echo "🏗️ [26/30] Generating Standalone Model..."
# FIX: Flags like --admin-grid are booleans, no need for values if we just want to enable them
$CMD model \
    --package Mage2Gen --module "$MODULE_NAME" \
    --name Review \
    --fields "title:text,content:text,rating:int" \
    --admin-grid \
    --admin-form \
    --api \
    --output-dir "$TEST_OUTPUT"

# 28. Generate Language Pack
echo "🌐 [27/30] Generating Language Pack..."
$CMD language \
    --package Mage2Gen --module "$MODULE_NAME" \
    --language "en_US" \
    --output-dir "$TEST_OUTPUT"

# 29. Use Python for snippets with CLI issues or not exposed via CLI
echo "🔧 [28/30] Generating additional features via Python API..."
python3 - <<EOF
import os
from mage2gen import Module
from mage2gen.snippets.cache import CacheSnippet
from mage2gen.snippets.messagequeue import MessageQueueSnippet
from mage2gen.snippets.viewmodel import ViewModelSnippet
from mage2gen.snippets.router import RouterSnippet
from mage2gen.snippets.companyattribute import CompanyAttributeSnippet

# Create module instance
module = Module("Mage2Gen", "$MODULE_NAME", "Comprehensive Test Module")

# Generate Company Attribute (FIXED: use correct parameters)
print("  → Generating Company Attribute...")
company_snippet = CompanyAttributeSnippet(module)
company_snippet.add(code="test_company_attr", label="Test Company Attribute")

# Generate Cache Configuration
print("  → Generating Cache Configuration...")
cache_snippet = CacheSnippet(module)
cache_snippet.add(name="test_cache", description="Test cache configuration")

# Generate Message Queue Configuration
print("  → Generating Message Queue Configuration...")
mq_snippet = MessageQueueSnippet(module)
mq_snippet.add(
    topic="mage2gen.test.topic",
    consumer="testConsumer",
    queue="mage2gen_test_queue",
    exchange="mage2gen_test_exchange",
    handler_method="processMessage",
    schema_type="string",
    generate_publisher=True
)

# Generate ViewModel
print("  → Generating ViewModel...")
vm_snippet = ViewModelSnippet(module)
vm_snippet.add(
    classname="TestViewModel",
    methodname="getMessage",
    layout_handle="test_index_index",
    reference_name="content"
)

# Generate Router
print("  → Generating Router...")
router_snippet = RouterSnippet(module)
router_snippet.add(routername="testrouter", adminhtml=False)

# Generate the module
module.generate_module("$TEST_OUTPUT")
EOF

# 30. Add final message and verification
echo "✅ [29/30] Generation complete. Running verification..."
echo ""
echo "✅✅✅ COMPREHENSIVE GENERATION COMPLETE! ✅✅✅"
echo ""
echo "Generated module: Mage2Gen_$MODULE_NAME"
echo "Output directory: $TEST_OUTPUT"
echo ""
echo "📊 Generation Summary:"
echo "======================"
echo "✓ 1 Base Module"
echo "✓ 1 Admin CRUD Feature (Product)"
echo "✓ 4 System Config Fields (Boolean, Color, Image, Email)"
echo "✓ 1 Dynamic Row Configuration"
echo "✓ 1 REST API Endpoint"
echo "✓ 1 Observer"
echo "✓ 1 Plugin"
echo "✓ 1 Console Command"
echo "✓ 1 Cron Job"
echo "✓ 1 Helper"
echo "✓ 1 Logger"
echo "✓ 1 Widget"
echo "✓ 1 Unit Test"
echo "✓ 1 GraphQL Endpoint"
echo "✓ 1 Product Attribute"
echo "✓ 1 Category Attribute"
echo "✓ 1 Customer Attribute"
echo "✓ 1 Company Attribute (via Python API)"
echo "✓ 1 Product Type"
echo "✓ 1 Payment Method"
echo "✓ 1 Shipping Method"
echo "✓ 1 EAV Entity"
echo "✓ 2 Controllers (Frontend & Admin)"
echo "✓ 1 Block with Template"
echo "✓ 1 Schema Patch"
echo "✓ 1 Standalone Model"
echo "✓ 1 Language Pack"
echo "✓ 1 Cache Configuration"
echo "✓ 1 Message Queue"
echo "✓ 1 ViewModel"
echo "✓ 1 Router"
echo ""
echo "Total: 29 distinct features generated!"
echo ""
echo "🔍 Verifying generated files..."

# Count generated files
echo "Counting generated files..."
TOTAL_FILES=$(find "$TEST_OUTPUT" -type f \( -name "*.php" -o -name "*.xml" -o -name "*.phtml" -o -name "*.csv" -o -name "*.js" -o -name "*.less" -o -name "*.graphqls" \) 2>/dev/null | wc -l)
echo "Total generated files: $TOTAL_FILES"

# List main directories
echo ""
echo "📁 Main Directories:"
find "$TEST_OUTPUT/Mage2Gen/$MODULE_NAME" -maxdepth 2 -type d 2>/dev/null | sort | sed 's|^|  |'

# Check for critical files
echo ""
echo "🔍 Checking critical files..."
BASE_PATH="$TEST_OUTPUT/Mage2Gen/$MODULE_NAME"

if [ -d "$BASE_PATH" ]; then
    CRITICAL_FILES=(
        "registration.php"
        "etc/module.xml"
    )
    
    for file in "${CRITICAL_FILES[@]}"; do
        if [ -f "$BASE_PATH/$file" ]; then
            echo "✓ $file"
        else
            echo "✗ $file (MISSING)"
        fi
    done
    
    # Check for common directories
    echo ""
    echo "📂 Checking generated directories:"
    DIRS_TO_CHECK=("Model" "Controller" "Block" "etc" "view" "Setup" "Api" "Ui" "Test")
    for dir in "${DIRS_TO_CHECK[@]}"; do
        if [ -d "$BASE_PATH/$dir" ]; then
            echo "✓ $dir/"
        else
            echo "○ $dir/ (not generated)"
        fi
    done
else
    echo "❌ ERROR: Module directory not found at $BASE_PATH"
fi

echo ""
echo "🎉 Comprehensive test module generation completed successfully!"
echo "The module includes examples of all major Mage2Gen 3.2 features."
echo ""
echo "To install this test module in Magento 2:"
echo "1. Copy to app/code: cp -r $TEST_OUTPUT/Mage2Gen /path/to/magento/app/code/"
echo "2. Run: bin/magento module:enable Mage2Gen_$MODULE_NAME"
echo "3. Run: bin/magento setup:upgrade"
echo ""
echo "Note: Some features may require Magento 2 B2B edition (Company Attribute)"
echo ""
echo "To run PHP CodeSniffer validation:"
echo "php ./phpcs.phar --standard=Magento2 $TEST_OUTPUT/Mage2Gen/$MODULE_NAME/"
