#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess

# Ensure we can import mage2gen
sys.path.insert(0, os.getcwd())

from mage2gen import Module
from mage2gen.snippets.model import ModelSnippet
from mage2gen.snippets.system import SystemSnippet
from mage2gen.snippets.observer import ObserverSnippet
from mage2gen.snippets.plugin import PluginSnippet
from mage2gen.snippets.controller import ControllerSnippet
from mage2gen.snippets.cronjob import CronjobSnippet
from mage2gen.snippets.console import ConsoleSnippet

def run_command(command):
    """Run shell command and return output/exit code"""
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

def generate_kitchen_sink():
    output_dir = os.path.join(os.getcwd(), 'generated')
    
    # 1. Cleanup
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    print(f"🚀 Generating 'Kitchen Sink' module in: {output_dir}")

    # 2. Initialize Module
    module = Module(package='Mage2Gen', name='KitchenSink', description='Complex Module for Manual Review')

    # --- Feature: Admin CRUD ---
    print("   - Adding CRUD Model (Post)...")
    model = ModelSnippet(module)
    model.add(
        name='Post', 
        fields='title:text,content:textarea,views:int,is_active:boolean,publish_date:date',
        admin_grid=True,
        admin_form=True,
        api=True,       # Generates Web API
        graphql=True    # Generates GraphQL
    )

    # --- Feature: System Config ---
    print("   - Adding Advanced System Configuration...")
    config = SystemSnippet(module)
    config.add(tab='app', section='settings', group='general', field='enable', type='select', default_value='1', create_tab=True)
    config.add(tab='app', section='settings', group='general', field='api_key', type='text', encrypt=True, depends='enable:1', comment="Encrypted API Key")
    config.add(tab='app', section='settings', group='design', field='logo', type='image')

    # --- Feature: Logic Injection ---
    print("   - Adding Logic (Observer, Plugin, Cron)...")
    ObserverSnippet(module).add('checkout_cart_add_product_complete', scope='frontend')
    PluginSnippet(module).add('Magento\Catalog\Model\Product', 'getName', type='after')
    CronjobSnippet(module).add('CleanLogs', schedule='0 0 * * *')
    ConsoleSnippet(module).add('data:import', description="Import Data Command")

    # --- Feature: Controller ---
    print("   - Adding Frontend Controller...")
    ControllerSnippet(module).add(frontname='kitchen', section='sink', action='index')

    # 3. Generate
    module.generate_module(output_dir)
    
    print(f"✅ Generation Complete.")
    
    # 4. PHP Lint Check (Syntax)
    print("\n🔍 Phase 1: PHP Syntax Check (Lint)...")
    error_count = 0
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.php'):
                full_path = os.path.join(root, file)
                res = os.system(f"php -l {full_path} > /dev/null 2>&1")
                if res != 0:
                    print(f"❌ Syntax Error: {file}")
                    error_count += 1
    
    if error_count == 0:
        print("✨ PHP Syntax Check Passed.")
    else:
        print(f"⚠️  Found {error_count} syntax errors.")

    # 5. Magento Coding Standard Check (Quality)
    print("\n🔍 Phase 2: Magento Coding Standard (PHPCS)...")
    
    # Run PHPCS
    # We ignore standard output and capture stderr/stdout
    cmd = f"phpcs --standard=Magento2 --extensions=php,xml,phtml {output_dir} -n"
    code, out, err = run_command(cmd)
    
    # Filter out Noise
    noise_patterns = [
        "DEPRECATED", 
        "Referenced sniff", 
        "is listening for", # Catches CSS, GRAPHQL, etc.
        "No matching sniffs were found",
        "Run \"phpcs --help\""
    ]
    
    clean_lines = []
    # Combine stdout and stderr for filtering
    combined_output = out + "\n" + err
    
    for line in combined_output.split('\n'):
        if not line.strip(): continue
        if any(p in line for p in noise_patterns): continue
        clean_lines.append(line)
    
    # Save Report
    report_path = os.path.join(output_dir, 'quality_report.txt')
    with open(report_path, 'w') as f:
        f.write('\n'.join(clean_lines))

    if not clean_lines:
        print("✨ Magento Coding Standard Passed! Zero violations.")
    else:
        # Simple heuristic to count violations (lines starting with a number usually)
        print(f"⚠️  Violations detected. Full report: generated/quality_report.txt")
        print("\n   Sample violations:")
        for line in clean_lines[:15]:
            print(f"   {line}")

if __name__ == "__main__":
    generate_kitchen_sink()