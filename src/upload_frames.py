import json

from tqdm import tqdm
from cvat_parser import FluxDataset
from gfs.utils.gs import upload_to_gs_uri
from gfs.store import remote
from gfs.anyuri import GSUri
from constant import FRAMEDIR, MASKDIR

frame_metadata = {}
mask_metadata = {}
frame_metadata_path = "frame_metadata.json"
mask_metadata_path = "mask_metadata.json"

dataset = FluxDataset()
for data in tqdm(
    dataset, total=len(dataset), desc=f"start from {dataset._current_frame_index}"
):
    frame = remote(data.image, location=FRAMEDIR)
    mask = remote(data.mask, location=MASKDIR)
    frame_metadata[data.frame_number] = frame
    mask_metadata[data.frame_number] = mask

with open(frame_metadata_path, "w") as fp:
    json.dump(frame_metadata, fp)
with open(mask_metadata_path, "w") as fp:
    json.dump(mask_metadata, fp)

upload_to_gs_uri(frame_metadata_path, GSUri(f"{FRAMEDIR}/metadata.json"))
upload_to_gs_uri(mask_metadata_path, GSUri(f"{MASKDIR}/metadata.json"))
