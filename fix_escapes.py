#!/usr/bin/env python3
"""
Fix invalid escape sequences in Python files using tokenization.

This script uses the tokenize module to accurately find string literals
and fix invalid escape sequences without corrupting multi-line strings.
"""

import argparse
import os
import re
import sys
import shutil
import tokenize
import io
from typing import List, Dict, Any, Tuple

# Valid Python escape sequences that should not be changed
VALID_ESCAPES = {
    '\\\\', '\\n', '\\t', '\\r', '\\b', '\\f', '\\v', '\\a', '\\0',
    '\\"', "\\'", '\\x', '\\u', '\\U', '\\N'
}

# Pattern to detect format placeholders like {0}, {name}, etc.
FORMAT_PLACEHOLDER_PATTERN = re.compile(r'(?<!\\)\{[^}]*\}')

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
                if i + 1 < len(text) and text[i + 1].isupper():
                    return True
            i += 2
        else:
            i += 1
    return False

def fix_string_content(text: str, has_format: bool = False) -> str:
    """Fix the content of a string (without quotes)."""
    if has_format:
        # Double backslashes
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
        # Use raw string if possible
        if "'" not in text:
            return "r'" + text + "'"
        elif '"' not in text:
            return 'r"' + text + '"'
        else:
            return text.replace('\\', '\\\\')

def process_file(filepath: str, dry_run: bool = True) -> List[str]:
    """Process a Python file using tokenization."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"{Colors.RED}Error reading file: {e}{Colors.RESET}"]
    
    changes = []
    
    # Handle tokenization errors gracefully
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(content).readline))
    except tokenize.TokenError as e:
        return [f"{Colors.RED}Tokenization error (file may be corrupted): {e}{Colors.RESET}"]
    except SyntaxError as e:
        return [f"{Colors.RED}Syntax error: {e}{Colors.RESET}"]
    
    modifications = []
    
    for i, token in enumerate(tokens):
        if token.type == tokenize.STRING:
            original_string = token.string
            quote_char = original_string[0]
            
            # Skip already raw strings
            if original_string.startswith('r'):
                continue
            
            # Determine quote length
            if original_string.startswith('"""') or original_string.startswith("'''"):
                quote_len = 3
            else:
                quote_len = 1
            
            string_content = original_string[quote_len:-quote_len]
            
            # Check for invalid escapes
            if not has_invalid_escapes(string_content):
                continue
            
            # Check for format placeholders
            has_format = bool(FORMAT_PLACEHOLDER_PATTERN.search(string_content))
            
            # Fix the content
            fixed_content = fix_string_content(string_content, has_format)
            
            # Reconstruct with proper quotes
            if has_format:
                fixed_string = quote_char + fixed_content + quote_char
            else:
                fixed_string = 'r' + quote_char + string_content + quote_char
            
            modifications.append({
                'start': token.start,
                'end': token.end,
                'original': original_string,
                'fixed': fixed_string,
                'has_format': has_format,
                'line': token.start[0]
            })
            
            change_type = "Format string" if has_format else "Raw string"
            context = token.line.strip() if token.line else ''
            changes.append(
                f"{Colors.YELLOW}Line {token.start[0]}{Colors.RESET}\n"
                f"  {Colors.CYAN}Type:{Colors.RESET} {change_type}\n"
                f"  {Colors.CYAN}Before:{Colors.RESET} {original_string[:80]}\n"
                f"  {Colors.CYAN}After:{Colors.RESET}  {fixed_string[:80]}\n"
                f"  {Colors.CYAN}Context:{Colors.RESET} {context[:60]}"
            )
    
    if not dry_run and modifications:
        # Apply modifications in reverse order
        modifications.sort(key=lambda x: (x['line'], x['start'][1]), reverse=True)
        
        lines = content.splitlines(keepends=True)
        
        for mod in modifications:
            start_line, start_col = mod['start']
            end_line, end_col = mod['end']
            
            if start_line == end_line:
                # Single line
                line = lines[start_line - 1]
                new_line = line[:start_col] + mod['fixed'] + line[end_col:]
                lines[start_line - 1] = new_line
            else:
                # Multi-line - replace entire range
                first_line = lines[start_line - 1][:start_col]
                last_line = lines[end_line - 1][end_col:]
                middle_lines = mod['fixed'].splitlines(keepends=True)
                
                lines[start_line - 1] = first_line + middle_lines[0]
                
                # Insert middle lines
                for i, line in enumerate(middle_lines[1:], 1):
                    lines.insert(start_line, line)
                
                # Append end of last line
                lines[start_line + len(middle_lines) - 1] = lines[start_line + len(middle_lines) - 1].rstrip('\n') + last_line
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            return [f"{Colors.RED}Error writing file: {e}{Colors.RESET}"]
    
    return changes

def main():
    parser = argparse.ArgumentParser(
        description='Fix invalid escape sequences in Python files using tokenization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 fix_escapes.py --dry-run ./mage2gen/
  python3 fix_escapes.py --backup ./mage2gen/
  python3 fix_escapes.py --verbose ./mage2gen/
        """
    )
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
    error_files = []
    
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
        
        if any("error" in change.lower() for change in file_changes):
            error_files.append((filepath, file_changes))
        elif file_changes:
            total_files_changed += 1
            total_changes += len(file_changes)
            
            print(f"\n{Colors.YELLOW if args.dry_run else Colors.GREEN}{'[DRY-RUN] ' if args.dry_run else ''}Fixed: {filepath}{Colors.RESET}")
            
            if args.verbose:
                for change in file_changes:
                    print(f"  {change}")
            else:
                formats = sum(1 for fc in file_changes if 'Format string' in fc)
                raws = sum(1 for fc in file_changes if 'Raw string' in fc)
                print(f"  {formats} format strings, {raws} raw string conversions")
    
    print(f"\n{Colors.CYAN}{'Summary:' if args.dry_run else 'Completed:'}{Colors.RESET}")
    print(f"Files processed: {len(python_files)}")
    print(f"Files modified: {total_files_changed}")
    print(f"Total string literals fixed: {total_changes}")
    
    if error_files:
        print(f"\n{Colors.RED}Files with errors:{Colors.RESET}")
        for filepath, errors in error_files:
            print(f"  {filepath}")
            for error in errors:
                print(f"    {error}")
    
    if args.dry_run:
        print(f"\n{Colors.YELLOW}Run without --dry-run to apply changes{Colors.RESET}")
    elif not args.backup:
        print(f"\n{Colors.CYAN}Consider using --backup for safety on production code{Colors.RESET}")

if __name__ == '__main__':
    main()