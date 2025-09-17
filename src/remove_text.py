import torch
from tqdm import tqdm
from itertools import islice
from diffusers.utils import load_image
from diffusers import FluxTransformer2DModel

from sdk.pipeline_flux_fill_with_cfg import FluxFillCFGPipeline
from cvat_parser import FluxDataset, FluxData
from gfs.temp import filename
from gfs.store import remote


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
        return remote(output_path)


if __name__ == "__main__":
    dataset = FluxDataset()
    # remover = TextRemover()
    max_iter = 5
    for data in tqdm(islice(dataset, max_iter), total=max_iter):
        pass
