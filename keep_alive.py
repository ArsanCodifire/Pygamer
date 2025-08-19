import os
from threading import Thread
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

def get_usage():
    with open("/proc/stat", "r") as f:
        parts = f.readline().split()
        total = sum(map(int, parts[1:]))
        idle = int(parts[4])
    cpu_percent = 100 - (idle * 100 / total)

    meminfo = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            key, value, *_ = line.split()
            meminfo[key] = int(value)
    ram_total = meminfo["MemTotal"]
    ram_free = meminfo["MemAvailable"]
    ram_used_percent = (1 - ram_free / ram_total) * 100

    return round(cpu_percent, 2), round(ram_used_percent, 2)

def make_html(bot_name, emoji, avatar_url):
    return f"""
    <html>
    <head>
        <title>{bot_name} Status</title>
    </head>
    <body style="background:url('https://raw.githubusercontent.com/ArsanCodifire/Profile-pic/refs/heads/main/Bg.jpg');background-size:cover;color:white;text-align:center;padding-top:5%;">
        <img src="{avatar_url}" style="width:150px;height:150px;border-radius:50%;">
        <h1>{emoji} {bot_name} Bot</h1>
        <p>✅ Bot is running 24/7</p>
        <p id="cpu">CPU Usage: ...</p>
        <p id="ram">RAM Usage: ...</p>
        <script>
            async function updateUsage() {{
                let res = await fetch('/usage');
                let data = await res.json();
                document.getElementById('cpu').innerText = "CPU Usage: " + data.cpu + "%";
                document.getElementById('ram').innerText = "RAM Usage: " + data.ram + "%";
            }}
            setInterval(updateUsage, 2000);
            updateUsage();
        </script>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return make_html("PyGamer", "🎮", "https://raw.githubusercontent.com/ArsanCodifire/Profile-pic/refs/heads/main/PyGamer.png")

@app.get("/usage", response_class=JSONResponse)
async def usage():
    cpu, ram = get_usage()
    return {"cpu": cpu, "ram": ram}

def run():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

def keep_alive():
    Thread(target=run, daemon=True).start()