import os
import sys

BASE_DIR = "test_output/Mage2Gen/Blog"

def check_file(path, must_contain=None):
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(full_path):
        print(f"❌ MISSING: {path}")
        sys.exit(1)
    
    if must_contain:
        with open(full_path, 'r') as f:
            content = f.read()
            if must_contain not in content:
                print(f"❌ INVALID CONTENT in {path}")
                print(f"   Expected: '{must_contain}'")
                sys.exit(1)
    print(f"✅ OK: {path}")

# 1. Check Module
check_file("registration.php", "Mage2Gen_Blog")

# 2. Check Admin CRUD
check_file("Model/Post.php", "class Post extends AbstractModel")
check_file("etc/db_schema.xml", '<table name="mage2gen_blog_post"')
check_file("Controller/Adminhtml/Post/Save.php", "class Save extends")

# 3. Check Advanced Config
check_file("Model/Config/Backend/LogoImage.php", "extends \Magento\Config\Model\Config\Backend\Image")
check_file("Block/Adminhtml/System/Config/Field/HeaderColorColor.php", "ColorPicker")

# 4. Check Dependencies
check_file("etc/adminhtml/system.xml", '<depends><field id="enabled">1</field></depends>')

# 5. Check Dynamic Rows
check_file("Block/Adminhtml/System/Config/Field/AccountsRow.php", "addColumn('network'")
check_file("etc/adminhtml/system.xml", "ArraySerialized")

print("\n🎉 SUCCESS: All A-Z Scenarios Passed!")