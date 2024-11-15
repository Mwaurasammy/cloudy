from supabase import create_client
from config import Config

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_presigned_url(file_name):
    response = supabase.storage.from_(Config.SUPABASE_BUCKET).create_signed_url(file_name, expires_in=3600)
    return response.get("signedURL")
