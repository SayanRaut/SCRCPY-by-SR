"""
Core Controller for SCRCPY and ADB interactions.
Manages device discovery, wireless TCP/IP pairing, scrcpy process lifecycle,
and remote Android key/media controls.
"""

import os
import sys
import json
import time
import subprocess
import threading
from typing import List, Dict, Optional, Callable


class ScrcpyCore:
    def __init__(self, base_dir: Optional[str] = None):
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.scrcpy_dir = os.path.join(self.base_dir, 'scrcpy')
        
        # Locate ADB and SCRCPY executables
        self.adb_path = self._find_executable('adb.exe' if os.name == 'nt' else 'adb')
        self.scrcpy_path = self._find_executable('scrcpy.exe' if os.name == 'nt' else 'scrcpy')
        
        self.config_path = os.path.join(self.base_dir, 'scrcpy_config.json')
        self.config = self.load_config()
        
        # Active scrcpy process management
        self.active_process: Optional[subprocess.Popen] = None
        self.process_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.last_record_file: Optional[str] = None

    def _find_executable(self, name: str) -> str:
        """Find executable in bundled scrcpy folder or system PATH."""
        bundled = os.path.join(self.scrcpy_dir, name)
        if os.path.isfile(bundled):
            return bundled
        return name

    def _get_subprocess_flags(self) -> Dict:
        """Get flags to suppress console windows on Windows."""
        kwargs = {}
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = startupinfo
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return kwargs

    def run_adb(self, args: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        """Run an ADB command synchronously."""
        cmd = [self.adb_path] + args
        kwargs = self._get_subprocess_flags()
        return subprocess.run(
            cmd,
            cwd=self.scrcpy_dir if os.path.isdir(self.scrcpy_dir) else self.base_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            **kwargs
        )

    def list_devices(self) -> List[Dict[str, str]]:
        """
        List connected ADB devices with detailed properties (model, product, transport).
        Returns: list of dicts with keys: serial, state, model, product, is_wireless
        """
        try:
            res = self.run_adb(['devices', '-l'], timeout=6)
            lines = res.stdout.strip().splitlines()
            devices = []
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    state = parts[1]
                    
                    # Extract model and product
                    model = "Android Device"
                    product = ""
                    for p in parts[2:]:
                        if p.startswith("model:"):
                            model = p.split("model:")[1].replace("_", " ")
                        elif p.startswith("product:"):
                            product = p.split("product:")[1]

                    is_wireless = ":" in serial and not serial.startswith("usb")
                    
                    devices.append({
                        "serial": serial,
                        "state": state,
                        "model": model,
                        "product": product,
                        "is_wireless": is_wireless,
                        "display_name": f"{model} ({'Wi-Fi' if is_wireless else 'USB'}: {serial})"
                    })
            return devices
        except Exception as e:
            return []

    def get_device_ip(self, serial: Optional[str] = None) -> Optional[str]:
        """
        Query the device directly via ADB to detect its local Wi-Fi IP address.
        """
        prefix = ['-s', serial] if serial else []
        try:
            # Method 1: Check ip route
            res = self.run_adb(prefix + ['shell', 'ip', 'route'])
            for line in res.stdout.splitlines():
                if 'wlan0' in line and 'src' in line:
                    parts = line.split()
                    if 'src' in parts:
                        idx = parts.index('src')
                        if idx + 1 < len(parts):
                            return parts[idx + 1].strip()

            # Method 2: ip -f inet addr show wlan0
            res = self.run_adb(prefix + ['shell', 'ip', '-f', 'inet', 'addr', 'show', 'wlan0'])
            for line in res.stdout.splitlines():
                line = line.strip()
                if line.startswith('inet '):
                    ip_cidr = line.split()[1]
                    return ip_cidr.split('/')[0].strip()

            # Method 3: ifconfig wlan0
            res = self.run_adb(prefix + ['shell', 'ifconfig', 'wlan0'])
            for line in res.stdout.splitlines():
                if 'inet addr:' in line:
                    return line.split('inet addr:')[1].split()[0].strip()
        except Exception:
            pass
        return None

    def get_device_details(self, serial: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch rich device metadata: manufacturer, brand, model, android_version,
        battery level, charging status, and temperature in a single roundtrip.
        """
        prefix = ['-s', serial] if serial else []
        details = {
            "brand": "Android",
            "manufacturer": "Generic",
            "model": "Device",
            "android_version": "N/A",
            "battery_level": "--",
            "battery_charging": False,
            "temperature": "--",
            "market_name": "Android Device"
        }
        try:
            batch_cmd = prefix + ['shell', 'getprop ro.product.brand; echo ___SEP___; getprop ro.product.manufacturer; echo ___SEP___; getprop ro.product.model; echo ___SEP___; getprop ro.build.version.release; echo ___SEP___; dumpsys battery']
            res = self.run_adb(batch_cmd, timeout=4)
            if res.returncode == 0 and res.stdout:
                sections = res.stdout.split('___SEP___')
                if len(sections) >= 5:
                    brand = sections[0].strip()
                    mfr = sections[1].strip()
                    model = sections[2].strip()
                    os_ver = sections[3].strip()
                    battery_raw = sections[4]

                    if brand:
                        details["brand"] = brand.upper()
                    if mfr:
                        details["manufacturer"] = mfr.title()
                    if model:
                        details["model"] = model.replace('_', ' ')
                    if os_ver:
                        details["android_version"] = f"Android {os_ver}"

                    # Clean marketing name
                    if details["brand"] == "POCO" and "22111317" in details["model"]:
                        details["market_name"] = "POCO X5 5G"
                    elif details["brand"] not in ("ANDROID", "GENERIC"):
                        details["market_name"] = f"{details['brand']} {details['model']}"
                    else:
                        details["market_name"] = details["model"]

                    for line in battery_raw.splitlines():
                        line = line.strip()
                        if line.startswith('level:'):
                            details["battery_level"] = line.split('level:')[1].strip() + "%"
                        elif line.startswith('status:'):
                            details["battery_charging"] = line.split('status:')[1].strip() in ('2', '5')
                        elif line.startswith('temperature:'):
                            try:
                                t_val = float(line.split('temperature:')[1].strip()) / 10.0
                                details["temperature"] = f"{t_val:.1f}°C"
                            except Exception:
                                pass
        except Exception:
            pass
        return details

    def enable_tcpip(self, serial: Optional[str] = None, port: int = 5555) -> (bool, str):
        """Enable TCP/IP mode on the device."""
        prefix = ['-s', serial] if serial else []
        try:
            res = self.run_adb(prefix + ['tcpip', str(port)])
            output = (res.stdout + res.stderr).strip()
            if "restarting in TCP mode" in output or res.returncode == 0:
                return True, output or f"TCP/IP mode enabled on port {port}"
            return False, output
        except Exception as e:
            return False, str(e)

    def connect_wireless(self, ip: str, port: int = 5555) -> (bool, str):
        """Connect to device over Wi-Fi (adb connect ip:port)."""
        target = f"{ip.strip()}:{port}" if ":" not in ip else ip.strip()
        try:
            res = self.run_adb(['connect', target], timeout=8)
            output = (res.stdout + res.stderr).strip()
            if "connected to" in output.lower():
                self.add_recent_ip(ip.strip())
                return True, output
            return False, output
        except Exception as e:
            return False, str(e)

    def disconnect_wireless(self, target: Optional[str] = None) -> (bool, str):
        """Disconnect wireless device or all devices."""
        args = ['disconnect']
        if target:
            args.append(target)
        try:
            res = self.run_adb(args)
            return True, (res.stdout + res.stderr).strip()
        except Exception as e:
            return False, str(e)

    def restart_adb(self) -> (bool, str):
        """Kill and restart ADB server."""
        try:
            self.run_adb(['kill-server'])
            time.sleep(1)
            res = self.run_adb(['start-server'])
            return True, "ADB server successfully restarted."
        except Exception as e:
            return False, f"Failed to restart ADB: {str(e)}"

    def send_keyevent(self, keycode: int, serial: Optional[str] = None) -> bool:
        """Inject an Android keyevent (Home=3, Back=4, Power=26, VolUp=24, VolDown=25, AppSwitch=187)."""
        prefix = ['-s', serial] if serial else []
        res = self.run_adb(prefix + ['shell', 'input', 'keyevent', str(keycode)])
        return res.returncode == 0

    def take_screenshot(self, output_dir: str, serial: Optional[str] = None) -> (bool, str):
        """Capture screen from device and save directly to PC."""
        abs_output_dir = os.path.abspath(output_dir)
        os.makedirs(abs_output_dir, exist_ok=True)
        filename = f"screenshot_{int(time.time())}.png"
        filepath = os.path.join(abs_output_dir, filename)
        prefix = ['-s', serial] if serial else []

        try:
            # Capture using exec-out to write binary directly to file
            cmd = [self.adb_path] + prefix + ['exec-out', 'screencap', '-p']
            kwargs = self._get_subprocess_flags()
            with open(filepath, 'wb') as f:
                subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True, **kwargs)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                return True, filepath
        except Exception:
            pass

        # Fallback: capture on-device then pull (bulletproof across all Android ROMs)
        try:
            temp_device_path = "/sdcard/scrcpy_temp_cap.png"
            self.run_adb(prefix + ['shell', 'screencap', '-p', temp_device_path])
            self.run_adb(prefix + ['pull', temp_device_path, filepath])
            self.run_adb(prefix + ['shell', 'rm', '-f', temp_device_path])
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                return True, filepath
            return False, "Captured file was empty or device was locked."
        except Exception as e:
            return False, str(e)

    def install_apk(self, apk_path: str, serial: Optional[str] = None) -> (bool, str):
        """Install an APK file on device."""
        if not os.path.isfile(apk_path):
            return False, "APK file not found."
        prefix = ['-s', serial] if serial else []
        res = self.run_adb(prefix + ['install', '-r', apk_path], timeout=60)
        out = (res.stdout + res.stderr).strip()
        return res.returncode == 0 and "Success" in out, out

    def get_device_details(self, serial: Optional[str] = None) -> Dict:
        """
        Fetch device company/brand, model, market name, Android OS version,
        and live battery stats in a single fast ADB batch shell command (~150ms).
        """
        prefix = ['-s', serial] if serial else []
        cmd = prefix + [
            'shell',
            'getprop ro.product.brand; echo ___SEP___; '
            'getprop ro.product.manufacturer; echo ___SEP___; '
            'getprop ro.product.model; echo ___SEP___; '
            'getprop ro.product.marketname; echo ___SEP___; '
            'getprop ro.build.version.release; echo ___SEP___; '
            'dumpsys battery'
        ]
        res = self.run_adb(cmd, timeout=4)
        details = {
            "brand": "Android",
            "manufacturer": "",
            "model": "Device",
            "market_name": "",
            "android_version": "Android",
            "battery_level": "--",
            "battery_charging": False,
            "battery_temp": ""
        }
        if res.returncode == 0 and res.stdout:
            parts = res.stdout.split("___SEP___")
            if len(parts) >= 5:
                brand = parts[0].strip()
                mfr = parts[1].strip()
                model = parts[2].strip()
                market = parts[3].strip()
                release = parts[4].strip()
                
                if brand:
                    details["brand"] = brand
                if mfr:
                    details["manufacturer"] = mfr
                if model:
                    details["model"] = model
                if market:
                    details["market_name"] = market
                if release:
                    details["android_version"] = f"Android {release}"

            # Parse battery from the last section
            battery_text = parts[-1] if parts else res.stdout
            for line in battery_text.splitlines():
                line = line.strip()
                if line.startswith("level:"):
                    lvl = line.split(":", 1)[1].strip()
                    details["battery_level"] = f"{lvl}%"
                elif line.startswith("status:"):
                    st = line.split(":", 1)[1].strip()
                    if st == "2":  # BATTERY_STATUS_CHARGING
                        details["battery_charging"] = True
                elif "USB powered: true" in line or "AC powered: true" in line:
                    details["battery_charging"] = True
                elif line.startswith("temperature:"):
                    try:
                        raw_temp = int(line.split(":", 1)[1].strip())
                        details["battery_temp"] = f"{raw_temp / 10:.1f}°C"
                    except Exception:
                        pass
        return details

    def build_scrcpy_command(self, options: Dict) -> List[str]:
        """
        Build CLI command list for scrcpy based on user configuration.
        """
        cmd = [self.scrcpy_path]

        # Serial / Device target
        serial = options.get('serial')
        if serial:
            cmd.extend(['-s', serial])

        # Bitrate
        bitrate = options.get('bitrate')
        if bitrate and bitrate != 'Default':
            cmd.extend(['-b', str(bitrate)])

        # Max resolution / size
        max_size = options.get('max_size')
        if max_size and max_size not in ('Original', 'Native'):
            cmd.extend(['-m', str(max_size)])

        # Max FPS (GNU getopt with equals)
        max_fps = options.get('max_fps')
        if max_fps and max_fps != 'Default':
            cmd.append(f'--max-fps={max_fps}')

        # Video Codec
        video_codec = options.get('video_codec')
        if video_codec and video_codec not in ('Default', 'Default (Auto)'):
            cmd.append(f'--video-codec={video_codec.lower()}')

        # Orientation
        orientation = options.get('orientation')
        if orientation and orientation != 'Auto':
            mapping = {'0° (Portrait)': '0', '90° (Landscape)': '90', '180° (Inverted)': '180', '270° (Landscape)': '270'}
            val = mapping.get(orientation, orientation)
            cmd.append(f'--orientation={val}')

        # Video Source (Screen vs Camera)
        video_source = options.get('video_source')
        if video_source == 'Camera':
            cmd.append('--video-source=camera')

        # Input Controls (Mouse and Keyboard)
        # Note: If video_source is Camera, scrcpy disables control automatically
        is_camera = (video_source == 'Camera')
        control_enabled = options.get('control', True)
        if not is_camera:
            if not control_enabled:
                cmd.append('--no-control')
            else:
                if not options.get('mouse_control', True):
                    cmd.append('--mouse=disabled')
                if not options.get('keyboard_control', True):
                    cmd.append('--keyboard=disabled')
                if options.get('no_mouse_hover', False):
                    cmd.append('--no-mouse-hover')

        # Gaming / Ultra-Low Latency Mode
        if options.get('game_mode', False):
            cmd.append('--display-buffer=0')
            if not options.get('no_audio', False):
                cmd.append('--audio-buffer=20')
            if '--no-mouse-hover' not in cmd and not is_camera and control_enabled:
                cmd.append('--no-mouse-hover')

        # Window & Display options
        # Note: If control is disabled or in camera mode, scrcpy cannot send -S, -w, or -t
        can_send_control_cmds = (not is_camera) and control_enabled
        if options.get('turn_screen_off', False) and can_send_control_cmds:
            cmd.append('-S')
        if options.get('stay_awake', False) and can_send_control_cmds:
            cmd.append('-w')
        if options.get('always_on_top', False):
            cmd.append('--always-on-top')
        if options.get('fullscreen', False):
            cmd.append('-f')
        if options.get('show_touches', False) and can_send_control_cmds:
            cmd.append('-t')
        if options.get('borderless', False):
            cmd.append('--window-borderless')
        if options.get('no_audio', False):
            cmd.append('--no-audio')

        # Recording
        if options.get('record', False):
            record_folder = options.get('record_folder') or os.path.join(self.base_dir, "recordings")
            os.makedirs(record_folder, exist_ok=True)
            record_format = options.get('record_format', 'mp4').lower()
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"scrcpy_{timestamp}.{record_format}"
            out_path = os.path.join(record_folder, filename)
            self.last_record_file = out_path
            cmd.extend(['--record', out_path])
        else:
            self.last_record_file = None

        # Window title
        cmd.extend(['--window-title', 'SCRCPY by Sneak'])

        return cmd

    def start_scrcpy(
        self,
        options: Dict,
        log_callback: Optional[Callable[[str, str], None]] = None,
        exit_callback: Optional[Callable[[int], None]] = None
    ) -> bool:
        """
        Launch scrcpy asynchronously in background thread, piping logs in real time.
        log_callback signature: log_callback(message, level)
        exit_callback signature: exit_callback(return_code)
        """
        if self.is_running():
            if log_callback:
                log_callback("Scrcpy is already running!", "WARN")
            return False

        cmd = self.build_scrcpy_command(options)
        
        if log_callback:
            log_callback(f"Executing: {' '.join(cmd)}", "INFO")

        def _worker():
            self._stop_event.clear()
            kwargs = {}
            if os.name == 'nt':
                # Use CREATE_NO_WINDOW to hide console, but NEVER use SW_HIDE as that hides the SDL2 GUI window!
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            proc = None
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=self.scrcpy_dir if os.path.isdir(self.scrcpy_dir) else self.base_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    **kwargs
                )
                self.active_process = proc

                for line in iter(proc.stdout.readline, ''):
                    if line:
                        msg = line.strip()
                        level = "INFO"
                        if "error" in msg.lower():
                            level = "ERROR"
                        elif "warn" in msg.lower():
                            level = "WARN"
                        if log_callback:
                            log_callback(msg, level)
                    if self._stop_event.is_set():
                        break

                try:
                    if proc.stdout:
                        proc.stdout.close()
                except Exception:
                    pass

                return_code = proc.wait()
                if log_callback:
                    log_callback(f"Scrcpy closed (code {return_code}).", "INFO")
                if exit_callback:
                    exit_callback(return_code)
            except Exception as e:
                if log_callback:
                    log_callback(f"Scrcpy execution error: {str(e)}", "ERROR")
                if exit_callback:
                    exit_callback(-1)
            finally:
                self.active_process = None

        self.process_thread = threading.Thread(target=_worker, daemon=True)
        self.process_thread.start()
        return True

    def stop_scrcpy(self):
        """Terminate the running scrcpy process cleanly and forcefully."""
        self._stop_event.set()
        proc = self.active_process
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                proc.terminate()
            except Exception:
                pass
            if os.name == 'nt' and proc.pid:
                try:
                    subprocess.run(
                        ['taskkill', '/F', '/T', '/PID', str(proc.pid)],
                        capture_output=True,
                        **self._get_subprocess_flags()
                    )
                except Exception:
                    pass

        # Always forcefully terminate ANY lingering/orphaned scrcpy.exe on Windows
        if os.name == 'nt':
            try:
                subprocess.run(
                    ['taskkill', '/F', '/IM', 'scrcpy.exe'],
                    capture_output=True,
                    **self._get_subprocess_flags()
                )
            except Exception:
                pass

        self.active_process = None

    def is_running(self) -> bool:
        """Check if scrcpy process is currently alive."""
        return self.active_process is not None and self.active_process.poll() is None

    # Config & Preset Persistence
    def load_config(self) -> Dict:
        """Load user configuration and recent IPs from file."""
        default_config = {
            "bitrate": "8M",
            "max_size": "Original",
            "max_fps": "60",
            "video_codec": "Default",
            "orientation": "Auto",
            "turn_screen_off": True,
            "stay_awake": True,
            "always_on_top": False,
            "fullscreen": False,
            "show_touches": False,
            "borderless": False,
            "no_audio": False,
            "record": False,
            "record_format": "mp4",
            "record_folder": os.path.join(self.base_dir, "recordings"),
            "recent_ips": []
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    default_config.update(data)
            except Exception:
                pass
        return default_config

    def save_config(self, new_config: Dict):
        """Persist settings to scrcpy_config.json."""
        self.config.update(new_config)
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def add_recent_ip(self, ip: str):
        """Save a successfully connected IP to recent list."""
        if not ip:
            return
        ips = self.config.get("recent_ips", [])
        if ip in ips:
            ips.remove(ip)
        ips.insert(0, ip)
        self.config["recent_ips"] = ips[:10]  # keep last 10
        self.save_config({"recent_ips": self.config["recent_ips"]})
