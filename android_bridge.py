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
    "camera": "com.android.camera",
    "settings": "com.android.settings",
    "play store": "com.android.vending",
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
    if package: return package

    installed = get_installed_apps()
    for app in installed:
        if normalize(app["label"]) == name_norm:
            return app["package"]
    return None

def open_app(app_name):
    package = resolve_package(app_name.strip())
    if not package: return False, f"App {app_name} not found"

    try:
        from jnius import autoclass
        context = get_context()
        Intent = autoclass('android.content.Intent')
        pm = context.getPackageManager()
        launch_intent = pm.getLaunchIntentForPackage(package)
        if launch_intent:
            launch_intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(launch_intent)
            return True, f"Opened {app_name}"
        return False, "Could not create launch intent"
    except Exception as e:
        return False, str(e)

def start_foreground_service():
    try:
        from jnius import autoclass
        context = get_context()
        Intent = autoclass('android.content.Intent')
        # Updated package path
        ServiceClass = autoclass('app.flowscript.FlowScriptForegroundService')
        intent = Intent(context, ServiceClass)
        if autoclass('android.os.Build').VERSION.SDK_INT >= 26:
            context.startForegroundService(intent)
        else:
            context.startService(intent)
    except Exception as e:
        print(f"Service start error: {e}")

def stop_foreground_service():
    try:
        from jnius import autoclass
        context = get_context()
        Intent = autoclass('android.content.Intent')
        ServiceClass = autoclass('app.flowscript.FlowScriptForegroundService')
        intent = Intent(context, ServiceClass)
        context.stopService(intent)
    except Exception as e:
        print(f"Service stop error: {e}")

def take_screenshot():
    try:
        from jnius import autoclass
        context = get_context()
        # Updated package path
        CaptureClass = autoclass('app.flowscript.FlowScriptScreenCapture')
        if not CaptureClass.hasPermission():
            return None
        img_bytes = CaptureClass.takeScreenshot(context)
        if img_bytes:
            return base64.b64encode(bytes(img_bytes)).decode()
        return None
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None

def get_accessibility_tree():
    try:
        from jnius import autoclass
        # Updated package path
        ServiceClass = autoclass('app.flowscript.FlowScriptService')
        service = ServiceClass.getInstance()
        if not service:
            print("Accessibility Service not bound yet")
            return []
        root = service.getRootInActiveWindow()
        if not root: return []
        elements = []
        collect_nodes(root, elements)
        return elements
    except Exception as e:
        print(f"Tree error: {e}")
        return []

def collect_nodes(node, elements):
    if node is None: return
    text = str(node.getText()) if node.getText() else ""
    desc = str(node.getContentDescription()) if node.getContentDescription() else ""
    label = text or desc
    if label:
        from jnius import autoclass
        Rect = autoclass('android.graphics.Rect')
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

# ... (perform_tap and perform_swipe remain the same but ensure they use correct imports)

def run_automation(task):
    step = 0
    history = []
    start_foreground_service()
    
    while step < MAX_STEPS:
        screenshot = take_screenshot()
        tree = get_accessibility_tree()
        
        if not screenshot:
            print("Failed to capture screen")
            break

        try:
            response = requests.post(
                f"{BACKEND_URL}/vision/next-action",
                json={"screenshot": screenshot, "task": task, "accessibility_tree": tree, "step": step},
                timeout=30
            )
            data = response.json()
            if data.get("status") == "done": break
            
            # Logic for TAP/TYPE/SWIPE based on backend data...
            step += 1
            time.sleep(1)
        except Exception as e:
            print(f"Loop error: {e}")
            break
            
    stop_foreground_service()
