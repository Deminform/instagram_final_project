POST_DESCRIPTION_MAX_LENGTH = 500
POST_DESCRIPTION_MIN_LENGTH = 2


COMMENT_MAX_LENGTH = 500
COMMENT_MIN_LENGTH = 2

TAG_MAX_LENGTH = 50
TAG_MIN_LENGTH = 2

SCORE_MAX_VALUE = 5
SCORE_MIN_VALUE = 1

EDITED_IMAGE_URL = 'edited_image_url'
ORIGINAL_IMAGE_URL = 'original_image_url'

FILTER_DICT = {
    "grayscale": {"effect": "grayscale"},
    "thumbnail": {"width": 150, "height": 150, "crop": "thumb"},
    "blur": {"effect": "blur:100"},
    "sepia": {"effect": "sepia"},
}