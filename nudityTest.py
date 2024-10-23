import os
from nudenet import NudeDetector
from PIL import Image, ImageEnhance
import mysql.connector

# Initialize the NudeDetector
detector = NudeDetector()

# Database connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bdword_v5"
    )
    print("Database connection successful.")
except mysql.connector.Error as err:
    print(f"Error connecting to database: {err}")
    exit()

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
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        img.save(image_path)

# Function to resize an image and overwrite the original file
def resize_image(image_path, size=(1280, 720)):
    with Image.open(image_path) as img:
        img = img.resize(size)
        img.save(image_path)

# Function to classify and move the image if nudity is detected
def classify_and_move_image(image_path, image_file):
    classification_results = detector.detect(image_path)

    if classification_results and isinstance(classification_results, list):
        print(f"Results for {image_file}: {classification_results}")
        for result in classification_results:
            if result['score'] > 0.1:  # Lower threshold to 0.1
                print(f"Nudity detected in {image_file}")

                # Extract series_season_episode and start_time from the filename
                basename = os.path.splitext(image_file)[0]
                parts = basename.split('_')
                if len(parts) >= 2:
                    series_season_episode = '_'.join(parts[:-1])  # All parts except the last one
                    start_time = parts[-1].replace("-", ":")  # Replace hyphens with colons to match the format in the DB

                    # SQL query to delete the row from the database
                    delete_query = (
                        "DELETE FROM sub WHERE series_season_episode = %s AND start_time = %s"
                    )
                    try:
                        cursor = conn.cursor()
                        cursor.execute(delete_query, (series_season_episode, start_time))
                        conn.commit()
                        print(f"Deleted row from database: {series_season_episode}, {start_time}")
                    except mysql.connector.Error as err:
                        print(f"Error deleting row from database: {err}")

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
    image_path = os.path.join(image_folder, image_file)

    nudity_detected = classify_and_move_image(image_path, image_file)

    if not nudity_detected:
        print(f"Resizing and reclassifying {image_file}...")
        resize_image(image_path)
        nudity_detected = classify_and_move_image(image_path, image_file)

    if not nudity_detected:
        print(f"Enhancing and reclassifying {image_file}...")
        enhance_image(image_path)
        classify_and_move_image(image_path, image_file)

print("Nudity detection and database cleanup process completed.")
conn.close()
