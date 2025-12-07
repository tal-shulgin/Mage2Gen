#!/bin/bash
set -e # Exit on error

# Ensure we are using the local code
export PYTHONPATH=$PYTHONPATH:$(pwd)

CMD="python3 -m mage2gen.app"

# 1. Cleanup
rm -rf test_output
mkdir test_output

# 2. Initialize Module
echo "🚀 [1/5] Creating Module..."
$CMD module \
    --package Mage2Gen \
    --name Blog \
    --description "V3.2 Verification Module" \
    --output-dir test_output

# 3. Generate Admin CRUD (The Meta-Snippet)
echo "🚀 [2/5] Generating Admin CRUD (Post)..."
$CMD admin-crud \
    --package Mage2Gen \
    --module Blog \
    --name Post \
    --fields "title:text,content:textarea,is_active:boolean,publish_date:date" \
    --output-dir test_output

# 4. Generate Advanced System Config
echo "🚀 [3/5] Generating System Configuration..."

# 4a. Boolean Toggle
$CMD system \
    --package Mage2Gen --module Blog \
    --tab blog_config --section general --group settings --field enabled \
    --type select --default 1 --create-tab \
    --output-dir test_output

# 4b. Color Picker
$CMD system \
    --package Mage2Gen --module Blog \
    --tab blog_config --section general --group design --field header_color \
    --type color \
    --output-dir test_output

# 4c. Image Upload
$CMD system \
    --package Mage2Gen --module Blog \
    --tab blog_config --section general --group design --field logo \
    --type image \
    --output-dir test_output

# 4d. Field Dependency
$CMD system \
    --package Mage2Gen --module Blog \
    --tab blog_config --section general --group design --field show_logo \
    --type select --default 1 \
    --depends "enabled:1" \
    --output-dir test_output

# 5. Generate Dynamic Row
echo "🚀 [4/5] Generating Dynamic Rows..."
$CMD system-dynamic \
    --package Mage2Gen --module Blog \
    --tab blog_config --section social --group links --field accounts \
    --columns "network:Network Name,url:Profile URL" \
    --output-dir test_output

# 6. Generate API Endpoint
echo "🚀 [5/5] Generating API..."
$CMD api \
    --package Mage2Gen --module Blog \
    --name GetLatestPost \
    --method GET \
    --output-dir test_output

echo "✅ Generation Complete. Verifying Artifacts..."