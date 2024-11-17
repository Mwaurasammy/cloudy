# from supabase import create_client
from config import Config
import os


# # Create the Supabase client
# supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

# def upload_file(bucket_name, file_path, file_content):
#     try:
#         response = supabase.storage.from_(Config.SUPABASE_BUCKET).upload(file_path, file_content)
#         if response.get("error"):
#             raise Exception(response["error"])
#         return {"url": f"{Config.SUPABASE_URL}/storage/v1/object/public/{Config.SUPABASE_BUCKET}/{file_path}"}
#     except Exception as e:
#         print(f"Error uploading file: {e}")
#         return None
def upload_file(bucket_name, file_path, file_content):
    # Example using supabase-py (Python client for Supabase)
    try:
        from supabase import create_client, Client
        supabase_url = Config.SUPABASE_URL
        supabase_key = Config.SUPABASE_KEY
        supabase: Client = create_client(supabase_url, supabase_key)

        # Upload the file
        response = supabase.storage.from_(bucket_name).upload(file_path, file_content)
        if response.status_code == 200:
            return response.data  # or whatever response data structure you're using
        else:
            print(f"Error uploading file: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred during upload: {e}")
        return None