"""Trasforma una voce in sussurro: tiene la forma delle parole (inviluppo spettrale) e sostituisce le corde vocali con fiato (rumore).
Uso: sussurro.py in.wav out.wav [quota_sussurro 0..1]"""
import sys, numpy as np, soundfile as sf
from scipy.signal import stft, istft
from scipy.ndimage import uniform_filter1d
x,sr=sf.read(sys.argv[1]); x=x if x.ndim==1 else x.mean(1); q=float(sys.argv[3]) if len(sys.argv)>3 else 0.7
n=1024; f,t,Z=stft(x,sr,nperseg=n,noverlap=n*3//4)
env=uniform_filter1d(np.abs(Z),size=9,axis=0)          # toglie le armoniche, restano le formanti
rng=np.random.default_rng(1); N=stft(rng.standard_normal(len(x)),sr,nperseg=n,noverlap=n*3//4)[2]
N=N/ (np.abs(N).mean()+1e-9)
tilt=np.clip(f/1500,0.25,1.6)[:,None]                    # il fiato ha piu' acuti
_,w=istft(env*N[:,:env.shape[1]]*tilt,sr,nperseg=n,noverlap=n*3//4)
w=w[:len(x)]; w=np.pad(w,(0,len(x)-len(w)))
w*= np.sqrt((x**2).mean())/ (np.sqrt((w**2).mean())+1e-9)
y=q*w+(1-q)*x; y/=max(1e-9,np.abs(y).max())/0.8
sf.write(sys.argv[2],y,sr)
