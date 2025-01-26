import json
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def load_annotations(file_path):
    """Load annotations from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def parse_nlp_annotations(annotations1, annotations2):
    """Parse NLP annotations and extract POS tags for overlapping samples."""
    annotations_dict1 = {annotation['id']: annotation for annotation in annotations1}
    annotations_dict2 = {annotation['id']: annotation for annotation in annotations2}
    common_ids = set(annotations_dict1.keys()) & set(annotations_dict2.keys())

    pos_tags1, pos_tags2 = [], []

    for common_id in common_ids:
        labels1 = annotations_dict1[common_id]['label']
        labels2 = annotations_dict2[common_id]['label']

        # Build a dictionary for quick lookup of labels by 'start' position
        labels2_by_start = {label['start']: label for label in labels2}

        for label1 in labels1:
            start1 = label1['start']
            if start1 in labels2_by_start:
                # Match labels based on 'start' position
                label2 = labels2_by_start[start1]
                pos_tags1.append(label1['labels'][0])  # Extract POS tag for annotator 1
                pos_tags2.append(label2['labels'][0])  # Extract POS tag for annotator 2
            else:
                # Handle unmatched cases (optional)
                print(f"Warning: No matching label for start {start1} in ID {common_id}. Skipping.")

    return pos_tags1, pos_tags2


def calculate_cohen_kappa(pos_tags1, pos_tags2):
    """Calculate Cohen's Kappa score and interpret the agreement."""
    
    # Print number of unique labels
    all_labels = set(pos_tags1 + pos_tags2)
    print("Number of unique labels:", len(all_labels))
    print("Labels used:", all_labels)
    
    # Identify mismatches
    mismatches = [(i, tag1, tag2) for i, (tag1, tag2) in enumerate(zip(pos_tags1, pos_tags2)) if tag1 != tag2]
    if mismatches:
        print("\nMismatched Annotations (Annotators Disagree):")
        for mismatch in mismatches:
            print(f"Index: {mismatch[0]}, Annotator 1: {mismatch[1]}, Annotator 2: {mismatch[2]}")
    else:
        print("\nNo mismatches detected. All annotators agree.")
    
    kappa = cohen_kappa_score(pos_tags1, pos_tags2)
    print("Cohen's Kappa:", kappa)

    # Interpret the agreement score
    if kappa < 0:
        print("No agreement")
    elif kappa < 0.2:
        print("Slight agreement")
    elif kappa < 0.4:
        print("Fair agreement")
    elif kappa < 0.6:
        print("Moderate agreement")
    elif kappa < 0.8:
        print("Substantial agreement")
    else:
        print("Almost perfect agreement")
    
    return kappa

def parse_cv_annotations(file_data):
    """Parse CV annotations and extract image name and label."""
    extracted_data = {}
    for item in file_data:
        image_name = item['image'].split('-')[-1]  # Extracts 'img_{number}.jpg'
        label = item['choice']
        extracted_data[image_name] = label
    return extracted_data

def combine_annotations(data1_parsed, data2_parsed, data3_parsed):
    """Combine annotations by image."""
    combined_data = {}
    for image_name in set(data1_parsed.keys()).union(data2_parsed.keys()):
        combined_data[image_name] = []
        if image_name in data1_parsed:
            combined_data[image_name].append(data1_parsed[image_name])
        if image_name in data2_parsed:
            combined_data[image_name].append(data2_parsed[image_name])
        if image_name in data3_parsed:
            combined_data[image_name].append(data3_parsed[image_name])
    return combined_data

def calculate_fleiss_kappa(combined_data):
    """Calculate Fleiss Kappa score and interpret the agreement."""
    df = pd.DataFrame.from_dict(combined_data, orient='index')
    mismatches = df[df.nunique(axis=1) > 1]
    all_labels = set(df.values.flatten())
    print("Number of unique labels:", len(all_labels))
    print("Labels used:", all_labels)

    if not mismatches.empty:
        print("\nMismatched Annotations (Annotators Disagree):")
        print(mismatches)
    else:
        print("\nNo mismatches detected. All annotators agree.")

    label_map = {label: i for i, label in enumerate(all_labels)}
    df_mapped = df.applymap(lambda x: label_map[x])
    rating_table = []
    for row in df_mapped.itertuples(index=False):
        counts = [0] * len(label_map)
        for label in row:
            counts[label] += 1
        rating_table.append(counts)

    fleiss_kappa_score = fleiss_kappa(rating_table)
    print("\nFleiss Kappa Score:", fleiss_kappa_score)
    if 0.80 <= fleiss_kappa_score <= 1.00:
        print("Very good agreement")
    elif 0.60 <= fleiss_kappa_score < 0.80:
        print("Good agreement")
    elif 0.40 <= fleiss_kappa_score < 0.60:
        print("Moderate agreement")
    elif 0.20 <= fleiss_kappa_score < 0.40:
        print("Fair agreement")
    else:
        print("Poor agreement")
    
    return fleiss_kappa_score

def summary(cohen_kappa_score, fleiss_kappa_score):
    """Print a summary of Cohen's Kappa and Fleiss Kappa scores."""
    print("\nSummary:")
    print(f"Cohen's Kappa Score: {cohen_kappa_score}")
    print(f"Fleiss Kappa Score: {fleiss_kappa_score}")

def main():
    # NLP Cohen's Kappa
    annotations1 = load_annotations('NLP_23110065.json')
    annotations2 = load_annotations('NLP_23110066.json')
    pos_tags1, pos_tags2 = parse_nlp_annotations(annotations1, annotations2)
    cohen_kappa_score = calculate_cohen_kappa(pos_tags1, pos_tags2)
    print("-" * 130)
    # CV Fleiss Kappa
    data1 = load_annotations('CV_23110065.json')
    data2 = load_annotations('CV_23110066.json')
    data3 = load_annotations('CV_third-member.json')
    data1_parsed = parse_cv_annotations(data1)
    data2_parsed = parse_cv_annotations(data2)
    data3_parsed = parse_cv_annotations(data3)
    combined_data = combine_annotations(data1_parsed, data2_parsed, data3_parsed)
    fleiss_kappa_score = calculate_fleiss_kappa(combined_data)

    # Print summary
    summary(cohen_kappa_score, fleiss_kappa_score)

if __name__ == "__main__":
    main()
