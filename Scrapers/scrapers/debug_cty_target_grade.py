#!/usr/bin/env python3
"""
Debug script to show EXACT content of target_grade column in CTY CSV file
"""

import csv
import os

def debug_target_grade_column():
    """Debug the target_grade column in CTY CSV file."""
    
    csv_file_path = r"C:\Users\u_wos\Downloads\Black Minds In STEM\Scrapers\scrapers\data\cty_programs_combined.csv"
    
    print("DEBUG: CTY TARGET_GRADE COLUMN ANALYSIS")
    print("=" * 60)
    print(f"File: {csv_file_path}")
    print()
    
    if not os.path.exists(csv_file_path):
        print(f"ERROR: File not found: {csv_file_path}")
        return
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        if not rows:
            print("ERROR: File is empty")
            return
            
        # Find target_grade column
        header = rows[0]
        print(f"HEADER ROW ({len(header)} columns):")
        for i, col_name in enumerate(header):
            print(f"  [{i}]: '{col_name}'")
        print()
        
        target_grade_col = None
        for i, col_name in enumerate(header):
            if 'target_grade' in col_name.lower():
                target_grade_col = i
                break
                
        if target_grade_col is None:
            print("ERROR: No target_grade column found!")
            return
            
        print(f"TARGET_GRADE COLUMN FOUND AT INDEX: {target_grade_col}")
        print()
        
        # Show all target_grade values
        print("ALL TARGET_GRADE VALUES:")
        print("-" * 40)
        
        for row_idx, row in enumerate(rows):
            if row_idx == 0:  # Skip header
                continue
                
            # Get program name for reference
            program_name = row[0] if len(row) > 0 else "UNKNOWN"
            
            # Get target_grade value
            if target_grade_col < len(row):
                target_grade_value = row[target_grade_col]
                
                # Show raw content with special characters visible
                print(f"Row {row_idx + 1:2d}: Program='{program_name[:40]:<40}' | target_grade='{target_grade_value}'")
                
                # Show character by character breakdown if it looks suspicious
                if any(char in target_grade_value for char in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 
                                                              '\n', '\r', '\t']):
                    print(f"      SUSPICIOUS! Character breakdown:")
                    for i, char in enumerate(target_grade_value):
                        if char == '\n':
                            print(f"        [{i:2d}]: '\\n' (newline)")
                        elif char == '\r':
                            print(f"        [{i:2d}]: '\\r' (carriage return)")
                        elif char == '\t':
                            print(f"        [{i:2d}]: '\\t' (tab)")
                        else:
                            print(f"        [{i:2d}]: '{char}'")
                    print()
            else:
                print(f"Row {row_idx + 1:2d}: Program='{program_name[:40]:<40}' | target_grade=MISSING (row too short)")
        
        print()
        print(f"TOTAL ROWS PROCESSED: {len(rows) - 1} (excluding header)")
        
        # Check for any month patterns
        print()
        print("SCANNING FOR MONTH PATTERNS:")
        print("-" * 30)
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                  'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        
        found_patterns = []
        
        for row_idx, row in enumerate(rows[1:], 1):  # Skip header
            if target_grade_col < len(row):
                target_grade_value = row[target_grade_col]
                for month in months:
                    if month in target_grade_value:
                        found_patterns.append((row_idx + 1, row[0], target_grade_value, month))
        
        if found_patterns:
            print("FOUND MONTH PATTERNS:")
            for row_num, program, value, month in found_patterns:
                print(f"  Row {row_num}: '{program[:30]}' -> '{value}' contains '{month}'")
        else:
            print("No month patterns found in target_grade column")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    debug_target_grade_column()