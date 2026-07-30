#!/usr/bin/env python3
"""
generate_banner.py  -  Phase 1: GitHub Profile Banner
pushkarrd/pushkarrd

Run:
    python banner/generate_banner.py --photo banner/photo.png

Outputs (in ./banner/):
    dark.svg          - GitHub dark mode
    light.svg         - GitHub light mode
    dots_dark.npy     - source-of-truth grid  (KEEP)
    dots_light.npy    - source-of-truth grid  (KEEP)

Requirements: pip install pillow numpy scipy
"""

import argparse, math, os
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from scipy.ndimage import binary_closing, binary_fill_holes, label as sp_label
from scipy.spatial import KDTree

DOT_D  = "#A78BFA"; DOT_L  = "#7C3AED"
CHR_D  = "#22D3EE"; CHR_L  = "#0891B2"
ACC    = "#10B981";  BG_D   = "#0A101F"; BG_L  = "#F0F4FF"
LIVE_C = "#EF4444";  LEAD_D = "#1E3A5F"; LEAD_L= "#94A3B8"
VAL_D  = "#CBD5E1";  VAL_L  = "#1E293B"
TB_D   = "#0D1526";  TB_L   = "#E2E8F0"

SW,SH=1180,610; TB_H=36; L_W=448; PAD=14
PORT_X=PAD; PORT_Y=TB_H+22; PORT_W=L_W-PAD*2; PORT_H=SH-PORT_Y-PAD; R_X=L_W+PAD
GW,GH=175,200; GPX=PORT_W/GW; GPY=PORT_H/GH; DS=0.65
N_INTRO=60; N_BANDS=94; N_TRAV=900; LOOP=14.2
T_P=3.0;T_D=4.3;T_L1=6.3;T_12=7.6;T_L2=9.6;T_23=10.9;T_L3=12.9;T_R=14.2
CW=7.8

INFO_ROWS=[
    ("Subject",       "Pushkar R Deshpande"),
    ("Role",          "Full-Stack Dev \u00b7 Open Source Explorer"),
    ("Origin",        "Bengaluru, India"),
    ("Education",     "B.Tech \u00b7 Bangalore Inst. of Technology"),
    ("Status",        "Building + Learning + Discovering"),
    ("ToolChain",     "VS Code \u00b7 Git \u00b7 Android Studio \u00b7 Claude"),
    ("Core.Lang",     "C \u00b7 C++ \u00b7 Python"),
    ("Core.Frontend", "HTML5 \u00b7 CSS \u00b7 React.js \u00b7 Next.js"),
    ("Core.Backend",  "FastAPI"),
    ("Core.Database", "SQL \u00b7 MongoDB"),
    ("Core.Infra",    "Firebase \u00b7 Supabase"),
    ("Grid.Mail",     "pushkardeshpande876@gmail.com"),
    ("Grid.Portfolio","Coming Soon"),
    ("Grid.LinkedIn", "/in/pushkar-r-deshpande"),
    ("Grid.GitHub",   "@pushkarrd"),
]

