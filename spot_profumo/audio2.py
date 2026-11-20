import numpy as np
SR=44100; D='/tmp/claude-0/spot/'
def note(f,dur,amp=0.15,att=0.9,rel=0.9):
    t=np.arange(int(SR*dur))/SR
    s=sum(np.sin(2*np.pi*f*h*t*(1+0.003*np.sin(2*np.pi*5.2*t+h)))/h**1.5 for h in range(1,7))
    env=np.minimum(1,t/att)*np.minimum(1,(dur-t)/rel)
    return s*env*amp
A=[220,261.6,329.6,110]; F=[174.6,220,261.6,87.3]; C=[196,261.6,329.6,130.8]; G=[196,246.9,293.7,98]; E=[164.8,207.7,246.9,82.4]; Dm=[174.6,220,293.7,146.8]
seq=[(A,3.2),(F,3.0),(C,3.0),(G,3.0),(Dm,3.0),(E,3.0),(A,4.8)]
N=int(SR*22); x=np.zeros(N+SR*2); pos=0
for c,d in seq:
    seg=sum(note(f,d+0.8) for f in c); i=int(pos*SR); x[i:i+len(seg)]+=seg; pos+=d
# fade in/out
x=x[:N]; t=np.arange(N)/SR; x*=np.minimum(1,t/1.5)*np.minimum(1,(22-t)/1.5)
x=x/np.abs(x).max()*0.5
open(D+'archi2.raw','wb').write((x*32767).astype('<i2').tobytes())
