package org.kivy.android;

import java.io.File;

import android.util.Log;

import android.content.Context;

/*
 * Unpacks the app and sets up the environment for start.c. Qt 6.10 dropped
 * the "android.app.static_init_classes" mechanism this class was originally
 * registered with, so PythonActivity.onCreate() drives it explicitly.
 */
public class PythonActivityInit {
    private static final String TAG = "PythonActivityInit";

    private PythonActivity mActivity;

    static {
        Log.v(TAG, "PythonActivityInit static");
    }

    public void setActivity(PythonActivity activity) {
        Log.v(TAG, "PythonActivityInit setActivity running");
        Log.v(TAG, activity.getClass().getName());
        mActivity = activity;
    }

    public void setContext(Context context) {
        Log.v(TAG, "PythonActivityInit setContext running");
        Log.v(TAG, context.getClass().getName());

        String app_root_dir = mActivity.getAppRoot();

        Log.v(TAG, "Ready to unpack");
        PythonUtil.unpackAsset(mActivity, "private", new File(app_root_dir), true);
        PythonUtil.unpackPyBundle(mActivity, mActivity.getApplicationInfo().nativeLibraryDir + "/" + "libpybundle", new File(app_root_dir), false);
        Log.v(TAG, "Device: " + android.os.Build.DEVICE);
        Log.v(TAG, "Model: " + android.os.Build.MODEL);

        String entry_point = mActivity.getEntryPoint(app_root_dir);
        PythonActivity.nativeSetenv("ANDROID_ENTRYPOINT", entry_point);
        PythonActivity.nativeSetenv("ANDROID_ARGUMENT", app_root_dir);
        PythonActivity.nativeSetenv("ANDROID_APP_PATH", app_root_dir);

        String mFilesDirectory = mActivity.getFilesDir().getAbsolutePath();
        Log.v(TAG, "Setting env vars for start.c and Python to use");
        PythonActivity.nativeSetenv("ANDROID_PRIVATE", mFilesDirectory);
        PythonActivity.nativeSetenv("ANDROID_UNPACK", app_root_dir);
        PythonActivity.nativeSetenv("PYTHONHOME", app_root_dir);
        PythonActivity.nativeSetenv("PYTHONPATH", app_root_dir + ":" + app_root_dir + "/lib");
        PythonActivity.nativeSetenv("PYTHONOPTIMIZE", "2");

        Log.v(TAG, "Setting env vars for Qt");
        PythonActivity.nativeSetenv("QT_QUICK_CONTROLS_STYLE", "Material");
    }
}
