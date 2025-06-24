import os
import re
import glob
from datetime import datetime, timedelta

def parse_tle_epoch(line1):
    try:
        epoch_year = int(line1[18:20])
        epoch_day = float(line1[20:32])
        
        if epoch_year < 57:
            year = 2000 + epoch_year
        else:
            year = 1900 + epoch_year
            
        base_date = datetime(year, 1, 1)
        date = base_date + timedelta(days=epoch_day - 1)
        
        return date
    except:
        return None

def extract_norad_id(line1):
    match = re.search(r'^\d\s+(\d+)', line1)
    if match:
        return int(match.group(1))
    return None

def read_tle_file(filepath):
    tle_data = {}
    
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
        
        lines = [line.strip() for line in lines]
        
        i = 0
        while i < len(lines) - 1:
            line1 = lines[i]
            line2 = lines[i+1]
            
            if line1.startswith('1 ') and line2.startswith('2 '):
                norad_id = extract_norad_id(line1)
                
                if norad_id:
                    epoch = parse_tle_epoch(line1)
                    
                    if norad_id not in tle_data:
                        tle_data[norad_id] = []
                    
                    tle_data[norad_id].append((epoch, line1, line2))
                
            i += 1
        
        return tle_data
    
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return {}

def create_norad_id_file(norad_id, tle_list, output_dir):
    filepath = os.path.join(output_dir, f"{norad_id}.txt")
    existing_tles = []
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()
            
            lines = [line.strip() for line in lines]
            
            i = 0
            while i < len(lines) - 1:
                if lines[i].startswith('1 ') and lines[i+1].startswith('2 '):
                    epoch = parse_tle_epoch(lines[i])
                    existing_tles.append((epoch, lines[i], lines[i+1]))
                i += 1
    
    all_tles = existing_tles + tle_list
    
    unique_tles = {}
    for epoch, line1, line2 in all_tles:
        if epoch is not None:
            key = f"{epoch}_{hash(line1+line2)}"
            if key not in unique_tles:
                unique_tles[key] = (epoch, line1, line2)
    
    sorted_tles = sorted([v for v in unique_tles.values()], key=lambda x: x[0] if x[0] else datetime.min)
    
    with open(filepath, 'w') as file:
        for _, line1, line2 in sorted_tles:
            file.write(f"{line1}\n{line2}\n")
    
    return len(sorted_tles)

def process_tle_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_paths = glob.glob(os.path.join(input_dir, "*.txt"))
    
    total_files_processed = 0
    total_objects_found = 0
    total_tles_processed = 0
    processed_norad_ids = set()
    
    print(f"Found {len(file_paths)} TLE files to process in {input_dir}")
    
    for file_path in file_paths:
        try:
            filename = os.path.basename(file_path)
            print(f"Processing {filename}...")
            
            tle_data = read_tle_file(file_path)
            
            for norad_id, tle_list in tle_data.items():
                tle_count = create_norad_id_file(norad_id, tle_list, output_dir)
                
                total_tles_processed += len(tle_list)
                
                if norad_id not in processed_norad_ids:
                    processed_norad_ids.add(norad_id)
                    total_objects_found += 1
                
                print(f"  - NORAD ID {norad_id}: {len(tle_list)} TLEs (total: {tle_count})")
            
            total_files_processed += 1
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    print("\nProcessing complete!")
    print(f"Files processed: {total_files_processed}")
    print(f"Unique objects found: {total_objects_found}")
    print(f"Total TLEs processed: {total_tles_processed}")
    print(f"Output directory: {output_dir}")

def main():
    input_dir = "data"
    output_dir = "objects"
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return
    
    process_tle_files(input_dir, output_dir)

if __name__ == "__main__":
    main()