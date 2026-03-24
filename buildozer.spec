[app]
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.3

# Added certifi for HTTPS requests and pinned versions for stability
requirements = python3==3.10.12,kivy==2.3.0,requests,certifi

# Cleaned up permissions for API 34
android.permissions = INTERNET, BIND_ACCESSIBILITY_SERVICE, FOREGROUND_SERVICE, FOREGROUND_SERVICE_DATA_SYNC, RECEIVE_BOOT_COMPLETED, POST_NOTIFICATIONS, READ_MEDIA_IMAGES

android.api = 34
android.minapi = 26
android.sdk = 34
android.ndk = 25b
android.build_tools_version = 34.0.0

# Added armeabi-v7a for better device compatibility
android.archs = arm64-v8a, armeabi-v7a

# Ensure these paths are relative to your source.dir
android.add_src = FlowScriptService.java, FlowScriptForegroundService.java, FlowScriptScreenCapture.java
android.add_res = res
android.add_manifests = manifest_patch.xml

[buildozer]
log_level = 2
warn_on_root = 1
