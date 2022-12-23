import json
import struct
import binascii

import rp2

from network import WLAN, STA_IF, AP_IF

import uasyncio as asyncio

from utime import sleep_ms, sleep_us
from machine import SPI, Pin, PWM, Signal

from ahttpserver import Server, sendfile

from websockets.client import connect
from websockets.server import serve

# constants

clock_freq_min = 5.0
clock_freq_max = 12.8

# PORT settings

led_pin = Pin("LED", mode=Pin.OUT)

cpu_pause_pin = Pin(7, Pin.OUT)  # CPU pause
cpu_reset_pin = Pin(9, Pin.OUT)  # console reset
video_pin = Pin(10, Pin.OUT)  # video mode  JP3/4
lang_pin = Pin(11, Pin.OUT)  # region JP1/2

led = Signal(led_pin, invert=False)

cpu_pause = Signal(cpu_pause_pin, invert=False)
cpu_reset = Signal(cpu_reset_pin, invert=False)
video = Signal(video_pin, invert=False)
lang = Signal(lang_pin, invert=False)

cpu_pwm = PWM(Pin(12))
cpu_pwm.duty_u16(32768)
# cpu_pwm.freq(1000000)

async def main():
    try:
        # # SPI
        # spi = SPI(1, sck=Pin(14), mosi=Pin(15))
        #
        # spi.init(baudrate=20_000_000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB)

        # HTTP

        sta_if = WLAN(STA_IF)
        app = Server(host="0.0.0.0", port=80)

        @app.route("GET", "/")
        async def root(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/html\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/index.html")

        @app.route("GET", "/favicon.ico")
        async def favicon(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: image/x-icon\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/favicon.ico")

        @app.route("GET", "/main.js")
        async def main(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/javascript\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/main.js")

        @app.route("GET", "/style.css")
        async def style_css(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/css\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/style.css")

        @app.route("GET", "/jquery-ui.min.js")
        async def jquery_ui(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/javascript\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/jquery-ui.min.js")

        @app.route("GET", "/jquery-ui.min.css")
        async def jquery_ui_css(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/css\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/jquery-ui.min.css")

        @app.route("GET", "/jquery-3.6.1.slim.min.js")
        async def jquery_slim(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/javascript\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/jquery-3.6.1.slim.min.js")

        @app.route("GET", "/images/ui-bg_20.png")
        async def ui_bg_20(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/png\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/images/ui-bg_20.png")

        @app.route("GET", "/images/ui-bg_22.png")
        async def ui_bg_22(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/png\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/images/ui-bg_22.png")

        @app.route("GET", "/images/ui-bg_26.png")
        async def ui_bg_26(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/png\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/images/ui-bg_26.png")

        @app.route("GET", "/images/ui-bg_inset.png")
        async def ui_bg_inset(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/png\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/images/ui-bg_inset.png")

        @app.route("GET", "/images/ui-icons.png")
        async def ui_icons(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/png\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/images/ui-icons.png")

        @app.route("GET", "/images/config_icon_small.png")
        async def ui_icons(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: text/png\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/images/config_icon_small.png")

        @app.route("GET", "/space-marine.ttf")
        async def fonts(reader, writer, request):

            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Connection: close\r\n")
            writer.write(b"Content-Type: font/ttf\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            await sendfile(writer, "app/space-marine.ttf")

        async def set_freq(freq,):
            cpu_pause.value(0)
            await asyncio.sleep_ms(10)

            cpu_pwm.freq(freq)

            await asyncio.sleep_ms(10)
            cpu_pause.value(1)

        async def reset_console():
            cpu_reset.value(1)
            sleep_ms(350)
            cpu_reset.value(0)

        async def set_mode(video_mode):
            if video_mode == 1:  # EUR PAL 50Hz
                video.value(0)
                lang.value(1)
            elif video_mode == 2:  # JAP NTSC 60Hz
                video.value(1)
                lang.value(0)
            elif video_mode == 3:  # USA NTSC 60Hz
                video.value(1)
                lang.value(1)

        def validate_json(jsonData):
            try:
                json.loads(jsonData)
            except ValueError as err:
                return False
            return True

        async def add_client(ws, path):
            print(f"Connection on {path}")

            try:
                # await ws.send(f"adding client to {path}")

                async for msg in ws:
                    led.value(1)
                    if msg == "__poll__":
                        json_read_file = open("data.json")
                        json_data = json.load(json_read_file)
                        await ws.send(json.dumps(json_data))
                        json_read_file.close()

                    elif msg == "__ping__":
                        await ws.send("__pong__")

                    elif msg == "__scan__":
                        scan_results = sta_if.scan()

                        net_list = []
                        for result in scan_results:
                            net_list.append(result[0])

                        print(net_list)

                        await ws.send(json.dumps(net_list))

                    elif validate_json(msg):

                        json_msg = json.loads(msg)

                        console = json_msg.get("console")
                        wlan = json_msg.get("wlan")

                        if console:
                            video_mode = int(console.get("video_mode"))
                            clock_freq = float(console.get("clock_freq"))
                            reset_game = bool(console.get("reset_game"))

                            if video_mode:
                                print(f"Set video mode: {video_mode}")
                                await set_mode(video_mode)

                            if (float(clock_freq) >= clock_freq_min) and (float(clock_freq) <= clock_freq_max):
                                print(f"Change freq to {clock_freq}")
                                freq = int(float(clock_freq) * 1000000)
                                await set_freq(freq)

                            if reset_game == True:
                                print("Reset console")
                                await reset_console()

                            json_writefile = open("data.json", "w")
                            json_writefile.write(msg)
                            json_writefile.close()

                        elif wlan:

                            json_writefile = open("wlan.json", "w")
                            json_writefile.write(msg)
                            json_writefile.close()

                    led.value(0)

            finally:
                print("Disconnected")

        def handle_exception(loop, context):
            # uncaught exceptions end up here
            import sys
            print("global exception handler:", context)
            sys.print_exception(context["exception"])
            # sys.exit()

        async def system_init():
            print("Load initial data")

            json_read_file = open("data.json")
            json_data = json.load(json_read_file)

            cpu_settings = json_data.get("console")

            clock_freq = float(cpu_settings.get("clock_freq"))
            video_mode = int(cpu_settings.get("video_mode"))

            print(f"Change freq to {clock_freq}")
            freq = int(clock_freq * 1000000)

            await set_freq(freq)

            await asyncio.sleep_ms(10)

            print(f"Set video mode: {video_mode}")
            await set_mode(video_mode)

            await asyncio.sleep_ms(10)

            await reset_console()

            json_read_file.close()

            print("Load complete")

        async def wlan_init():

            # WIFI settings

            wlan_file = open("wlan.json")
            wlan_data = json.load(wlan_file)
            wlan_file.close()

            wlan_settings = wlan_data.get("wlan")

            dev_country = wlan_settings.get("country")
            dev_ssid = wlan_settings.get("ssid")
            dev_pwd = wlan_settings.get("pwd")

            if dev_country:
                rp2.country(dev_country)

            async def init_ap():

                ap_if = WLAN(AP_IF)
                mac_addr = ap_if.config('mac')

                dev_id = binascii.hexlify(mac_addr)[:4]

                ap_if.config(ssid=f"MCW_{dev_id.upper():04}", password=f"My_MCW_{dev_id.upper():04}")
                ap_if.active(True)

            if dev_ssid == "":
                await init_ap()

            elif (dev_ssid != "") and (dev_pwd != ""):

                # set power mode to get WiFi power-saving off (if needed)
                sta_if.config(pm=0xa11140)

                if not sta_if.isconnected():
                    print('connecting to network...')
                    sta_if.active(True)
                    sta_if.connect(dev_ssid, dev_pwd)
                    conn_timeout = 20
                    while not sta_if.isconnected():
                        print(f"Connecting... {conn_timeout}")
                        conn_timeout -= 1

                        led.value(1)
                        await asyncio.sleep_ms(50)
                        led.value(0)
                        await asyncio.sleep_ms(50)
                        led.value(1)
                        await asyncio.sleep_ms(50)
                        led.value(0)

                        await asyncio.sleep_ms(1000)

                        if conn_timeout <= 0:
                            await init_ap()
                            break

                print("Connected")

                if sta_if.isconnected():
                    print(sta_if.ifconfig())

            else:
                await init_ap()
                print("Error wlan credentials")

        async def wrapper(delay, coro):
            await asyncio.sleep(delay)
            return await coro

        loop = asyncio.get_event_loop()
        loop.set_exception_handler(handle_exception)

        loop.create_task(wrapper(0.0, system_init()))
        loop.create_task(wrapper(1.0, wlan_init()))
        loop.create_task(wrapper(4.0, serve(add_client, "0.0.0.0", 1337)))
        loop.create_task(wrapper(5.0, app.start()))

        loop.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        cpu_pwm.deinit()
        asyncio.run(app.stop())
        asyncio.new_event_loop()


if __name__ == "__main__":
    asyncio.run(main())
