POST_DESCRIPTION_MAX_LENGTH = 1500
POST_DESCRIPTION_MIN_LENGTH = 2

COMMENT_MAX_LENGTH = 1500
COMMENT_MIN_LENGTH = 2

TAG_NUMBER_LIMIT=5
TAG_MAX_LENGTH = 30
TAG_MIN_LENGTH = 2

SCORE_MAX_VALUE = 5
SCORE_MIN_VALUE = 1

EDITED_IMAGE_URL = "edited_image_url"
ORIGINAL_IMAGE_URL = "original_image_url"

FILTER_DICT = {
    "grayscale": {"effect": "grayscale"},
    "thumbnail": {"width": 150, "height": 150, "crop": "thumb"},
    "blur": {"effect": "blur:1000"},
    "crop": {"width": 1080, "height": 1080, "crop": "fill"},
    "negate": {"effect": "negate"},
    "vignette": {"effect": "vignette:1000"},
    "brightness": {"effect": "brightness:1000"},
    "contrast": {"effect": "contrast:10000000"},
    "saturation": {"effect": "saturation:1000"},
    "hue": {"effect": "hue:120"},
    "invert": {"effect": "invert"},
    "sharpen": {"effect": "sharpen:100"},
    "noise": {"effect": "noise:1000"},
    "oil_painting": {"effect": "oil_paint:3"},
    "pixelate": {"effect": "pixelate:20"},
    "posterize": {"effect": "posterize:5"},
}