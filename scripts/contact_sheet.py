import subprocess, json, io
from PIL import Image, ImageDraw, ImageFont
eps=[("QR","QR_v6"),("Elevator","Elevator_v6b"),("Sky","Sky_v6"),("ANC","ANC_v7")]  # final r6 picks
N=8; W=200; H=356; LW=170
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",22) if __import__('os').path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") else ImageFont.load_default()
sheet=Image.new("RGB",(LW+N*W,len(eps)*(H+30)+10),(13,14,18)); d=ImageDraw.Draw(sheet)
for r,(id,f) in enumerate(eps):
    mp4=f"renders/{f}.mp4"
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",mp4]))
    y=r*(H+30)+10; d.text((10,y+H//2-20),f,fill=(255,176,32),font=font); d.text((10,y+H//2+10),f"{dur:.1f}s",fill=(243,239,230),font=font)
    for i in range(N):
        t=0.3+i*(dur-0.6)/(N-1)
        png=subprocess.check_output(["ffmpeg","-v","error","-ss",f"{t:.2f}","-i",mp4,"-frames:v","1","-vf",f"scale={W}:{H}","-f","image2pipe","-vcodec","png","-"])
        sheet.paste(Image.open(io.BytesIO(png)),(LW+i*W,y)); d.text((LW+i*W+4,y+H+2),f"{t:.1f}s",fill=(180,180,180),font=ImageFont.load_default())
sheet.save("contact_sheet_v6.png"); print(sheet.size)
