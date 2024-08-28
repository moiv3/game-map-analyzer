def filter_frames(filenames, threshold):
    filtered_filenames = []
    for filename in filenames:
        # Extract the numeric part from the filename
        num_part = int(filename.split('frame_')[1].split('.')[0])
        # Check if the numeric part is greater than or equal to the threshold
        if num_part >= threshold:
            filtered_filenames.append(filename)
    return filtered_filenames