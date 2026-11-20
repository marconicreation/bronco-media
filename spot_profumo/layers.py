from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
D='/tmp/claude-0/spot/'
W,H=1080,1920
# bronco: clean alpha
b=Image.open(D+'bronco_cut_local.png').convert('RGBA')
a=np.array(b.split()[3]).astype(float)
a=np.clip((a-90)/(200-90),0,1)*255
b.putalpha(Image.fromarray(a.astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)))
b=b.crop(b.getbbox())
bw=1000; b=b.resize((bw,int(b.height*bw/b.width)),Image.LANCZOS)   # downscale from 2528
b.save(D+'L_bronco.png')
# mug
m=Image.open(D+'tazza_cut.png').convert('RGBA'); m=m.crop(m.getbbox())
mw=560; m=m.resize((mw,int(m.height*mw/m.width)),Image.LANCZOS); m.save(D+'L_tazza.png')
# counter from photo
p=Image.open('/mnt/project-files/gadget/foto/bronco_tango_foto.jpg').convert('RGB')
wood=p.crop((0,1720,2000,2000)).resize((W,300),Image.LANCZOS)
wood=ImageEnhance.Brightness(wood).enhance(0.85)
c=Image.new('RGBA',(W,300)); c.paste(wood,(0,0))
# top highlight edge
d=ImageDraw.Draw(c); d.rectangle((0,0,W,10),fill=(120,70,35,255)); d.line((0,10,W,10),fill=(60,30,15,255),width=3)
c.save(D+'L_bancone.png')
print(b.size,m.size)
