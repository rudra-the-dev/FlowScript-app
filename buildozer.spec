[app]
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.3
requirements = python3==3.10.12,kivy==2.2.1,requests,certifi
android.permissions = INTERNET,BIND_ACCESSIBILITY_SERVICE,FOREGROUND_SERVICE,FOREGROUND_SERVICE_DATA_SYNC,RECEIVE_BOOT_COMPLETED,POST_NOTIFICATIONS,READ_MEDIA_IMAGES
android.api = 34
android.minapi = 26
android.ndk = 25.1.8937393
android.build_tools_version = 34.0.0
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.add_src = app/FlowScriptService.java,app/FlowScriptForegroundService.java,app/FlowScriptScreenCapture.java
android.add_res = res
android.add_manifests = manifest_patch.xml
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.1.8937393
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1