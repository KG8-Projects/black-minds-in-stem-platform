#!/usr/bin/env python3
"""
Simple script to show raw target_grade column content
"""

import csv

csv_file_path = r"C:\Users\u_wos\Downloads\Black Minds In STEM\Scrapers\scrapers\data\cty_programs_combined.csv"

with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    rows = list(reader)

# Find target_grade column (should be index 6)
header = rows[0]
target_grade_col = 6

print("RAW TARGET_GRADE COLUMN CONTENT:")
print("================================")

for i, row in enumerate(rows):
    if i == 0:
        print(f"HEADER: {row[target_grade_col]}")
        continue
    
    if target_grade_col < len(row):
        print(f"Row {i}: {repr(row[target_grade_col])}")
    else:
        print(f"Row {i}: [MISSING]")