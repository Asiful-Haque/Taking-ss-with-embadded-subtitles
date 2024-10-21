import os
import mysql.connector
import subprocess

def format_timecode(timecode):
    time_parts = timecode.split(",")
    milliseconds = time_parts[1].zfill(3)  # Pad milliseconds with zeros
    formatted_time = time_parts[0] + '.' + milliseconds
    return formatted_time

# Function to check if subtitles exist
def has_subtitles(video_path):
    cmd_check = f"ffmpeg -i \"{video_path}\""
    result = subprocess.run(cmd_check, shell=True, capture_output=True, text=True)
    return "Stream #0:" in result.stderr and "Subtitle" in result.stderr

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

# Paths
video_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\Series"
srt_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\sub"
screenshot_folder = r"C:\Users\USER\Documents\Screenshot_Part\test\screenshots"

# Check if folders exist, create screenshot folder if missing
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

print("Script started...")

# Check if video folder exists
if os.path.exists(video_folder):
    print("Video folder exists.")
    
    # List video files
    video_files = [file for file in os.listdir(video_folder) if file.endswith(('.mp4', '.mkv'))]
    print(f"Found {len(video_files)} video files.")
    
    for video_file in video_files:
        print(f"Processing video file: {video_file}")
        video_path = os.path.join(video_folder, video_file)
        basename = os.path.splitext(video_file)[0]

        # Construct SRT file path
        srt_file = os.path.join(srt_folder, f"{basename}.srt")

        # Check for subtitles before attempting to extract
        if has_subtitles(video_path):
            # Construct FFmpeg command to extract subtitles
            cmd = f"ffmpeg -i \"{video_path}\" -map 0:s:0 \"{srt_file}\""
            print(f"Running command: {cmd}")

            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)  # 60 seconds timeout
                if result.returncode != 0:
                    print(f"Error executing FFmpeg command for {video_file}: {result.stderr}")
                    continue
            except subprocess.TimeoutExpired:
                print(f"FFmpeg command timed out for {video_file}.")
                continue

            print(f"Extracted SRT from {video_file}")

            # Read and parse SRT data
            if os.path.exists(srt_file):
                with open(srt_file, 'r', encoding='utf-8') as srt:
                    srtData = srt.read()

                # Split SRT into individual subtitles
                subtitles = [subtitle for subtitle in srtData.strip().split("\n\n") if subtitle]

                for subtitle in subtitles:
                    subtitleLines = subtitle.split("\n")

                    # Extract start and end timestamps
                    timestamps = subtitleLines[1].split(" --> ")
                    start_time = format_timecode(timestamps[0])
                    end_time = format_timecode(timestamps[1])

                    # Clean up subtitle text
                    cleanedSubtitle = subtitleLines[2].strip()

                    if len(cleanedSubtitle) >= 20:  # Only process subtitles with at least 20 characters
                        escapedSubtitle = conn.converter.escape(cleanedSubtitle)

                        # Insert subtitle and timestamps into database
                        insert_query = (
                            "INSERT INTO sub (start_time, end_time, subs, series_season_episode) "
                            f"VALUES ('{start_time}', '{end_time}', '{escapedSubtitle}', '{basename}')"
                        )
                        try:
                            cursor = conn.cursor()
                            cursor.execute(insert_query)
                            conn.commit()
                            print(f"Inserted subtitle into database for {basename} at {start_time}")
                        except mysql.connector.Error as err:
                            print(f"Error inserting subtitle into database: {err}")
                            continue

                        # Generate screenshot filename and path
                        # Replace colons with hyphens in the filename
                        safe_start_time = start_time.replace(":", "-")
                        screenshot_filename = f"{basename}_{safe_start_time}.jpg"
                        screenshot_path = os.path.join(screenshot_folder, screenshot_filename)

                        # Capture frame using FFmpeg
                        cmd_screenshot = f"ffmpeg -ss {start_time} -i \"{video_path}\" -t 1 -vframes 1 -update 1 \"{screenshot_path}\""
                        print(f"Capturing screenshot: {cmd_screenshot}")

                        try:
                            result_screenshot = subprocess.run(cmd_screenshot, shell=True, capture_output=True, text=True, timeout=60)
                            if result_screenshot.returncode != 0:
                                print(f"Error capturing frame at {start_time}: {result_screenshot.stderr}")
                                continue
                        except subprocess.TimeoutExpired:
                            print(f"Screenshot command timed out for {video_file} at {start_time}.")
                            continue

                        # Convert captured frame to .webp for compression
                        webp_screenshot_filename = f"{basename}_{safe_start_time}.webp"
                        webp_screenshot_path = os.path.join(screenshot_folder, webp_screenshot_filename)

                        cmd_webp = f"ffmpeg -i \"{screenshot_path}\" -vf \"scale=240:-1\" -c:v webp -b:v 240K \"{webp_screenshot_path}\""
                        print(f"Converting to webp: {cmd_webp}")

                        try:
                            result_webp = subprocess.run(cmd_webp, shell=True, capture_output=True, text=True, timeout=60)
                            if result_webp.returncode != 0:
                                print(f"Error converting to webp: {result_webp.stderr}")
                                continue
                        except subprocess.TimeoutExpired:
                            print(f"WebP conversion command timed out for {screenshot_filename}.")
                            continue

                        # Update database with the screenshot link
                        screenshot_link = f'http://localhost/screenshot_project/screenshots/{webp_screenshot_filename}'
                        update_query = (
                            "UPDATE sub SET screenshot_link = %s "
                            "WHERE start_time = %s AND series_season_episode = %s"
                        )
                        try:
                            cursor.execute(update_query, (screenshot_link, start_time, basename))
                            conn.commit()
                            print("Screenshot link updated in database")
                        except mysql.connector.Error as err:
                            print(f"Error updating screenshot link: {err}")
                    else:
                        print(f"Skipped subtitle with less than 20 characters: {cleanedSubtitle}")
            else:
                print(f"SRT file not found for {video_file}")
        else:
            print(f"No subtitle stream found in {video_file}. Skipping subtitle extraction.")

else:
    print("Video folder does not exist.")

print("Script finished.")
conn.close()
