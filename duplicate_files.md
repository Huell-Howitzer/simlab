It looks like the script ran but didn’t find any files to compare. This likely happened because:
	1.	The directory path provided (/mnt/data/large_directory) might not contain any files in the supported formats (text, PDF, OpenOffice).
	2.	Exclusion patterns could have filtered out too many files.
	3.	There could be a permissions issue or incorrect directory path.

🔍 Here’s How You Can Run This Locally with Your Large Dataset

I recommend running this on your local machine since you’re working with a multi-terabyte directory. Below is a fully functional script tailored to your needs:

✅ Full Script for Local Use

# Install dependencies
pip install pandas pdfminer.six fuzzywuzzy python-Levenshtein odfpy tqdm

📜 Complete Python Script

import os
import re
import pandas as pd
from tqdm import tqdm
from itertools import combinations
from fuzzywuzzy import fuzz
from pdfminer.high_level import extract_text as extract_pdf_text
from odf.opendocument import load as load_odf
from odf.text import P, H

def extract_text(filepath):
    try:
        if filepath.endswith(('.txt', '.py', '.java', '.js', '.html', '.css', '.md')):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        elif filepath.endswith('.pdf'):
            return extract_pdf_text(filepath)
        elif filepath.endswith(('.odt', '.ods', '.odp')):
            return extract_odf_text(filepath)
        else:
            return None
    except:
        return None

def extract_odf_text(filepath):
    try:
        doc = load_odf(filepath)
        text_content = ''
        for elem in doc.getElementsByType(P) + doc.getElementsByType(H):
            text_content += str(elem) + '\n'
        return text_content
    except:
        return None

def scan_directory(directory, exclude_patterns):
    file_contents = {}
    for root, dirs, files in os.walk(directory):
        if any(re.search(pattern, root) for pattern in exclude_patterns):
            continue
        for filename in files:
            filepath = os.path.join(root, filename)
            if filepath.endswith(('.txt', '.py', '.java', '.js', '.html', '.css', '.md', '.pdf', '.odt', '.ods', '.odp')):
                text = extract_text(filepath)
                if text:
                    file_contents[filepath] = text
    return file_contents

def find_near_duplicates(file_contents, similarity_threshold=85):
    similar_files = []
    checked_pairs = set()

    for (file1, content1), (file2, content2) in tqdm(combinations(file_contents.items(), 2), total=len(file_contents) * (len(file_contents) - 1) // 2):
        if (file1, file2) in checked_pairs or (file2, file1) in checked_pairs:
            continue
        similarity = fuzz.ratio(content1, content2)
        if similarity >= similarity_threshold:
            similar_files.append({
                "File 1": file1,
                "File 2": file2,
                "Similarity Score": similarity
            })
        checked_pairs.add((file1, file2))
    return similar_files

def group_duplicates(similar_files):
    clusters = []
    file_to_cluster = {}

    for pair in similar_files:
        file1 = pair['File 1']
        file2 = pair['File 2']

        cluster1 = file_to_cluster.get(file1)
        cluster2 = file_to_cluster.get(file2)

        if cluster1 and cluster2:
            if cluster1 != cluster2:
                clusters[cluster1].update(clusters[cluster2])
                for f in clusters[cluster2]:
                    file_to_cluster[f] = cluster1
                clusters[cluster2] = set()
        elif cluster1 or cluster2:
            cluster_index = cluster1 if cluster1 is not None else cluster2
            clusters[cluster_index].update([file1, file2])
            file_to_cluster[file1] = cluster_index
            file_to_cluster[file2] = cluster_index
        else:
            new_cluster = {file1, file2}
            clusters.append(new_cluster)
            cluster_index = len(clusters) - 1
            file_to_cluster[file1] = cluster_index
            file_to_cluster[file2] = cluster_index

    clusters = [cluster for cluster in clusters if cluster]
    return clusters

def process_directory(directory, exclude_patterns):
    print("Scanning directory for files...")
    file_contents = scan_directory(directory, exclude_patterns)
    
    print(f"Found {len(file_contents)} files to compare.")
    print("Finding near-duplicates...")
    similar_files = find_near_duplicates(file_contents)

    print("Grouping duplicates...")
    clusters = group_duplicates(similar_files)

    cluster_data = []
    for idx, cluster in enumerate(clusters, start=1):
        for file in cluster:
            cluster_data.append({'Cluster ID': idx, 'File': file})

    duplicate_df = pd.DataFrame(cluster_data)
    return duplicate_df

# Example usage:
directory_to_scan = input("Enter the directory to scan: ")
exclude_patterns = [r'backup', r'temp', r'\.git']  # Modify as needed

duplicates_df = process_directory(directory_to_scan, exclude_patterns)

# Save output to a CSV
output_file = "near_duplicates_report.csv"
duplicates_df.to_csv(output_file, index=False)
print(f"Duplicate files report saved to {output_file}")

🔧 Usage Instructions
	1.	Replace directory_to_scan with the root path of the directory you want to scan.
	2.	Add any directories you want to exclude using regex patterns.
	3.	Run the script in your terminal:

python detect_duplicates.py


	4.	The results will be saved in a near_duplicates_report.csv file.

Would you like me to help modify the exclusion logic further, or provide additional optimization suggestions for handling massive datasets efficiently? ￼