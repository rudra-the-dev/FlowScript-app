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


def open_app(app_name):
    name = app_name.lower().strip()
    package = APP_MAP.get(name) or fuzzy_match_app(name)
    if not package:
        return False, f"Could not find app: {app_name}"
    try:
        from jnius import autoclass
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')

        intent = Intent()
        intent.setAction(Intent.ACTION_MAIN)
        intent.addCategory(Intent.CATEGORY_LAUNCHER)
        intent.setPackage(package)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.addFlags(Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED)

        pm = context.getPackageManager()
        activities = pm.queryIntentActivities(intent, 0)

        if activities.size() > 0:
            context.startActivity(intent)
            time.sleep(2)
            return True, f"Opened {app_name}"

        launch_intent = pm.getLaunchIntentForPackage(package)
        if launch_intent:
            launch_intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(launch_intent)
            time.sleep(2)
            return True, f"Opened {app_name}"

        return False, f"App {app_name} not installed"
    except Exception as e:
        return False, f"Error opening {app_name}: {str(e)}"


def fuzzy_match_app(name):
    try:
        context = get_context()
        pm = context.getPackageManager()
        packages = pm.getInstalledPackages(0)
        name_lower = name.lower()
        best_match = None
        best_score = 0
        for i in range(packages.size()):
            pkg = packages.get(i)
            app_name = str(pm.getApplicationLabel(pkg.applicationInfo)).lower()
            pkg_name = str(pkg.packageName).lower()
            score = 0
            if name_lower in app_name:
                score = len(name_lower) / len(app_name)
            elif name_lower in pkg_name:
                score = 0.5
            if score > best_score:
                best_score = score
                best_match = str(pkg.packageName)
        return best_match if best_score > 0.3 else None
    except Exception as e:
        print(f"Fuzzy match error: {e}")
        return None


def take_screenshot():
    try:
        view = get_context().getWindow().getDecorView().getRootView()
        view.setDrawingCacheEnabled(True)
        bitmap = view.getDrawingCache()
        buf = io.BytesIO()
        bitmap_bytes = bytearray(bitmap.getWidth() * bitmap.getHeight() * 4)
        bitmap.copyPixelsToBuffer(bytearray(bitmap_bytes))
        return base64.b64encode(bytes(bitmap_bytes)).decode()
    except Exception as e:
        print(f"Screenshot error: {e}")
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
        Instrumentation = autoclass('android.app.Instrumentation')
        Instrumentation().sendStringSync(text)
        return True
    except Exception as e:
        print(f"Type error: {e}")
        return False


def perform_swipe(direction="up"):
    try:
        display = get_context().getSystemService(Context.WINDOW_SERVICE).getDefaultDisplay()
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
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
        context = get_context()
        builder = NotificationCompat.Builder(context, "flowscript")
        builder.setContentTitle("FlowScript")
        builder.setContentText(message)
        builder.setSmallIcon(autoclass('android.R$drawable').ic_dialog_info)
        builder.setPriority(NotificationCompat.PRIORITY_DEFAULT)
        nm = context.getSystemService(Context.NOTIFICATION_SERVICE)
        nm.notify(1, builder.build())
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

    print(f"Automation started: {task}")

    while step < MAX_STEPS:
        screenshot = take_screenshot()
        if not screenshot:
            return False, "Could not take screenshot"

        tree = get_accessibility_tree()

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
        except Exception as e:
            return False, f"Backend error: {e}"

        status = data.get("status")
        thought = data.get("thought", "")
        print(f"Step {step + 1}: {thought}")

        verification = data.get("verification")
        if verification:
            print(f"Verification: {verification.get('verdict')}")

        if status == "done":
            return True, "Task completed"

        if status in ["needs_help", "failed"]:
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
            perform_tap(x, y)
            history.append(f"Tapped '{data.get('element_text', '')}' at ({x},{y})")
        elif action == "TYPE":
            perform_type(data.get("text", ""))
            history.append(f"Typed: {data.get('text', '')}")
        elif action == "SWIPE":
            perform_swipe(data.get("direction", "up"))
            history.append(f"Swiped {data.get('direction', 'up')}")

        if len(history) > 6:
            history = history[-6:]

        time.sleep(delay_ms / 1000)

    return False, f"Task did not complete within {MAX_STEPS} steps"
