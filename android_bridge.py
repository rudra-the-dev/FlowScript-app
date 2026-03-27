import requests
import base64
import io
import time

BACKEND_URL = "https://flowscript-backend-service.onrender.com"
MAX_STEPS = 15

APP_MAP = {
    "whatsapp": "com.whatsapp",
    "youtube": "com.google.android.youtube",
    "instagram": "com.instagram.android",
    "chrome": "com.android.chrome",
    "gmail": "com.google.android.gm",
    "spotify": "com.spotify.music",
    "maps": "com.google.android.apps.maps",
    "google maps": "com.google.android.apps.maps",
    "camera": "com.android.camera",
    "settings": "com.android.settings",
    "twitter": "com.twitter.android",
    "x": "com.twitter.android",
    "telegram": "org.telegram.messenger",
    "snapchat": "com.snapchat.android",
    "facebook": "com.facebook.katana",
    "netflix": "com.netflix.mediaclient",
    "amazon": "com.amazon.mShop.android.shopping",
    "flipkart": "com.flipkart.android",
    "phonepe": "com.phonepe.app",
    "gpay": "com.google.android.apps.nbu.paisa.user",
    "google pay": "com.google.android.apps.nbu.paisa.user",
    "paytm": "net.one97.paytm",
    "zomato": "com.application.zomato",
    "swiggy": "in.swiggy.android",
    "hotstar": "in.startv.hotstar",
    "prime": "com.amazon.avod.thirdpartyclient",
    "amazon prime": "com.amazon.avod.thirdpartyclient",
    "contacts": "com.android.contacts",
    "phone": "com.android.dialer",
    "messages": "com.google.android.apps.messaging",
    "clock": "com.android.deskclock",
    "calculator": "com.android.calculator2",
    "photos": "com.google.android.apps.photos",
    "play store": "com.android.vending",
    "playstore": "com.android.vending",
    "meet": "com.google.android.apps.tachyon",
    "google meet": "com.google.android.apps.tachyon",
    "zoom": "us.zoom.videomeetings",
    "linkedin": "com.linkedin.android",
    "reddit": "com.reddit.frontpage",
    "discord": "com.discord",
    "truecaller": "com.truecaller",
}


def get_context():
    from jnius import autoclass
    return autoclass('org.kivy.android.PythonActivity').mActivity


def normalize(s):
    return ''.join(c for c in s.lower() if c.isalnum())


def get_installed_apps():
    try:
        from jnius import autoclass
        context = get_context()
        pm = context.getPackageManager()
        Intent = autoclass('android.content.Intent')
        intent = Intent(Intent.ACTION_MAIN)
        intent.addCategory(Intent.CATEGORY_LAUNCHER)
        activities = pm.queryIntentActivities(intent, 0)
        apps = []
        for i in range(activities.size()):
            info = activities.get(i)
            label = str(pm.getApplicationLabel(info.activityInfo.applicationInfo))
            package = str(info.activityInfo.packageName)
            apps.append({"label": label, "package": package})
        return apps
    except Exception as e:
        print(f"get_installed_apps error: {e}")
        return []


def resolve_package(name):
    name_norm = normalize(name)

    package = APP_MAP.get(name.lower().strip())
    if package:
        print(f"Resolved '{name}' from map → {package}")
        return package

    installed = get_installed_apps()
    print(f"Scanning {len(installed)} installed apps for '{name}'")

    exact = None
    contains = []
    for app in installed:
        label_norm = normalize(app["label"])
        if label_norm == name_norm:
            exact = app["package"]
            break
        if name_norm in label_norm or label_norm in name_norm:
            contains.append((len(label_norm), app))

    if exact:
        print(f"Exact match → {exact}")
        return exact

    if contains:
        contains.sort(key=lambda x: x[0])
        best = contains[0][1]
        print(f"Best match: '{best['label']}' → {best['package']}")
        return best["package"]

    print(f"No match for '{name}'. Sample apps:")
    for app in installed[:15]:
        print(f"  {app['label']} → {app['package']}")
    return None


