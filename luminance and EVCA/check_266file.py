import os
import csv


def generate_expected_filenames():
    """Generate a list of all expected filenames."""
    filenames = []
    for index in range(251, 501):
        for qp in range(10, 51, 2):
            filenames.append(f"[RA][test0{index}_config][QP{qp}].266")
    return set(filenames)

def find_missing_files(directory):
    """Check for missing files in the specified directory."""
    expected_files = generate_expected_filenames()
    existing_files = set(os.listdir(directory))
    missing_files = expected_files - existing_files
    return sorted(missing_files)

def save_missing_to_csv(missing_files, output_csv):
    """Save the list of missing files to a CSV file."""
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Missing Files"])
        for filename in missing_files:
            writer.writerow([filename])

def main():
    resolution = '360p'
    directory = "C:/Inter4K/VVC/360p"  # Replace with the actual folder containing .266 files
    output_csv = f"./log/missing_files_{resolution}.csv"

    missing_files = find_missing_files(directory)
    save_missing_to_csv(missing_files, output_csv)

    print(f"Number of missing files: {len(missing_files)}")
    print(f"The list of missing files has been saved to {output_csv}")

if __name__ == "__main__":
    main()

