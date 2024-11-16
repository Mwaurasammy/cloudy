from supabase import create_client
from config import Config

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_presigned_url(file_name):
    try:
        response = supabase.storage.from_(Config.SUPABASE_BUCKET).create_signed_url(file_name, expires_in=3600)
        print(response)  # Check the full response to debug
        if "signedURL" in response:
            return response["signedURL"]
        else:
            raise ValueError("Failed to generate presigned URL: No 'signedURL' found in response")
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