def open_app(app_name):
    package = resolve_package(app_name.strip())

    if not package:
        installed = get_installed_apps()
        labels = [a['label'] for a in installed[:10]]
        return False, f"App '{app_name}' not found. Installed sample: {labels}"

    try:
        from jnius import autoclass
        context = get_context()
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        pm = context.getPackageManager()

        launch_intent = pm.getLaunchIntentForPackage(package)
        if launch_intent:
            launch_intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(launch_intent)
            time.sleep(2)
            return True, f"Opened {app_name}"

        intent = Intent(Intent.ACTION_MAIN)
        intent.addCategory(Intent.CATEGORY_LAUNCHER)
        intent.setPackage(package)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        try:
            context.startActivity(intent)
            time.sleep(2)
            return True, f"Opened {app_name}"
        except:
            pass

        store_intent = Intent(Intent.ACTION_VIEW)
        store_intent.setData(Uri.parse(f"market://details?id={package}"))
        store_intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(store_intent)
        return False, f"App '{app_name}' not installed. Opening Play Store."

    except Exception as e:
        return False, f"Error opening '{app_name}': {str(e)}"


def start_foreground_service():
    try:
        from jnius import autoclass
        context = get_context()
        Intent = autoclass('android.content.Intent')
        ForegroundService = autoclass('app.flowscript.FlowScriptForegroundService')
        intent = Intent(context, ForegroundService)
        if autoclass('android.os.Build').VERSION.SDK_INT >= 26:
            context.startForegroundService(intent)
        else:
            context.startService(intent)
        print("Foreground service started")
    except Exception as e:
        print(f"Foreground service error: {e}")


def stop_foreground_service():
    try:
        from jnius import autoclass
        context = get_context()
        Intent = autoclass('android.content.Intent')
        ForegroundService = autoclass('app.flowscript.FlowScriptForegroundService')
        intent = Intent(context, ForegroundService)
        context.stopService(intent)
        print("Foreground service stopped")
    except Exception as e:
        print(f"Stop foreground service error: {e}")


def notify_debug(message):
    try:
        send_notification(f"[FS] {message}")
    except:
        print(f"DEBUG: {message}")


def take_screenshot():
    try:
        notify_debug("Taking screenshot...")
        from jnius import autoclass
        context = get_context()
        ScreenCapture = autoclass('app.flowscript.FlowScriptScreenCapture')

        if not ScreenCapture.hasPermission():
            notify_debug("Screen capture permission not granted")
            return None

        img_bytes = ScreenCapture.takeScreenshot(context)
        if img_bytes is None:
            notify_debug("Screenshot returned null")
            return None

        notify_debug("Screenshot captured OK")
        return base64.b64encode(bytes(img_bytes)).decode()

    except Exception as e:
        notify_debug(f"Screenshot FAILED: {str(e)[:60]}")
        return None


def get_accessibility_tree():
    try:
        from org.kivy.android import FlowScriptAccessibility
        service = FlowScriptAccessibility.getInstance()
        if not service:
            return []
        root = service.getRootInActiveWindow()
        if not root:
            return []
        elements = []
        collect_nodes(root, elements)
        return elements
    except Exception as e:
        print(f"Accessibility tree error: {e}")
        return []


def collect_nodes(node, elements):
    if node is None:
        return
    text = str(node.getText()) if node.getText() else ""
    desc = str(node.getContentDescription()) if node.getContentDescription() else ""
    label = text or desc
    if label:
        from android.graphics import Rect
        bounds = Rect()
        node.getBoundsInScreen(bounds)
        elements.append({
            "text": label,
            "x": (bounds.left + bounds.right) // 2,
            "y": (bounds.top + bounds.bottom) // 2,
            "bounds": [bounds.left, bounds.top, bounds.right, bounds.bottom],
            "clickable": node.isClickable()
        })
    for i in range(node.getChildCount()):
        collect_nodes(node.getChild(i), elements)


