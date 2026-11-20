import sys,requests
B='https://huggingface.co/datasets/zengxianyu/open-sora-pexels-subset/resolve/main/videos/'
def get(url,a,n):
    r=requests.get(url,headers={'Range':f'bytes={a}-{a+n-1}'},allow_redirects=True,timeout=60); return r.content
shard,vid,out=sys.argv[1:4]
url=requests.head(B+shard,allow_redirects=True).url
off=0
while True:
    h=get(url,off,512)
    name=h[:100].rstrip(b'\0').decode(errors='ignore')
    if not name: print('notfound');break
    size=int(h[124:136].rstrip(b'\0 ').decode() or '0',8)
    if name.endswith(vid+'.mp4'):
        open(out,'wb').write(get(url,off+512,size)); print('ok',name,size); break
    off+=512+((size+511)//512)*512
