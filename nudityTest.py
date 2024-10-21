import os
from nudenet import NudeDetector

# Initialize the NudeDetector
detector = NudeDetector()

# Specify the folder containing the images
image_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\screenshots_for_model"
moved_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\screenshots_for_model_moved"

# Create the moved folder if it doesn't exist
os.makedirs(moved_folder, exist_ok=True)

# Get a list of all image files in the folder
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

# Loop through each image file
for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)  # Full path to the image
    classification_results = detector.detect(image_path)  # Classify the image
    
    # Check if nudity is detected
    if classification_results and isinstance(classification_results, list):
        for result in classification_results:
            if result['score'] > 0.5:  # Assuming score > 0.5 means nudity
                print("Nudity detected in", image_file)
                
                # Move the image to the moved_screenshot directory
                destination_path = os.path.join(moved_folder, image_file)
                os.rename(image_path, destination_path)  # Move the file
                
                print(f"Moved {image_file} to {moved_folder}")
                break  # Stop checking after the first nudity detection
        else:
            print("No nudity detected in", image_file)
    else:
        print("Unable to determine classification for", image_file)

print("Nudity detection and moving completed.")
