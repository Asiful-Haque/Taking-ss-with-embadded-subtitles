import os
from nudenet import NudeDetector
from PIL import Image, ImageEnhance

# Initialize the NudeDetector
detector = NudeDetector()

# Specify the folder containing the images
image_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\screenshots_for_model"
moved_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\screenshots_for_model_moved"

# Create the moved folder if it doesn't exist
os.makedirs(moved_folder, exist_ok=True)

# Get a list of all image files in the folder
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

# Function to enhance image contrast and sharpness
def enhance_image(image_path):
    with Image.open(image_path) as img:
        # Enhance contrast and sharpness
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)  # Increase contrast by 1.5x
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)  # Increase sharpness by 2x
        
        img.save(image_path)  # Overwrite the original image

# Function to resize an image and overwrite the original file
def resize_image(image_path, size=(1280, 720)):
    with Image.open(image_path) as img:
        img = img.resize(size)
        img.save(image_path)  # Overwrite the original image

# Function to classify and move the image if nudity is detected
def classify_and_move_image(image_path, image_file):
    classification_results = detector.detect(image_path)  # Classify the image

    # Check if nudity is detected
    if classification_results and isinstance(classification_results, list):
        print(f"Results for {image_file}: {classification_results}")
        for result in classification_results:
            if result['score'] > 0.1:  # Lower threshold to 0.1
                print(f"Nudity detected in {image_file}")
                
                # Move the image to the moved_screenshot directory
                destination_path = os.path.join(moved_folder, image_file)
                os.rename(image_path, destination_path)  # Move the file
                
                print(f"Moved {image_file} to {moved_folder}")
                return True
        else:
            print(f"No nudity detected in {image_file}")
            return False
    else:
        print(f"Unable to determine classification for {image_file}")
        return False

# Loop through each image file
for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)  # Full path to the image
    
    # First attempt to classify the original image
    nudity_detected = classify_and_move_image(image_path, image_file)

    # If classification failed, try resizing and classifying the resized image
    if not nudity_detected:
        print(f"Resizing and reclassifying {image_file}...")

        # Resize the image in the same folder (overwriting the original)
        resize_image(image_path)
        
        # Classify the resized image
        nudity_detected = classify_and_move_image(image_path, image_file)

    # If resizing doesn't help, enhance the image and try again
    if not nudity_detected:
        print(f"Enhancing and reclassifying {image_file}...")

        # Enhance the image (contrast and sharpness)
        enhance_image(image_path)
        
        # Classify the enhanced image
        classify_and_move_image(image_path, image_file)

print("Nudity detection, resizing, enhancing, and moving process completed.")
