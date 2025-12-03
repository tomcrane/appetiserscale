import requests
from image import scale_dimensions_to_fit, scale_dimensions_to_fit_mine
from operations import _parse_iiif_size_str

dds_raw = requests.get("https://iiif.wellcomecollection.org/dash/Peek/IIIFRaw/b33123354?skipDlcsSizeCheck=true").json()
dlcs_nq = requests.get("https://dlcs.io/iiif-resource/wellcome/preview/5/b33123354").json()

# nb these are not in ascending order of size (yet)
size_params = [
    "1338,",
    "880,",
    "420,",
    "282,",
    "!1024,1024",
    "!400,400",
    "!200,200",
    "!100,100"
]

item = 0
for canvas in dds_raw["items"]:

    dds_sizes = canvas["thumbnail"][0]["service"][0]["sizes"]
    nq_canvas = dlcs_nq["items"][item]
    nq_sizes = nq_canvas["thumbnail"][0]["service"][0]["sizes"]
    nq_sizes.sort(key=lambda size: size["width"]) # nq are descending order

    print()
    source_w = canvas["width"]
    source_h = canvas["height"]
    print(f"{canvas["id"].split("/")[-1]} ({source_w}, {source_h})")

    appetiser_sizes = []
    parsed_sizes = []
    donald_sizes = []
    for sp in size_params:
        parsed_sizes.append(_parse_iiif_size_str(sp, source_w, source_h))
        req_width, req_height = parsed_sizes[-1]
        appetiser_sizes.append(scale_dimensions_to_fit(source_w, source_h, req_width, req_height))
        donald_sizes.append(scale_dimensions_to_fit_mine(source_w, source_h, req_width, req_height))

    appetiser_sizes.sort(key=lambda wh: wh[0])
    parsed_sizes.sort(key=lambda wh: wh[0] or wh[1])
    donald_sizes.sort(key=lambda wh: wh[0])

    counter = 0
    print("  "
          + " | " + "DDS".ljust(12)
          + " | " + "Parsed size".ljust(12)
          + " | " + "Appetiser".ljust(12)
          + " | " + "Donald".ljust(12)
          + " | " + "NQ".ljust(12))
    print("-----------------------------------------------------------------------------")
    for dds_size in dds_sizes:
        dds_w = dds_size['width']
        dds_h = dds_size['height']
        app_w, app_h = appetiser_sizes[counter]
        if dds_w != app_w or dds_h != app_h:
            pfx = "X"
        else:
            pfx = " "
        print(f" {pfx}"
              + " | " + f"({dds_w}, {dds_h})".ljust(12)
              + " | " + f"{parsed_sizes[counter]}".ljust(12)
              + " | " + f"{appetiser_sizes[counter]}".ljust(12)
              + " | " + f"{donald_sizes[counter]}".ljust(12)
              + " | " + f"({nq_sizes[counter]['width']}, {nq_sizes[counter]['height']})".ljust(12))
        counter = counter + 1

    item = item + 1