def perform_tap(x, y):
    try:
        from jnius import autoclass
        Instrumentation = autoclass('android.app.Instrumentation')
        MotionEvent = autoclass('android.view.MotionEvent')
        SystemClock = autoclass('android.os.SystemClock')
        inst = Instrumentation()
        down = SystemClock.uptimeMillis()
        inst.sendPointerSync(MotionEvent.obtain(down, down, MotionEvent.ACTION_DOWN, float(x), float(y), 0))
        time.sleep(0.05)
        inst.sendPointerSync(MotionEvent.obtain(down, SystemClock.uptimeMillis(), MotionEvent.ACTION_UP, float(x), float(y), 0))
        return True
    except Exception as e:
        print(f"Tap error: {e}")
        return False


def perform_type(text):
    try:
        from jnius import autoclass
        autoclass('android.app.Instrumentation')().sendStringSync(text)
        return True
    except Exception as e:
        print(f"Type error: {e}")
        return False


def perform_swipe(direction="up"):
    try:
        from jnius import autoclass
        Context = autoclass('android.content.Context')
        Instrumentation = autoclass('android.app.Instrumentation')
        MotionEvent = autoclass('android.view.MotionEvent')
        SystemClock = autoclass('android.os.SystemClock')
        context = get_context()
        display = context.getSystemService(Context.WINDOW_SERVICE).getDefaultDisplay()
        w = display.getWidth()
        h = display.getHeight()
        cx = w // 2
        inst = Instrumentation()
        down = SystemClock.uptimeMillis()
        if direction in ["up", "down"]:
            sy = int(h * 0.7) if direction == "up" else int(h * 0.3)
            ey = int(h * 0.3) if direction == "up" else int(h * 0.7)
            inst.sendPointerSync(MotionEvent.obtain(down, down, MotionEvent.ACTION_DOWN, float(cx), float(sy), 0))
            for i in range(10):
                y = sy + (ey - sy) * i // 10
                inst.sendPointerSync(MotionEvent.obtain(down, SystemClock.uptimeMillis(), MotionEvent.ACTION_MOVE, float(cx), float(y), 0))
                time.sleep(0.01)
            inst.sendPointerSync(MotionEvent.obtain(down, SystemClock.uptimeMillis(), MotionEvent.ACTION_UP, float(cx), float(ey), 0))
        else:
            sx = int(w * 0.8) if direction == "left" else int(w * 0.2)
            ex = int(w * 0.2) if direction == "left" else int(w * 0.8)
            my = h // 2
            inst.sendPointerSync(MotionEvent.obtain(down, down, MotionEvent.ACTION_DOWN, float(sx), float(my), 0))
            for i in range(10):
                x = sx + (ex - sx) * i // 10
                inst.sendPointerSync(MotionEvent.obtain(down, SystemClock.uptimeMillis(), MotionEvent.ACTION_MOVE, float(x), float(my), 0))
                time.sleep(0.01)
            inst.sendPointerSync(MotionEvent.obtain(down, SystemClock.uptimeMillis(), MotionEvent.ACTION_UP, float(ex), float(my), 0))
        return True
    except Exception as e:
        print(f"Swipe error: {e}")
        return False


