#!/usr/bin/env python3
"""
Fix invalid escape sequences in Python files for Magento 2 module generator.

This script scans Python files for string literals containing backslashes that
form invalid escape sequences (like \\M, \\F in PHP class names) and fixes them
by either:
1. Converting to raw strings (r'...') for simple strings
2. Doubling backslashes for strings with format placeholders

Usage:
    python fix_escapes.py --dry-run /path/to/module
    python fix_escapes.py --backup /path/to/module
    python fix_escapes.py /path/to/module  # Apply changes
"""

import argparse
import ast
import os
import re
import sys
import shutil
from typing import List, Dict, Any, Tuple

# Valid Python escape sequences that should not be changed
VALID_ESCAPES = {
    '\\\\', '\\n', '\\t', '\\r', '\\b', '\\f', '\\v', '\\a', '\\0',
    '\\"', "\\'", '\\x', '\\u', '\\U', '\\N'
}

# Pattern to detect format placeholders like {0}, {name}, etc.
FORMAT_PLACEHOLDER_PATTERN = re.compile(r'(?<!\\)\{[^}]*\}')

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def is_valid_escape_sequence(text: str, pos: int) -> bool:
    """Check if the backslash at position pos starts a valid escape sequence."""
    if pos >= len(text) - 1:
        return False
    
    # Check two-character escapes
    two_char = text[pos:pos + 2]
    if two_char in VALID_ESCAPES:
        return True
    
    # Check hex escape \xhh
    if text[pos + 1] == 'x' and pos + 3 < len(text) and text[pos + 2:pos + 4].isdigit():
        return True
    
    # Check octal escapes \ooo
    if text[pos + 1] in '01234567':
        octal_digits = 0
        for i in range(pos + 1, min(pos + 4, len(text))):
            if text[i] in '01234567':
                octal_digits += 1
            else:
                break
        return octal_digits > 0
    
    # Check unicode name escape \N{name}
    if text[pos + 1] == 'N' and pos + 2 < len(text) and text[pos + 2] == '{':
        return True
    
    return False

def has_invalid_escapes(text: str) -> bool:
    """Check if a string contains invalid escape sequences."""
    if text.startswith('r"') or text.startswith("r'"):
        return False  # Already a raw string
    
    i = 0
    while i < len(text) - 1:
        if text[i] == '\\':
            if not is_valid_escape_sequence(text, i):
                # Check if it's likely a PHP namespace (capital letter after backslash)
                if i + 1 < len(text) and text[i + 1].isupper():
                    return True
            i += 2  # Skip the escape sequence
        else:
            i += 1
    return False

def fix_string_literal(text: str, has_format: bool = False) -> str:
    """
    Fix a string literal by either making it raw or doubling backslashes.
    
    Args:
        text: The original string value
        has_format: Whether the string contains format placeholders
    
    Returns:
        The fixed string literal text
    """
    if has_format:
        # Can't use raw string - double backslashes instead
        result = []
        i = 0
        while i < len(text):
            if text[i] == '\\':
                if is_valid_escape_sequence(text, i):
                    result.append(text[i:i+2])
                    i += 2
                else:
                    result.append('\\\\')
                    i += 1
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)
    else:
        # Can use raw string if no quotes inside
        if "'" not in text:
            return "r'" + text + "'"
        elif '"' not in text:
            return 'r"' + text + '"'
        else:
            # Contains both quote types - must escape
            return text.replace('\\', '\\\\')

