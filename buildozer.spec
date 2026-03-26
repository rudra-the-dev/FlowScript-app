[app]
requirements = python3==3.10.12,kivy==2.3.0,requests,certifi
android.api = 34
android.sdk = 34
android.ndk = 25b
android.add_src = app/FlowScriptService.java, app/FlowScriptForegroundService.java, app/FlowScriptScreenCapture.java
android.add_manifests = manifest_patch.xml
