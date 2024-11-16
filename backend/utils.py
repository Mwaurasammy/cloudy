from supabase import create_client
from config import Config
import logging

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)

# Create the Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_presigned_url(file_name):
    try:
        # Ensure the file path includes the appropriate directory if needed
        file_path = f"{Config.SUPABASE_BUCKET}/{file_name}"
        logging.debug(f"Attempting to generate signed URL for file: {file_path} in bucket: {Config.SUPABASE_BUCKET}")
        
        # Create a signed URL for a new file upload, set to expire in 3600 seconds (1 hour)
        response = supabase.storage.from_(Config.SUPABASE_BUCKET).create_signed_url(file_path, expires_in=3600)

        # Log the response for debugging
        logging.debug(f"Supabase Response: {response}")

        # Check if the signed URL was successfully returned
        if "signed_url" in response:
            return response["signed_url"]
        else:
            # If the signed URL isn't in the response, raise an exception
            raise Exception(f"Failed to get signed URL. Response: {response}")
    except Exception as e:
        # Log the error with more details
        logging.error(f"Error generating presigned URL: {e}")
        return None
