import decimal
import logging

logger = logging.getLogger(__name__)



def scale_dimensions_to_fit(
    width: int, height: int, req_width: int | None, req_height: int | None
) -> tuple[int, int]:
    """For a given width and height, scale these such that they will fit within
    the required height and width by reducing them by an appropriate scale
    factor.
    Setting the precision of the Decimal context _may_ be included to allow
    for parity with .net components that use this precision (i.e. no off-by-one
    scaling issues).
    """
    decimal.getcontext().prec = 17

    dec_width = decimal.Decimal(width)
    dec_height = decimal.Decimal(height)
    width_scale = decimal.Decimal(0.0)
    if req_width:
        dec_req_width = decimal.Decimal(req_width)
        width_scale = dec_req_width / dec_width

    height_scale = decimal.Decimal(0.0)
    if req_height:
        dec_req_height = decimal.Decimal(req_height)
        height_scale = dec_req_height / dec_height

    if not height_scale and width_scale:
        height_scale = width_scale
    if not width_scale and height_scale:
        width_scale = height_scale
    logger.debug(
        f"Scale factor calculated as: ({width_scale=}, {height_scale=}, {width=}, {height=}, {req_width=}, {req_height=})",
    )
    scaled_int_width = int((dec_width * width_scale).to_integral_exact())
    scaled_int_height = int((dec_height * height_scale).to_integral_exact())
    logger.debug(
        f"Scaled image dimensions: ({dec_width=}, {dec_height=}, {scaled_int_width=}, {scaled_int_height=})",
    )
    return scaled_int_width, scaled_int_height


def scale_dimensions_to_fit_mine(
    width: int, height: int, req_width: int | None, req_height: int | None
) -> tuple[int, int]:
    dec_width = decimal.Decimal(width)
    dec_height = decimal.Decimal(height)

    if req_width and req_height:
        # this is confined - we don't support mutation
        # all cribbed from old Appetiser
        dec_req_width = decimal.Decimal(req_width)
        dec_req_height = decimal.Decimal(req_height)
        scale = min(dec_req_width/dec_width, dec_req_height/dec_height)
        scaled_int_width = int((dec_width * scale).to_integral_exact())
        scaled_int_height = int((dec_height * scale).to_integral_exact())
        return scaled_int_width, scaled_int_height

    # if we are here we have width OR height. This doesn't handle confined requests
    final_width = int(req_width if req_width else width * req_height / dec_height)
    final_height = int(req_height if req_height else height * req_width / dec_width)
    return final_width, final_height

