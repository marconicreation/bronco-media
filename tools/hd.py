"""Posa in alta definizione per i primi piani della sitcom (Robi 18/11: "immagini sgranate").
Uso: python3 tools/hd.py sitcom/pose/NOME.jpg   -> crea sitcom/pose/hd/NOME.jpg (2x, waifu2x cunet art, gratis, sul computer cloud)
sitcom.py usa da solo la versione hd quando esiste."""
import sys, os, subprocess, numpy as np, onnxruntime as ort
from PIL import Image
MOD = '/tmp/waifu2x_cunet_art_noise1_scale2x.onnx'
if not os.path.exists(MOD):
    subprocess.run(['curl', '-sL', '-o', MOD, 'https://huggingface.co/deepghs/waifu2x_onnx/resolve/main/20230202/onnx_models/cunet/art/noise1_scale2x.onnx'], check=True)
s = ort.InferenceSession(MOD); name = s.get_inputs()[0].name
src = sys.argv[1]; dst = os.path.join(os.path.dirname(src), 'hd', os.path.basename(src)); os.makedirs(os.path.dirname(dst), exist_ok=True)
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255
H, W, _ = im.shape; P = 18; T = 256
pad = np.pad(im, ((P, P + T), (P, P + T), (0, 0)), mode='reflect')
out = np.zeros((2 * H + 2 * T, 2 * W + 2 * T, 3), np.float32)
for y in range(0, H, T):
    for x in range(0, W, T):
        t = pad[y:y + T + 2 * P, x:x + T + 2 * P].transpose(2, 0, 1)[None]
        r = s.run(None, {name: t})[0][0].transpose(1, 2, 0)
        out[2 * y:2 * y + 2 * T, 2 * x:2 * x + 2 * T] = r
out = np.clip(out[:2 * H, :2 * W], 0, 1)
Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(dst, quality=92); print(dst)