def send_notification(message):
    try:
        from jnius import autoclass
        context = get_context()
        Build = autoclass('android.os.Build')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        CHANNEL_ID = "flowscript"

        if Build.VERSION.SDK_INT >= 26:
            NotificationChannel = autoclass('android.app.NotificationChannel')
            nm = context.getSystemService(context.NOTIFICATION_SERVICE)
            channel = NotificationChannel(
                CHANNEL_ID,
                "FlowScript",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            nm.createNotificationChannel(channel)
            builder = NotificationBuilder(context, CHANNEL_ID)
        else:
            builder = NotificationBuilder(context)

        builder.setContentTitle("FlowScript")
        builder.setContentText(message)
        builder.setSmallIcon(autoclass('android.R$drawable').ic_dialog_info)
        builder.setAutoCancel(True)

        nm = context.getSystemService(context.NOTIFICATION_SERVICE)
        nm.notify(int(time.time()) % 10000, builder.build())
        return True
    except Exception as e:
        print(f"Notification error: {e}")
        return False


def run_automation(task, on_needs_help=None):
    history = []
    failure_counts = {}
    prev_elements = []
    prev_expected = None
    step = 0

    notify_debug(f"Automation started: {task[:40]}")
    start_foreground_service()

    try:
        while step < MAX_STEPS:
            screenshot = take_screenshot()
            if not screenshot:
                notify_debug("STOPPED: Could not take screenshot")
                return False, "Could not take screenshot"

            tree = get_accessibility_tree()
            notify_debug(f"Step {step+1}: Sending to backend ({len(tree)} elements)")

            try:
                response = requests.post(
                    f"{BACKEND_URL}/vision/next-action",
                    json={
                        "screenshot": screenshot,
                        "task": task,
                        "history": history,
                        "accessibility_tree": tree,
                        "failure_counts": failure_counts,
                        "prev_elements": prev_elements,
                        "prev_expected": prev_expected,
                        "step": step
                    },
                    timeout=30
                )
                data = response.json()
                notify_debug(f"Backend responded: {data.get('status')} — {data.get('thought','')[:40]}")
            except requests.exceptions.Timeout:
                notify_debug("Backend TIMEOUT — no response in 30s")
                stop_foreground_service()
                return False, "Backend timed out"
            except requests.exceptions.ConnectionError:
                notify_debug("Backend CONNECTION ERROR — is server running?")
                stop_foreground_service()
                return False, "Could not connect to backend"
            except Exception as e:
                notify_debug(f"Backend ERROR: {str(e)[:60]}")
                stop_foreground_service()
                return False, f"Backend error: {e}"

            status = data.get("status")
            thought = data.get("thought", "")

            if status == "done":
                notify_debug("Task COMPLETED successfully")
                stop_foreground_service()
                return True, "Task completed"

            if status in ["needs_help", "failed"]:
                notify_debug(f"STOPPED: {thought[:60]}")
                stop_foreground_service()
                if on_needs_help:
                    on_needs_help(thought)
                return False, thought

            action = data.get("action")
            x = data.get("x", 0)
            y = data.get("y", 0)
            delay_ms = data.get("time_delay", 600)

            prev_elements = data.get("prev_elements", [])
            prev_expected = data.get("prev_expected")
            failure_counts = data.get("failure_counts", failure_counts)
            step = data.get("step", step + 1)

            if action == "TAP":
                notify_debug(f"Tapping '{data.get('element_text','')}' at ({x},{y})")
                success = perform_tap(x, y)
                if not success:
                    notify_debug(f"TAP FAILED at ({x},{y})")
                history.append(f"Tapped '{data.get('element_text', '')}' at ({x},{y})")

            elif action == "TYPE":
                text = data.get("text", "")
                notify_debug(f"Typing: {text[:40]}")
                perform_type(text)
                history.append(f"Typed: {text}")

            elif action == "SWIPE":
                direction = data.get("direction", "up")
                notify_debug(f"Swiping {direction}")
                perform_swipe(direction)
                history.append(f"Swiped {direction}")

            if len(history) > 6:
                history = history[-6:]

            time.sleep(delay_ms / 1000)

        notify_debug(f"STOPPED: Reached max {MAX_STEPS} steps")
        stop_foreground_service()
        return False, f"Task did not complete within {MAX_STEPS} steps"

    except Exception as e:
        notify_debug(f"Automation crashed: {str(e)[:60]}")
        stop_foreground_service()
        return False, str(e)