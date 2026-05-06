from django.core.exceptions import ValidationError

def validate_file_size(value):
        filesize = value.size
        
        # Limit to 1MB (expressed in bytes)
        limit = 1 * 1024 * 1024 
        if filesize > limit:
            raise ValidationError("The maximum file size that can be uploaded is 1MB")
        return value
