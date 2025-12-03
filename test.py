import requests
from image import scale_dimensions_to_fit, scale_dimensions_to_fit_mine
from operations import _parse_iiif_size_str

b_nums = [
    "b33123354",
    "b33118929",
    "b24738815",
    "b24723757",
    "b24390768",
    "b33668851",
    "b3367212x",
    "b33672064"
]

unfixed_images = []

for b_num in b_nums:
    dds_raw = requests.get(f"https://iiif.wellcomecollection.org/dash/Peek/IIIFRaw/{b_num}?skipDlcsSizeCheck=true").json()
    dlcs_nq = requests.get(f"https://dlcs.io/iiif-resource/wellcome/preview/5/{b_num}").json()

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
        image_name = canvas["id"].split("/")[-1]
        print(f"{image_name} ({source_w}, {source_h})")

        appetiser_sizes = []
        parsed_sizes = []
        donald_sizes = []
        for sp in size_params:
            parsed_sizes.append({
                "param": sp,
                "parsed": _parse_iiif_size_str(sp, source_w, source_h)
            })
            req_width, req_height = parsed_sizes[-1]["parsed"]
            appetiser_sizes.append(scale_dimensions_to_fit(source_w, source_h, req_width, req_height))
            donald_sizes.append(scale_dimensions_to_fit_mine(source_w, source_h, req_width, req_height))

        appetiser_sizes.sort(key=lambda wh: wh[0])
        parsed_sizes.sort(key=lambda ps: ps["parsed"][0] or ps["parsed"][1])
        donald_sizes.sort(key=lambda wh: wh[0])

        counter = 0
        print("  |  "
              + " | " + "iiif size".ljust(12)
              + " | " + "DDS".ljust(12)
              + " | " + "Parsed size".ljust(12)
              + " | " + "Appetiser".ljust(12)
              + " | " + "Donald".ljust(12)
              + " | " + "NQ".ljust(12))
        print("----------------------------------------------------------------------------------------------")
        is_not_fixed = False
        for dds_size in dds_sizes:
            dds_w = dds_size['width']
            dds_h = dds_size['height']
            app_w, app_h = appetiser_sizes[counter]
            pfx = " "
            fix = " "
            if dds_w != app_w or dds_h != app_h:
                pfx = "X"
                if dds_w == donald_sizes[counter][0] and dds_h == donald_sizes[counter][1]:
                    fix = "Y"
                else:
                    is_not_fixed = True

            print(f"{pfx}"
                  + " | " + fix
                  + " | " + f"{parsed_sizes[counter]["param"]}".ljust(12)
                  + " | " + f"({dds_w}, {dds_h})".ljust(12)
                  + " | " + f"{parsed_sizes[counter]["parsed"]}".ljust(12)
                  + " | " + f"{appetiser_sizes[counter]}".ljust(12)
                  + " | " + f"{donald_sizes[counter]}".ljust(12)
                  + " | " + f"({nq_sizes[counter]['width']}, {nq_sizes[counter]['height']})".ljust(12))
            counter = counter + 1

        if is_not_fixed:
            unfixed_images.append(image_name)

        item = item + 1

print()
print("Unfixed images:")
for unfixed_image in unfixed_images:
    print(unfixed_image)