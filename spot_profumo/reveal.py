from PIL import Image,ImageFilter,ImageOps,ImageEnhance,ImageDraw
import numpy as np,sys
D='/tmp/claude-0/spot/'
def warm(im):
    a=np.array(im).astype(float); a[...,0]*=1.18; a[...,1]*=1.0; a[...,2]*=0.75
    return Image.fromarray(np.clip(a,0,255).astype('uint8'))
def bgprep(fr):
    bg=ImageOps.fit(fr.convert('RGB'),(1080,1920),centering=(0.25,0.5)).filter(ImageFilter.GaussianBlur(14))
    return warm(ImageEnhance.Brightness(bg).enhance(1.05))
if __name__=='__main__':
    bg=bgprep(Image.open(D+'bgframe.png'))
    f=bg.convert('RGBA'); b=Image.open(D+'L_bronco.png'); m=Image.open(D+'L_tazza.png'); c=Image.open(D+'L_bancone.png')
    m=m.resize((620,620),Image.LANCZOS)
    f.alpha_composite(b,((1080-b.width)//2+60,1920-300-b.height+120))
    f.alpha_composite(c,(0,1620))
    f.alpha_composite(m,(60,1700-m.height+50))
    f.convert('RGB').save(D+'reveal_test.jpg',quality=85)
