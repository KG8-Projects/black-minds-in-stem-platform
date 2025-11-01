#!/usr/bin/env python3
"""
Comprehensive Target Grade Date Pattern Fixer

This script fixes ALL possible date format patterns in the target_grade column 
of ALL CSV files in the data folder and replaces them with proper grade ranges.
"""

import os
import csv
import re
from typing import Dict, List, Tuple

def create_replacement_mappings() -> Dict[str, str]:
    """Create comprehensive mapping of all date patterns to proper grade ranges."""
    replacements = {}
    
    # Month name to number mapping
    month_to_num = {
        'Jan': 1, 'January': 1,
        'Feb': 2, 'February': 2, 
        'Mar': 3, 'March': 3,
        'Apr': 4, 'April': 4,
        'May': 5, 'May': 5,  # Same for both short/long
        'Jun': 6, 'June': 6,
        'Jul': 7, 'July': 7,
        'Aug': 8, 'August': 8,
        'Sep': 9, 'September': 9,
        'Oct': 10, 'October': 10,
        'Nov': 11, 'November': 11,
        'Dec': 12, 'December': 12
    }
    
    # Generate all possible patterns for numbers 1-12
    for num in range(1, 13):
        for month_abbr, month_num in month_to_num.items():
            
            # MONTH-NUMBER patterns (Month represents grade, Number represents upper bound)
            pattern1 = f"{month_abbr}-{num}"
            if month_num <= num:
                if month_num == num:
                    grade_range = str(month_num)  # Single grade
                else:
                    grade_range = f"{month_num}-{num}"
            else:
                grade_range = f"{month_num}-{num}"  # Even if lower > upper, keep format
            replacements[pattern1] = grade_range
            
            # NUMBER-MONTH patterns (Number represents upper bound, Month represents grade)  
            pattern2 = f"{num}-{month_abbr}"
            if month_num <= num:
                if month_num == num:
                    grade_range = str(month_num)  # Single grade
                else:
                    grade_range = f"{month_num}-{num}"
            else:
                grade_range = f"{month_num}-{num}"  # Even if lower > upper, keep format
            replacements[pattern2] = grade_range
    
    # Special cases for logical grade ranges
    special_cases = {
        # Common logical patterns
        '12-Dec': '12',        # Dec=12, so 12-12 = 12
        'Dec-12': '12',        # Dec=12, so 12-12 = 12
        '11-Nov': '11',        # Nov=11, so 11-11 = 11
        'Nov-11': '11',        # Nov=11, so 11-11 = 11
        '10-Oct': '10',        # Oct=10, so 10-10 = 10
        'Oct-10': '10',        # Oct=10, so 10-10 = 10
        
        # Reverse logical ranges (when month > number)
        '1-Dec': '1-12',       # 1 to December(12)
        '2-Dec': '2-12',       # 2 to December(12)
        '3-Dec': '3-12',       # 3 to December(12)
        'Jan-12': '1-12',      # January(1) to 12
        'Feb-11': '2-11',      # February(2) to 11
        'Mar-10': '3-10',      # March(3) to 10
    }
    
    # Override with special cases
    replacements.update(special_cases)
    
    return replacements

def fix_target_grade_column(csv_file_path: str) -> Tuple[int, List[str]]:
    """
    Fix date patterns in target_grade column of a CSV file.
    
    Returns:
        Tuple of (num_replacements_made, list_of_changes_made)
    """
    replacements = create_replacement_mappings()
    changes_made = []
    total_replacements = 0
    
    # Read the CSV file
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
            # Detect the CSV dialect
            sample = file.read(1024)
            file.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            
            reader = csv.reader(file, dialect)
            rows = list(reader)
            
        if not rows:
            print(f"  Empty file: {csv_file_path}")
            return 0, []
            
        # Find target_grade column index (should be column 7, index 6)
        header = rows[0]
        target_grade_col = None
        
        for i, col_name in enumerate(header):
            if 'target_grade' in col_name.lower():
                target_grade_col = i
                break
                
        if target_grade_col is None:
            print(f"  No target_grade column found in: {csv_file_path}")
            return 0, []
            
        print(f"  Found target_grade column at index {target_grade_col}")
        
        # Process each data row
        for row_idx in range(1, len(rows)):  # Skip header
            if target_grade_col < len(rows[row_idx]):
                original_value = rows[row_idx][target_grade_col]
                modified_value = original_value
                
                # Apply all replacement patterns
                for pattern, replacement in replacements.items():
                    if pattern in modified_value:
                        old_modified = modified_value
                        modified_value = modified_value.replace(pattern, replacement)
                        if old_modified != modified_value:
                            changes_made.append(f"Row {row_idx+1}: '{pattern}' -> '{replacement}'")
                            total_replacements += 1
                            print(f"    Row {row_idx+1}: '{original_value}' -> '{modified_value}'")
                
                # Update the row if changes were made
                rows[row_idx][target_grade_col] = modified_value
        
        # Write back the modified CSV
        if total_replacements > 0:
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, dialect)
                writer.writerows(rows)
            print(f"  Saved {csv_file_path} with {total_replacements} replacements")
        else:
            print(f"  No changes needed in {csv_file_path}")
            
    except Exception as e:
        print(f"  Error processing {csv_file_path}: {str(e)}")
        return 0, []
    
    return total_replacements, changes_made

def main():
    """Main function to process all CSV files in the data folder."""
    
    # Set the data folder path
    data_folder = r"C:\Users\u_wos\Downloads\Black Minds In STEM\Scrapers\scrapers\data"
    
    print("COMPREHENSIVE TARGET_GRADE DATE PATTERN FIXER")
    print("=" * 60)
    print(f"Processing CSV files in: {data_folder}")
    print()
    
    if not os.path.exists(data_folder):
        print(f"Error: Data folder not found: {data_folder}")
        return
    
    # Find all CSV files
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the data folder")
        return
        
    print(f"Found {len(csv_files)} CSV files to process")
    print()
    
    total_files_modified = 0
    total_replacements_made = 0
    all_changes = {}
    
    # Process each CSV file
    for csv_file in sorted(csv_files):
        csv_path = os.path.join(data_folder, csv_file)
        print(f"Processing: {csv_file}")
        
        num_replacements, changes = fix_target_grade_column(csv_path)
        
        if num_replacements > 0:
            total_files_modified += 1
            total_replacements_made += num_replacements
            all_changes[csv_file] = changes
            
        print()  # Empty line between files
    
    # Print final summary
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(csv_files)}")
    print(f"Files modified: {total_files_modified}")
    print(f"Total replacements made: {total_replacements_made}")
    
    if all_changes:
        print()
        print("DETAILED CHANGES BY FILE:")
        print("-" * 40)
        for file_name, changes in all_changes.items():
            print(f"{file_name}:")
            for change in changes:
                print(f"  - {change}")
            print()
    else:
        print()
        print("No date format patterns found in any target_grade columns!")
        print("All CSV files already have proper grade range formatting.")
    
    print("Processing complete!")

if __name__ == "__main__":
    main()