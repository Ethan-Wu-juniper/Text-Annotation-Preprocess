import json
import torch
from tqdm import tqdm
from diffusers.utils import load_image
from diffusers import FluxTransformer2DModel

from sdk.pipeline_flux_fill_with_cfg import FluxFillCFGPipeline
from cvat_parser import FluxDataset, FluxData
from gfs.temp import filename
from gfs.utils.gs import upload_to_gs_uri
from gfs.anyuri import GSUri
from gfs.store import remote
from constant import GSDIR


class TextRemover:
    def __init__(self):
        transformer_onereward = FluxTransformer2DModel.from_pretrained(
            "bytedance-research/OneReward",
            subfolder="flux.1-fill-dev-OneReward-transformer",
            torch_dtype=torch.bfloat16,
        )

        self.pipe = FluxFillCFGPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-Fill-dev",
            transformer=transformer_onereward,
            torch_dtype=torch.bfloat16,
        ).to("cuda")

    def run(self, data: FluxData):
        image = load_image(data.image)
        mask = load_image(data.mask)
        image = self.pipe(
            prompt="remove",
            negative_prompt="nsfw",
            image=image,
            mask_image=mask,
            height=image.height,
            width=image.width,
            guidance_scale=1.0,
            true_cfg=4.0,
            num_inference_steps=50,
            generator=torch.Generator("cpu").manual_seed(0),
        ).images[0]

        output_path = filename(".jpg")
        image.save(output_path)
        return remote(output_path, location=GSDIR)


if __name__ == "__main__":
    dataset = FluxDataset()
    remover = TextRemover()
    metadata_path = "metadata.json"
    with open(metadata_path, "r") as fp:
        metadata = json.load(fp)

    for data in tqdm(
        dataset, total=len(dataset), desc=f"running {dataset._current_frame_index} data"
    ):
        result = remover.run(data)
        metadata[data.frame_number] = result

    with open(metadata_path, "w") as fp:
        json.dump(metadata, fp)
    upload_to_gs_uri(metadata_path, GSUri(f"{GSDIR}/metadata.json"))
