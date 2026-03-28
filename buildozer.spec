[app]
# (Section 1: Basic Info)
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.4

# (Section 2: Requirements)
# Added pyjnius (essential for autoclass) and android (essential for app control)
requirements = python3,kivy==2.3.0,requests,pyjnius,android

# (Section 3: Android Specifics)
# Added foreground service permissions required for API 33+
android.permissions = INTERNET, BIND_ACCESSIBILITY_SERVICE, POST_NOTIFICATIONS, FOREGROUND_SERVICE, FOREGROUND_SERVICE_DATA_SYNC
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.0

# Building for your modern Motorola 5G device
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.add_res = res
android.add_manifests = manifest_patch.xml
orientation = portrait
fullscreen = 0
android.accept_sdk_license = True
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk

[buildozer]
log_level = 2
warn_on_root = 1