def process_file(filepath: str, dry_run: bool = True) -> List[str]:
    """Process a Python file and return list of changes made."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"{Colors.RED}Error reading file: {e}{Colors.RESET}"]
    
    try:
        tree = ast.parse(content, filepath)
    except SyntaxError as e:
        return [f"{Colors.RED}SyntaxError: {e}{Colors.RESET}"]
    
    changes = []
    lines = content.splitlines(keepends=True)
    
    class StringVisitor(ast.NodeVisitor):
        def __init__(self):
            self.string_nodes = []
        
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value:
                self.string_nodes.append(node)
        
        # For Python < 3.8 compatibility
        def visit_Str(self, node):
            if isinstance(getattr(node, 's', ''), str):
                self.string_nodes.append(node)
    
    visitor = StringVisitor()
    visitor.visit(tree)
    
    line_modifications = {}
    
    for node in visitor.string_nodes:
        value = node.value if hasattr(node, 'value') else getattr(node, 's', '')
        if not value or not isinstance(value, str):
            continue
        
        if not has_invalid_escapes(value):
            continue
        
        has_format = bool(FORMAT_PLACEHOLDER_PATTERN.search(value))
        fixed_value = fix_string_literal(value, has_format)
        
        # Get line and column positions
        line_no = node.lineno - 1
        col_offset = node.col_offset
        
        if line_no not in line_modifications:
            line_modifications[line_no] = []
        
        # Store original and fixed versions for display
        original_repr = repr(value)
        if has_format:
            fixed_display = f'"{fixed_value}"'
        elif fixed_value.startswith('r'):
            fixed_display = fixed_value
        else:
            fixed_display = f'"{fixed_value}"'
        
        line_modifications[line_no].append({
            'start': col_offset,
            'end': col_offset + len(original_repr),
            'fixed': fixed_value,
            'original': original_repr,
            'fixed_display': fixed_display,
            'has_format': has_format
        })
        
        # Show change context
        lines_std = content.splitlines()
        if line_no < len(lines_std):
            context = lines_std[line_no].strip()
            change_type = "Format string" if has_format else "Raw string"
            changes.append(
                f"{Colors.YELLOW}Line {node.lineno}{Colors.RESET}\n"
                f"  {Colors.CYAN}Type:{Colors.RESET} {change_type}\n"
                f"  {Colors.CYAN}Before:{Colors.RESET} {original_repr[:80]}\n"
                f"  {Colors.CYAN}After:{Colors.RESET}  {fixed_display[:80]}\n"
                f"  {Colors.CYAN}Context:{Colors.RESET} {context[:60]}"
            )
    
    if not dry_run and line_modifications:
        new_lines = []
        for i, line in enumerate(lines):
            if i in line_modifications:
                # Sort modifications by start position in reverse to apply from right to left
                mods = sorted(line_modifications[i], key=lambda x: x['start'], reverse=True)
                for mod in mods:
                    line = line[:mod['start']] + mod['fixed'] + line[mod['end']:]
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        except Exception as e:
            return [f"{Colors.RED}Error writing file: {e}{Colors.RESET}"]
    
    return changes

def main():
    parser = argparse.ArgumentParser(description='Fix invalid escape sequences in Python files')
    parser.add_argument('directory', help='Directory to scan for Python files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--backup', action='store_true', help='Backup files before modifying')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed changes per file')
    parser.add_argument('--suffix', default='.bak', help='Backup suffix')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"{Colors.RED}Error: {args.directory} is not a valid directory{Colors.RESET}", file=sys.stderr)
        sys.exit(1)
    
    python_files = []
    for root, dirs, files in os.walk(args.directory):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env', 'node_modules']]
        python_files.extend([os.path.join(root, f) for f in files if f.endswith('.py')])
    
    if not python_files:
        print("No Python files found")
        sys.exit(0)
    
    print(f"{Colors.GREEN}Found {len(python_files)} Python files to scan{Colors.RESET}")
    if args.dry_run:
        print(f"{Colors.YELLOW}Running in DRY-RUN mode{Colors.RESET}")
    
    total_files_changed = 0
    total_changes = 0
    
    for filepath in python_files:
        if args.backup and not args.dry_run:
            backup_path = filepath + args.suffix
            try:
                shutil.copy2(filepath, backup_path)
                print(f"{Colors.CYAN}Backed up {filepath} to {backup_path}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Error backing up {filepath}: {e}{Colors.RESET}")
                continue
        
        file_changes = process_file(filepath, dry_run=args.dry_run)
        if file_changes:
            total_files_changed += 1
            total_changes += len(file_changes)
            
            print(f"\n{Colors.YELLOW if args.dry_run else Colors.GREEN}{'[DRY-RUN] ' if args.dry_run else ''}Fixed: {filepath}{Colors.RESET}")
            
            if args.verbose:
                for change in file_changes:
                    print(f"  {change}")
            else:
                # Show summary of changes
                formats = sum(1 for fc in file_changes if 'Format string' in fc)
                raws = sum(1 for fc in file_changes if 'Raw string' in fc)
                print(f"  {formats} format strings, {raws} raw string conversions")
    
    print(f"\n{Colors.CYAN}{'Summary:' if args.dry_run else 'Completed:'}{Colors.RESET}")
    print(f"Files processed: {len(python_files)}")
    print(f"Files modified: {total_files_changed}")
    print(f"Total string literals fixed: {total_changes}")
    
    if args.dry_run:
        print(f"\n{Colors.YELLOW}Run without --dry-run to apply changes{Colors.RESET}")
    elif not args.backup:
        print(f"\n{Colors.CYAN}Consider using --backup for safety on production code{Colors.RESET}")

if __name__ == '__main__':
    main()