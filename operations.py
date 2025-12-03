import re

import logging

logger = logging.getLogger(__name__)

IIIF_SIZE_STR_PATTERN = re.compile(
    r"^!(?P<img_width>\d+),(?P<img_height>\d+)$|^\^(?P<upscale_width>\d+),(?P<upscale_height>\d+)$|^(?P<width>\d+),(?P<height>\d+)$|^\^(?P<upscale_just_width>\d+),$|^(?P<just_width>\d+),$|^\^,(?P<upscale_just_height>\d+)$|^,(?P<just_height>\d+)$"
)

def _parse_iiif_size_str(
    iiif_size_str: str, src_width: int, src_height: int
) -> tuple[(int | None), (int | None)]:
    pattern_match = IIIF_SIZE_STR_PATTERN.match(iiif_size_str)
    if not pattern_match:
        raise ValueError(f"Invalid IIIF Size string: {iiif_size_str=}")
    match_groups = pattern_match.groupdict()
    logger.debug(f"Parsing: {iiif_size_str=}")
    logger.debug(f"Source image size: {src_width}, {src_height}")
    # iiif_size_str is like f"!{img_width},{img_height}"
    # !w,h
    # The extracted region is scaled so that the width and height of the returned image are not greater than w and h, while maintaining the aspect ratio.
    # The returned image must be as large as possible but not larger than the extracted region, w or h, or server-imposed limits.
    if match_groups["img_width"] and match_groups["img_height"]:
        logger.debug("Match like `!w,h`")
        img_width = int(match_groups["img_width"])
        img_height = int(match_groups["img_height"])
        logger.debug(f"Matched: {img_width=} {img_height=}")
        if img_width >= src_width and img_height >= src_height:
            width = None
            height = None
        else:
            if src_width >= src_height:
                width = img_width
                height = None
            else:
                width = None
                height = img_height
    # iiif_size_str is like f"^{upscale_width},{upscale_height}"
    # ^w,h
    # The width and height of the returned image are exactly w and h.
    # The aspect ratio of the returned image may be significantly different than the extracted region, resulting in a distorted image.
    # If w and/or h are greater than the corresponding pixel dimensions of the extracted region, the extracted region is upscaled.
    elif match_groups["upscale_width"] and match_groups["upscale_height"]:
        logger.debug("Match like `^w,h`")
        width = int(match_groups["upscale_width"])
        height = int(match_groups["upscale_height"])
        logger.debug(f"Matched: {width=} {height=}")
    # iiif_size_str is like f"{width},{height}"
    # w,h
    # The width and height of the returned image are exactly w and h.
    # The aspect ratio of the returned image may be significantly different than the extracted region, resulting in a distorted image.
    # The values of w and h must not be greater than the corresponding pixel dimensions of the extracted region.
    elif match_groups["width"] and match_groups["height"]:
        logger.debug("Match like `w,h`")
        width = int(match_groups["width"])
        height = int(match_groups["height"])
        logger.debug(f"Matched: {width=} {height=}")
        if width >= src_width and height >= src_height:
            width = None
            height = None
        elif width >= src_width:
            width = src_width
        elif height >= src_height:
            height = src_height
    # iiif_size_str is like f"^{upscale_just_width},"
    # ^w,
    # The extracted region should be scaled so that the width of the returned image is exactly equal to w.
    # If w is greater than the pixel width of the extracted region, the extracted region is upscaled.
    elif match_groups["upscale_just_width"]:
        logger.debug("Match like `^w,`")
        width = int(match_groups["upscale_just_width"])
        logger.debug(f"Matched: {width=}")
        height = None
    # iiif_size_str is like f"{just_width},"
    # w,
    # The extracted region should be scaled so that the width of the returned image is exactly equal to w.
    # The value of w must not be greater than the width of the extracted region.
    elif match_groups["just_width"]:
        logger.debug("Match like `w,`")
        just_width = int(match_groups["just_width"])
        logger.debug(f"Matched: {just_width=}")
        width = just_width
        if just_width >= src_width:
            width = None
        height = None
    # iiif_size_str is like f"^,{upscale_just_height}"
    # ^,h
    # The extracted region should be scaled so that the height of the returned image is exactly equal to h.
    # If h is greater than the pixel height of the extracted region, the extracted region is upscaled.
    elif match_groups["upscale_just_height"]:
        logger.debug("Match like `^,h`")
        width = None
        height = int(match_groups["upscale_just_height"])
        logger.debug(f"Matched: {height=}")
    # iiif_size_str is like f",{just_height}"
    # ,h
    # The extracted region should be scaled so that the height of the returned image is exactly equal to h.
    # The value of h must not be greater than the height of the extracted region.
    elif match_groups["just_height"]:
        logger.debug("Match like `,h`")
        width = None
        just_height = int(match_groups["just_height"])
        logger.debug(f"Matched: {just_height=}")
        height = just_height
        if just_height >= src_height:
            height = None
    else:
        raise ValueError(f"Invalid IIIF Size string: {iiif_size_str=}")

    logger.debug(f"Parsed image size: ({height=}, {width=})")
    return width, height