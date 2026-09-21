# SeedVR2 Upscaler

A simple plug-and-play ComfyUI workflow for upscaling images with SeedVR2.

## Setup

### 1. Download the models

**SeedVR2 model**  
https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_int8_convrot.safetensors

Put it here:
```text
ComfyUI/models/diffusion_models/
```

**SeedVR2 VAE**  
https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/vae/seedvr2_ema_vae_fp16.safetensors

Put it here:
```text
ComfyUI/models/vae/
```

Restart or refresh ComfyUI after adding the files.

## Use

1. Open the workflow in ComfyUI.
2. Load your image into the **Load Image** node.
3. Press **Queue Prompt**.
4. Find the result in:
   `ComfyUI/output/upscaled/`

That's it.

## Changing the size

The default **Target Length** is **3840 px**.

Change it in the **Target Length** node if needed.

Common values:
- `2048` — lighter/faster
- `3072` — good general size
- `3840` — default
- `5120` — larger, heavier

## Notes

The workflow also includes an image comparison so you can quickly check the original against the upscale.

### If ComfyUI says a model is missing

Check that the filenames and folders match exactly:

```text
ComfyUI/models/diffusion_models/seedvr2_7b_int8_convrot.safetensors
ComfyUI/models/vae/seedvr2_ema_vae_fp16.safetensors
```

## Model

SeedVR2 by Comfy-Org:
https://huggingface.co/Comfy-Org/SeedVR2