def load_photo(path):
    img=Image.open(path).convert("RGB")
    w,h=img.size; r=GW/GH
    if w/h>r:
        nw=int(h*r); img=img.crop(((w-nw)//2,0,(w+nw)//2,h))
    else:
        nh=int(w/r); t=max(0,min(int(h*.04),h-nh)); img=img.crop((0,t,w,t+nh))
    img=img.resize((GW,GH),Image.LANCZOS)
    img=ImageOps.autocontrast(img,cutoff=1)
    img=ImageEnhance.Contrast(img).enhance(1.3)
    img=img.filter(ImageFilter.UnsharpMask(radius=3,percent=140,threshold=0))
    return img

def segment(rgb):
    dist=np.sqrt(((rgb.astype(float)-255)**2).sum(axis=2))
    fg=dist>65; fg=binary_closing(fg,iterations=4); fg=binary_fill_holes(fg)
    lab,n=sp_label(fg)
    if not n: return fg
    cnt=np.bincount(lab.ravel()); cnt[0]=0
    return lab==cnt.argmax()

def dither_fs(gray,mask=None,invert=False):
    a=gray.astype(float)/255.
    if invert: a=1.-a
    H,W=a.shape; dots=[]
    for y in range(H):
        rtl=(y%2==1); xs=range(W-1,-1,-1) if rtl else range(W)
        for x in xs:
            if mask is not None and not mask[y,x]:
                a[y,x]=0.; continue
            old=a[y,x]; new=1. if old>=.5 else 0.; err=old-new; a[y,x]=new
            if new==0.: dots.append((x,y))
            for dy,dx,w in [(0,1,7/16),(1,-1,3/16),(1,0,5/16),(1,1,1/16)]:
                ny=y+dy; nx=(x-dx) if rtl else (x+dx)
                if 0<=ny<H and 0<=nx<W:
                    a[ny,nx]=float(np.clip(a[ny,nx]+err*w,0.,1.))
    return dots

def to_svg(dots):
    return [(PORT_X+(gx+.5)*GPX,PORT_Y+(gy+.5)*GPY) for gx,gy in dots]

LOGO_CX=PORT_X+PORT_W/2; LOGO_CY=PORT_Y+PORT_H/2; LOGO_SC=min(PORT_W,PORT_H)*.72

def n2s(pts):
    return [(LOGO_CX+(x-.5)*LOGO_SC,LOGO_CY+(y-.5)*LOGO_SC) for x,y in pts]

def react_cloud(n=N_TRAV,seed=1):
    rng=np.random.RandomState(seed); pts=[]
    for _ in range(n//8):
        a=rng.uniform(0,2*math.pi); r=rng.uniform(0,.06)
        pts.append((.5+r*math.cos(a),.5+r*math.sin(a)))
    per=(n-len(pts))//3
    for k in range(3):
        phi=k*math.pi/3
        for t in rng.uniform(0,2*math.pi,per):
            ex=.38*math.cos(t); ey=.14*math.sin(t)
            pts.append((float(np.clip(.5+ex*math.cos(phi)-ey*math.sin(phi),.02,.98)),
                        float(np.clip(.5+ex*math.sin(phi)+ey*math.cos(phi),.02,.98))))
    while len(pts)<n: pts.append(pts[rng.randint(len(pts))])
    return pts[:n]

def code_cloud(n=N_TRAV,seed=2):
    rng=np.random.RandomState(seed); pts=[]; TH=.022
    def seg(x0,y0,x1,y1,c):
        for _ in range(c):
            t=rng.random()
            pts.append((float(np.clip(x0+t*(x1-x0)+rng.uniform(-TH,TH),.02,.98)),
                        float(np.clip(y0+t*(y1-y0)+rng.uniform(-TH,TH),.02,.98))))
    p=n//3
    seg(.32,.28,.20,.50,p//2); seg(.20,.50,.32,.72,p//2)
    seg(.44,.74,.56,.26,p)
    seg(.68,.28,.80,.50,p//2); seg(.80,.50,.68,.72,p//2)
    while len(pts)<n: pts.append(pts[rng.randint(len(pts))])
    return pts[:n]

def vercel_cloud(n=N_TRAV,seed=3):
    rng=np.random.RandomState(seed); TH=.022; R=.34
    v=[(0.5+R*math.cos(-math.pi/2+k*2*math.pi/3),
        0.52+R*math.sin(-math.pi/2+k*2*math.pi/3)) for k in range(3)]
    pts=[]; p=n//3
    for i in range(3):
        x0,y0=v[i]; x1,y1=v[(i+1)%3]
        for _ in range(p):
            t=rng.random()
            pts.append((float(np.clip(x0+t*(x1-x0)+rng.uniform(-TH,TH),.02,.98)),
                        float(np.clip(y0+t*(y1-y0)+rng.uniform(-TH,TH),.02,.98))))
    while len(pts)<n: pts.append(pts[rng.randint(len(pts))])
    return pts[:n]

def ot_match(src,dst):
    _,idx=KDTree(np.array(dst)).query(np.array(src)); return idx.tolist()

def make_bands(svg_dots,n=N_BANDS):
    rng=np.random.RandomState(7); arr=np.array(svg_dots)
    noisy=arr[:,1]+rng.normal(0,4.,len(arr))+rng.normal(0,PORT_H*.45,len(arr))
    order=np.argsort(noisy); bands=[[] for _ in range(n)]
    for i,di in enumerate(order): bands[i%n].append(int(di))
    return bands

def evenness_metric(groups,svg_dots,cells=8):
    arr=np.array(svg_dots); M=np.zeros((cells,cells,len(groups)))
    for gi,g in enumerate(groups):
        for di in g:
            if di>=len(arr): continue
            cx=int(np.clip((arr[di,0]-PORT_X)/PORT_W*cells,0,cells-1))
            cy=int(np.clip((arr[di,1]-PORT_Y)/PORT_H*cells,0,cells-1))
            M[cy,cx,gi]=1
    return float(np.mean(np.var(M,axis=2)))

def boundary_metric(bands,svg_dots):
    arr=np.array(svg_dots); ys=arr[:,1]
    stds=[np.std(ys[b])/PORT_H for b in bands if len(b)>1]
    return max(0.,0.25-(np.mean(stds) if stds else 0.))

def build_row_map(indices,svg_dots):
    rm={}
    for di in indices:
        if di>=len(svg_dots): continue
        sx,sy=svg_dots[di]; gy=int((sy-PORT_Y)/GPY); rm.setdefault(gy,[]).append(round(sx,2))
    return rm

def rm_to_path(rm):
    parts=[]; s2=round(DS*2,2)
    for gy,xs in sorted(rm.items()):
        sy=round(PORT_Y+(gy+.5)*GPY,2); y0=round(sy-DS,2)
        for sx in xs:
            x0=round(sx-DS,2); parts.append(f"M{x0},{y0}h{s2}v{s2}h-{s2}Z")
    return "".join(parts)

def build_info(dark):
    C=CHR_D if dark else CHR_L; VL=VAL_D if dark else VAL_L; LD=LEAD_D if dark else LEAD_L
    L=[]
    hy=TB_H+19
    L.append(f'<text x="{R_X}" y="{hy}" font-family="\'Courier New\',monospace" font-size="12" fill="{C}" letter-spacing="4" font-weight="700" opacity=".85">SYSTEM.INFO</text>')
    lx,ly=SW-PAD-70,TB_H+5
    L.append(f'<g transform="translate({lx},{ly})"><circle cx="6" cy="8" r="5" fill="{LIVE_C}"><animate attributeName="opacity" values=".9;.2;.9" dur="1.4s" repeatCount="indefinite"/><animate attributeName="r" values="5;7;5" dur="1.4s" repeatCount="indefinite"/></circle><text x="15" y="13" font-family="monospace" font-size="11" fill="{LIVE_C}" font-weight="700" letter-spacing="2">LIVE</text></g>')
    pt="@pushkarrd"; pw2=int(len(pt)*CW+22); px2=SW-PAD-pw2; py2=hy+10
    L+=[f'<rect x="{px2}" y="{py2}" width="{pw2}" height="22" rx="11" fill="{ACC}" opacity=".12"/>',
        f'<rect x="{px2}" y="{py2}" width="{pw2}" height="22" rx="11" fill="none" stroke="{ACC}" stroke-width="1"/>',
        f'<text x="{px2+pw2//2}" y="{py2+15}" text-anchor="middle" font-family="monospace" font-size="13" fill="{ACC}" font-weight="700">{pt}</text>']
    dvy=py2+30
    L.append(f'<line x1="{R_X}" y1="{dvy}" x2="{SW-PAD}" y2="{dvy}" stroke="{C}" stroke-width=".5" opacity=".3"/>')
    ry0=dvy+26; rh=23; ml=max(len(r[0]) for r in INFO_ROWS); lc=(ml+2)*CW
    for i,(lab,val) in enumerate(INFO_ROWS):
        ry=ry0+i*rh
        if i in (6,11):
            sy=ry-9; L.append(f'<line x1="{R_X}" y1="{sy}" x2="{SW-PAD}" y2="{sy}" stroke="{C}" stroke-width=".3" opacity=".2" stroke-dasharray="3,5"/>')
        L.append(f'<text x="{R_X}" y="{ry}" font-family="\'Courier New\',monospace" font-size="13" fill="{C}" opacity=".8">{lab}</text>')
        vw=round(len(val)*CW); vx=SW-PAD
        L.append(f'<text x="{vx}" y="{ry}" text-anchor="end" font-family="\'Courier New\',monospace" font-size="13" fill="{VL}" textLength="{vw}" lengthAdjust="spacingAndGlyphs">{val}</text>')
        lx0=R_X+(len(lab)+1)*CW; lx1=vx-vw-4; lw=lx1-lx0
        if lw>12:
            nd=max(3,int(lw/5.8)); lm=(lx0+lx1)/2
            L.append(f'<text x="{lm:.1f}" y="{ry}" text-anchor="middle" font-family="monospace" font-size="13" fill="{LD}" opacity=".45" letter-spacing="1">{"·"*nd}</text>')
    return "\n".join(L)

def _kt(*times): return ";".join(f"{t/LOOP:.4f}" for t in times)
def _ks(n): return ";".join([".4 0 .6 1"]*n)

def build_svg(svg_dots,dark,bands,trav_base,l1_trav,l2_trav,l3_trav):
    DT=DOT_D if dark else DOT_L; C=CHR_D if dark else CHR_L
    BG=BG_D if dark else BG_L; TB=TB_D if dark else TB_L
    LP="#0D1526" if dark else "#EEF2FF"
    P=[]
    P.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SW}" height="{SH}" viewBox="0 0 {SW} {SH}" role="img" aria-label="Pushkar R Deshpande GitHub banner">')
    P.append(f'<rect width="{SW}" height="{SH}" fill="{BG}" rx="12"/>')
    P.append(f'<rect width="{SW}" height="{TB_H}" fill="{TB}" rx="12"/>')
    P.append(f'<rect y="24" width="{SW}" height="12" fill="{TB}"/>')
    for cx,col in [(20,"#FF5F57"),(40,"#FFBD2E"),(60,"#28CA41")]:
        P.append(f'<circle cx="{cx}" cy="18" r="6" fill="{col}"/>')
    P.append(f'<text x="{SW//2}" y="23" text-anchor="middle" font-family="monospace" font-size="13" fill="{C}" letter-spacing="2" opacity=".9">profile.sh --live</text>')
    P.append(f'<rect x="0" y="{TB_H}" width="{L_W}" height="{SH-TB_H}" fill="{LP}" opacity=".55"/>')
    P.append(f'<line x1="{L_W}" y1="{TB_H}" x2="{L_W}" y2="{SH}" stroke="{C}" stroke-width="1" stroke-dasharray="4,3" opacity=".5"/>')
    P.append(f'<text x="{L_W//2}" y="{TB_H+13}" text-anchor="middle" font-family="monospace" font-size="10" fill="{C}" letter-spacing="4" opacity=".55">VISUAL.MAP</text>')
    bx,by=PORT_X-2,PORT_Y-2; bw,bh=PORT_W+4,PORT_H+4; bs=18
    P.append(f'<path d="M{bx+bs},{by}L{bx},{by}L{bx},{by+bs} M{bx+bw-bs},{by}L{bx+bw},{by}L{bx+bw},{by+bs} M{bx},{by+bh-bs}L{bx},{by+bh}L{bx+bs},{by+bh} M{bx+bw},{by+bh-bs}L{bx+bw},{by+bh}L{bx+bw-bs},{by+bh}" fill="none" stroke="{C}" stroke-width="1.5" opacity=".55"/>')
    P.append(f'<defs><clipPath id="pc"><rect x="{PORT_X}" y="{PORT_Y}" width="{PORT_W}" height="{PORT_H}"/></clipPath></defs>')

    # LAYER A - INTRO
    rng_a=np.random.RandomState(5); all_i=list(range(len(svg_dots))); rng_a.shuffle(all_i)
    ig=[all_i[k::N_INTRO] for k in range(N_INTRO)]
    P.append(f'<g id="LA" clip-path="url(#pc)">')
    P.append(f'  <animate attributeName="opacity" from="1" to="0" dur=".08s" begin="3.12s" fill="freeze"/>')
    for gi,grp in enumerate(ig):
        stagger=gi*(2./N_INTRO); rm=build_row_map(grp,svg_dots); pd=rm_to_path(rm)
        if not pd: continue
        P.append(f'  <path d="{pd}" fill="{DT}" shape-rendering="crispEdges" opacity="0">')
        P.append(f'    <animate attributeName="opacity" from="0" to="1" dur=".4s" begin="{stagger:.3f}s" fill="freeze"/>')
        P.append('  </path>')
    P.append('</g>')

    # LAYER B - LOOP PORTRAIT
    p_kt=_kt(0,T_P,T_D,T_R-.1,T_R); p_kv="1;1;0;0;1"
    P.append(f'<g id="LB" clip-path="url(#pc)" opacity="0">')
    P.append(f'  <animate attributeName="opacity" from="0" to="1" dur=".08s" begin="3.12s" fill="freeze"/>')
    P.append('  <g id="LBi">')
    P.append(f'    <animate attributeName="opacity" values="{p_kv}" keyTimes="{p_kt}" dur="{LOOP}s" begin="3.2s" repeatCount="indefinite" calcMode="spline" keySplines="{_ks(4)}"/>')
    l1cx=sum(p[0] for p in l1_trav)/len(l1_trav); l1cy=sum(p[1] for p in l1_trav)/len(l1_trav)
    pcx=PORT_X+PORT_W/2; pcy=PORT_Y+PORT_H/2; rng_b=np.random.RandomState(11)
    for band in bands:
        ndx=rng_b.normal(0,3.5); ndy=rng_b.normal(0,3.5)
        dx=(l1cx-pcx)*.42+ndx; dy=(l1cy-pcy)*.42+ndy
        rm=build_row_map(band,svg_dots); pd=rm_to_path(rm)
        if not pd: continue
        d_kt=_kt(0,T_P,T_D,T_R); d_kv=f"0,0;0,0;{dx:.1f},{dy:.1f};0,0"
        P.append('    <g>')
        P.append(f'      <animateTransform attributeName="transform" type="translate" values="{d_kv}" keyTimes="{d_kt}" dur="{LOOP}s" begin="3.2s" repeatCount="indefinite" calcMode="spline" keySplines="{_ks(3)}"/>')
        P.append(f'      <path d="{pd}" fill="{DT}" shape-rendering="crispEdges"/>')
        P.append('    </g>')
    P.append('  </g>'); P.append('</g>')

    # TRAVELLERS
    t_kt=_kt(0,T_P,T_D,T_L1,T_12,T_L2,T_23,T_L3,T_R,T_R); t_kv="0;0;0;1;1;1;1;1;0;0"
    P.append(f'<g id="TR" clip-path="url(#pc)" opacity="0">')
    P.append(f'  <animate attributeName="opacity" values="{t_kv}" keyTimes="{t_kt}" dur="{LOOP}s" begin="3.2s" repeatCount="indefinite" calcMode="spline" keySplines="{_ks(9)}"/>')
    lim=min(N_TRAV,len(trav_base),len(l1_trav),len(l2_trav),len(l3_trav))
    for ti in range(lim):
        bx2,by2=trav_base[ti]; x1,y1=l1_trav[ti]; x2,y2=l2_trav[ti]; x3,y3=l3_trav[ti]
        dx1,dy1=x1-bx2,y1-by2; dx2,dy2=x2-bx2,y2-by2; dx3,dy3=x3-bx2,y3-by2
        pos_kt=_kt(0,T_D,T_L1,T_12,T_L2,T_23,T_L3,T_R,T_R)
        pos_kv=f"0,0;{dx1:.1f},{dy1:.1f};{dx1:.1f},{dy1:.1f};{dx2:.1f},{dy2:.1f};{dx2:.1f},{dy2:.1f};{dx3:.1f},{dy3:.1f};{dx3:.1f},{dy3:.1f};0,0;0,0"
        P.append(f'  <circle cx="{bx2:.1f}" cy="{by2:.1f}" r="1.8" fill="{DT}">')
        P.append(f'    <animateTransform attributeName="transform" type="translate" values="{pos_kv}" keyTimes="{pos_kt}" dur="{LOOP}s" begin="3.2s" repeatCount="indefinite" calcMode="spline" keySplines="{_ks(8)}"/>')
        P.append('  </circle>')
    P.append('</g>')

    P.append(f'<g id="IP">{build_info(dark)}</g>')
    P.append('</svg>')
    return "\n".join(P)

def main():
    ap=argparse.ArgumentParser(description="Generate GitHub profile banner SVGs")
    ap.add_argument("--photo",required=True); ap.add_argument("--out",default="banner")
    args=ap.parse_args(); os.makedirs(args.out,exist_ok=True)
    print("Loading photo..."); img=load_photo(args.photo); rgb=np.array(img); gr=np.array(img.convert("L"))
    print("Dark portrait..."); msk=segment(rgb); d_grid=dither_fs(gr,mask=msk,invert=False)
    d_svg=to_svg(d_grid); np.save(os.path.join(args.out,"dots_dark.npy"),np.array(d_grid)); print(f"  {len(d_svg):,} dots")
    print("Light portrait..."); l_grid=dither_fs(gr,mask=msk,invert=False)
    l_svg=to_svg(l_grid); np.save(os.path.join(args.out,"dots_light.npy"),np.array(l_grid)); print(f"  {len(l_svg):,} dots")
    print("Logo clouds...")
    react_s=n2s(react_cloud()); code_s=n2s(code_cloud()); verc_s=n2s(vercel_cloud())
    i12=ot_match(react_s,code_s); i13=ot_match(react_s,verc_s)
    code_m=[code_s[i] for i in i12]; verc_m=[verc_s[i] for i in i13]
    rng=np.random.RandomState(13)
    trav_base=[(PORT_X+PORT_W*rng.uniform(.1,.9),PORT_Y+PORT_H*rng.uniform(.1,.9)) for _ in range(N_TRAV)]
    ib1=ot_match(trav_base,react_s); l1_t=[react_s[i] for i in ib1]
    ib2=ot_match(l1_t,code_m); ib3=ot_match(l1_t,verc_m)
    l2_t=[code_m[i] for i in ib2]; l3_t=[verc_m[i] for i in ib3]
    print("Bands & metrics...")
    d_bands=make_bands(d_svg); l_bands=make_bands(l_svg)
    rng2=np.random.RandomState(5); al=list(range(len(d_svg))); rng2.shuffle(al)
    ig_d=[al[k::N_INTRO] for k in range(N_INTRO)]
    ev=evenness_metric(ig_d,d_svg); bm=boundary_metric(d_bands,d_svg)
    print(f"  Evenness: {ev:.4f} target<0.05 {'OK' if ev<.05 else 'WARN'}"); print(f"  Boundary: {bm:.4f} target<0.01 {'OK' if bm<.01 else 'WARN'}")
    print("Writing dark.svg...")
    dark_svg=build_svg(d_svg,True,d_bands,trav_base,l1_t,l2_t,l3_t)
    dp=os.path.join(args.out,"dark.svg")
    with open(dp,"w",encoding="utf-8") as f: f.write(dark_svg)
    print(f"  {os.path.getsize(dp)/1024:.0f} KB")
    print("Writing light.svg...")
    lite_svg=build_svg(l_svg,False,l_bands,trav_base,l1_t,l2_t,l3_t)
    lp=os.path.join(args.out,"light.svg")
    with open(lp,"w",encoding="utf-8") as f: f.write(lite_svg)
    print(f"  {os.path.getsize(lp)/1024:.0f} KB")
    print("\nDone! Open banner/dark.svg in browser (dark mode) to verify.")

if __name__=="__main__":
    main()
