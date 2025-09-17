import torch
from diffusers.utils import load_image
from diffusers import FluxTransformer2DModel

from sdk.pipeline_flux_fill_with_cfg import FluxFillCFGPipeline
from cvat_parser import Dataset

dataset = Dataset()

transformer_onereward = FluxTransformer2DModel.from_pretrained(
    "bytedance-research/OneReward",
    subfolder="flux.1-fill-dev-OneReward-transformer",
    torch_dtype=torch.bfloat16,
    device_map="cuda",
    low_cpu_mem_usage=True,
)

pipe = FluxFillCFGPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-Fill-dev",
    transformer=transformer_onereward,
    torch_dtype=torch.bfloat16,
).to("cuda")

# Image Fill
image_url, mask_url = next(dataset)
image = load_image(image_url)
mask = load_image(mask_url)
image = pipe(
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
image.save("image_fill.jpg")
