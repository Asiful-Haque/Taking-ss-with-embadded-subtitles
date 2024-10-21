import os
import subprocess

# Path to the original screenshots
screenshot_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\screenshots"

# Path to store resized and compressed screenshots
resized_screenshot_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\resized_screenshots"

# Get a list of all .jpg files in the original folder
jpg_files = [f for f in os.listdir(screenshot_folder) if f.endswith('.jpg')]

for jpg_file in jpg_files:
    # Construct full file path
    jpg_file_path = os.path.join(screenshot_folder, jpg_file)

    # Extract filename without extension
    filename = os.path.splitext(jpg_file)[0]

    # Output resized and compressed file path
    output_file = os.path.join(resized_screenshot_folder, f"{filename}.webp")

    # Construct FFmpeg command for resizing and compressing
    cmd = f"ffmpeg -i \"{jpg_file_path}\" -vf \"scale=320:-1\" \"{output_file}\""

    # Execute FFmpeg command and handle errors
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if output.returncode != 0:
        print(f"Error resizing and compressing {jpg_file_path}: {output.stderr}")
    else:
        print(f"Resized and compressed {jpg_file_path} successfully")
