[app]
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.2
requirements = python3,kivy,requests
android.permissions = INTERNET,BIND_ACCESSIBILITY_SERVICE,FOREGROUND_SERVICE,RECEIVE_BOOT_COMPLETED
android.api = 34
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.add_src = FlowScriptService.java
android.add_res = res
orientation = portrait
fullscreen = 0
android.manifest.intent_filters = <service android:name="app.flowscript.FlowScriptService" android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE" android:exported="true"><intent-filter><action android:name="android.accessibilityservice.AccessibilityService" /></intent-filter><meta-data android:name="android.accessibilityservice" android:resource="@xml/accessibility_service" /></service>

[buildozer]
log_level = 2