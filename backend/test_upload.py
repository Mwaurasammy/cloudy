import os
from supabase_client import upload_file_to_storage  # Adjust this import as needed
from flask import current_app as app

# Path to the image file you want to test
file_path = '/home/mgridge/Pictures/Screenshots/Screenshot from 2024-10-22 12-12-12.png'
user_id = 27  # Replace this with the appropriate user ID

# Read the file content
with open(file_path, 'rb') as file:
    file_content = file.read()

# Get the file name (without the path)
file_name = os.path.basename(file_path)

# Push the Flask app context and call the upload function inside it
with app.app_context():
    result = upload_file_to_storage(file_name, file_content, user_id)

# Print the result
print(result)
