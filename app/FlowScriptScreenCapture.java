package app.flowscript;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.PixelFormat;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Handler;
import android.os.Looper;
import android.util.DisplayMetrics;
import android.view.WindowManager;

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;

public class FlowScriptScreenCapture {

    private static MediaProjection mediaProjection;
    private static int resultCode;
    private static Intent resultData;
    private static boolean hasPermission = false;

    public static final int REQUEST_CODE = 1001;

    public static void setProjectionResult(int code, Intent data) {
        resultCode = code;
        resultData = data;
        hasPermission = (code == Activity.RESULT_OK);
    }

    public static boolean hasPermission() {
        return hasPermission;
    }

    public static void requestPermission(Activity activity) {
        MediaProjectionManager mpm = (MediaProjectionManager)
            activity.getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        activity.startActivityForResult(mpm.createScreenCaptureIntent(), REQUEST_CODE);
    }

    public static byte[] takeScreenshot(Context context) {
        if (!hasPermission || resultData == null) {
            return null;
        }

        try {
            MediaProjectionManager mpm = (MediaProjectionManager)
                context.getSystemService(Context.MEDIA_PROJECTION_SERVICE);

            if (mediaProjection == null) {
                mediaProjection = mpm.getMediaProjection(resultCode, resultData);
            }

            WindowManager wm = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
            DisplayMetrics metrics = new DisplayMetrics();
            wm.getDefaultDisplay().getMetrics(metrics);

            int width = metrics.widthPixels;
            int height = metrics.heightPixels;
            int density = metrics.densityDpi;

            ImageReader imageReader = ImageReader.newInstance(
                width, height, PixelFormat.RGBA_8888, 2
            );

            VirtualDisplay virtualDisplay = mediaProjection.createVirtualDisplay(
                "FlowScriptCapture",
                width, height, density,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                imageReader.getSurface(), null, null
            );

            Thread.sleep(200);

            Image image = imageReader.acquireLatestImage();
            if (image == null) {
                virtualDisplay.release();
                imageReader.close();
                return null;
            }

            Image.Plane[] planes = image.getPlanes();
            ByteBuffer buffer = planes[0].getBuffer();
            int pixelStride = planes[0].getPixelStride();
            int rowStride = planes[0].getRowStride();
            int rowPadding = rowStride - pixelStride * width;

            Bitmap bitmap = Bitmap.createBitmap(
                width + rowPadding / pixelStride, height, Bitmap.Config.ARGB_8888
            );
            bitmap.copyPixelsFromBuffer(buffer);
            bitmap = Bitmap.createBitmap(bitmap, 0, 0, width, height);

            image.close();
            virtualDisplay.release();
            imageReader.close();

            ByteArrayOutputStream stream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.PNG, 90, stream);
            return stream.toByteArray();

        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
