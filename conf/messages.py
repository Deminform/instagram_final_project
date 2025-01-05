from conf import const

ACCOUNT_EXIST = "Account already exists"
INCORRECT_CREDENTIALS = "Incorrect username or password"
EMAIL_NOT_CONFIRMED = "Email not confirmed"
EMAIL_CONFIRMED = "Email verified successfully"
EMAIL_ALREADY_CONFIRMED = "Your email is already confirmed"
INCORRECT_REFRESH_TOKEN = "Could not validate credentials"
VERIFICATION_FAILED = "Verification failed"
FORBIDDEN = "You do not have permission to perform this action"
LOGOUT_SUCCESS = "Logout Successfully"
INTERNAL_SERVER_ERROR = "Internal Server Error"
BANNED = "You are banned"
ALREADY_BANNED = "User is already banned"
NOT_BANNED = "User is already not banned"
POST_ALREADY_EXISTS = "Post already exists"
POST_NOT_FOUND = "Post not found"
TAG_NOT_FOUND = "Tag not found"
USER_NOT_FOUND = "User not found"
INVALID_SCOPE_TOKEN = "Invalid scope token"
INVALID_TOKEN_DATA = "Invalid token data"
DATABASE_IS_NOT_AVAILABLE = "Database is not available"
DATABASE_IS_HEALTHY = "Database is healthy"
DATA_INTEGRITY_ERROR = "Data integrity error."
DATA_NOT_UNIQUE = "Data already exist."
TAG_NUMBER_LIMIT = f"Maximum number of tags is {const.TAG_NUMBER_LIMIT}"
TAG_NAME_LIMIT = f"Maximum length of tag name is {const.TAG_MAX_LENGTH}"
TAG_DESCRIPTION = f"Tags may be separated by commas, an example: 'tag1,tag2,tag3', up to {const.TAG_NUMBER_LIMIT} tags"
IMAGE_FILTER_DESCRIPTION = "Image filter, an example: 'blur'"
POST_DESCRIPTION = f"Post description, an example: 'This is a test post', minimum {const.POST_DESCRIPTION_MIN_LENGTH} character, up to {const.POST_DESCRIPTION_MAX_LENGTH} characters and can`t be empty"

SCORE_WARNING_SELF_SCORE="Users cannot score their posts"

UPLOAD_IMAGE_ERROR = "Upload image failed"
FILTER_IMAGE_ERROR = "Filter image failed"
FILTER_IMAGE_ERROR_DETAIL = "Filter name is incorrect"

QR_NOT_FOUND = "QR code not found"

NOT_COMMENT = "Comment not found or not available."

# TODO REPLACE ALL ERROR MESSAGES IN PROJECT
