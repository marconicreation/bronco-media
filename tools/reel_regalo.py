import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = '/home/user/bronco-media/'
SRC = '/mnt/project-files/video/bronco_higgsfield_shaker.mp4'
CARD = '/mnt/project-files/regali/esempio_giulia.jpg'
OUT = sys.argv[1]
W, H, FPS = 1080, 1920, 30
BIG = ImageFont.truetype(R + 'Bangers-Regular.ttf', 112)
MID = ImageFont.truetype(R + 'Bangers-Regular.ttf', 84)
SM = ImageFont.truetype(R + 'Bangers-Regular.ttf', 64)
YEL = (255, 214, 90)
BG = (38, 22, 14)

def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)

def title(img, txt, t, y=250, font=BIG, fill=YEL):
    d = ImageDraw.Draw(img)
    p = ease(t / 0.35); dy = int((1 - p) * -160)
    d.multiline_text((W // 2, y + dy), txt, font=font, fill=fill, anchor='mm', align='center',
                     stroke_width=8, stroke_fill=(0, 0, 0), spacing=8)

# --- scena 1: clip shaker (8 s) con didascalie in alto
cap1 = [(0, 2.7, "NON SAI COSA\nREGALARE A NATALE?"),
        (2.7, 5.4, "RACCONTAMI CHI È\nIN TRE RIGHE..."),
        (5.4, 8.1, "...E INVENTO UN COCKTAIL\nCOL SUO NOME!")]
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-vf', f'fps={FPS},scale={W}:{H}:flags=lanczos',
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
frames1 = []
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    frames1.append(Image.frombytes('RGB', (W, H), b))
dec.wait()

enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19',
                        '/tmp/claude-0/-home-user/ef19c02f-dc99-5213-a7a3-16a32bccd6fd/scratchpad/v.mp4'],
                       stdin=subprocess.PIPE)

def band(img, h=470):
    ov = Image.new('RGBA', (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(h):
        d.line([(0, y), (W, y)], fill=(20, 10, 5, int(170 * (1 - y / h))))
    img.paste(ov, (0, 0), ov)

for i, f in enumerate(frames1):
    t = i / FPS
    f = f.copy(); band(f)
    for a, b, txt in cap1:
        if a <= t < b: title(f, txt, t - a, y=200)
    frames1[i] = f
    enc.stdin.write(f.tobytes())

# --- scena 2: la card di Giulia (5 s)
card = Image.open(CARD).convert('RGB')
blur = card.resize((W, H)).filter(ImageFilter.GaussianBlur(30))
blur = Image.blend(blur, Image.new('RGB', (W, H), BG), 0.55)
def scene2(t):
    c = blur.copy()
    z = 0.86 + 0.06 * ease(t / 5)
    cw, ch = int(1080 * z), int(1350 * z)
    cc = card.resize((cw, ch), Image.LANCZOS)
    y = 330 + int((1 - ease(t / 0.5)) * 400)
    c.paste(cc, ((W - cw) // 2, y + (1350 - ch) // 2 - 60))
    title(c, "ECCO QUELLO\nDI GIULIA", t, y=175)
    if t > 1.6:
        title(c, "RICETTA + SENZA ALCOL + CARD", t - 1.6, y=1760, font=SM, fill='white')
    return c

# --- scena 3: chiusura (4 s)
logo = Image.open(R + 'tools/bronco_logo.png').convert('RGBA').resize((360, 360))
def scene3(t):
    c = Image.new('RGB', (W, H), BG)
    c.paste(logo, ((W - 360) // 2, 330), logo)
    title(c, "IL COCKTAIL\nCOL TUO NOME", t, y=880)
    if t > 0.5: title(c, "REGALO DI NATALE · 5 €", t - 0.5, y=1130, font=MID, fill='white')
    if t > 1.0: title(c, "ARRIVA PER EMAIL IN 24 ORE", t - 1.0, y=1260, font=SM, fill=(230, 200, 160))
    if t > 1.5: title(c, "ORDINA DAL LINK IN BIO", t - 1.5, y=1500, font=MID)
    ImageDraw.Draw(c).text((W // 2, 1800), "@marconicreation", font=SM, fill=(230, 200, 160), anchor='mm')
    return c

FADE = int(0.4 * FPS)
last1 = frames1[-1]
for k in range(5 * FPS):
    f = scene2(k / FPS)
    if k < FADE: f = Image.blend(last1, f, k / FADE)
    if k >= 5 * FPS - FADE: f = Image.blend(f, scene3(0), (k - (5 * FPS - FADE)) / FADE)
    enc.stdin.write(f.tobytes())
for k in range(4 * FPS):
    enc.stdin.write(scene3(k / FPS).tobytes())
enc.stdin.close(); enc.wait()

dur = len(frames1) / FPS + 9
# audio: traccia dello shaker due volte, dissolvenza finale
subprocess.run(['ffmpeg', '-y', '-v', 'error',
                '-i', '/tmp/claude-0/-home-user/ef19c02f-dc99-5213-a7a3-16a32bccd6fd/scratchpad/v.mp4',
                '-stream_loop', '2', '-i', SRC,
                '-filter_complex', f'[1:a]atrim=0:{dur},afade=t=out:st={dur-2}:d=2[a]',
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
                '-shortest', '-movflags', '+faststart', OUT], check=True)
