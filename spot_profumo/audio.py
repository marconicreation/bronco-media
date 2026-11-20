import numpy as np, wave
SR=44100; D='/tmp/claude-0/spot/'
def note(f,dur,amp=0.15):
    t=np.arange(int(SR*dur))/SR
    s=sum(np.sin(2*np.pi*f*h*t*(1+0.002*np.sin(2*np.pi*5*t)))/h**1.4 for h in range(1,7))
    env=np.minimum(1,t/0.5)*np.minimum(1,(dur-t)/0.4)
    return s*env*amp
def chord(fs,dur): return sum(note(f,dur) for f in fs)
# Am, F, C, E (dramatic), 7.6 s
seq=[([220,261.6,329.6,110],1.9),([174.6,220,261.6,87.3],1.9),([196,261.6,329.6,130.8],1.9),([164.8,207.7,246.9,82.4],1.9)]
x=np.concatenate([chord(c,d) for c,d in seq])
x=x/np.abs(x).max()*0.5
open(D+'archi.raw','wb').write((x*32767).astype('<i2').tobytes())
