package org.kivy.android;

import android.os.SystemClock;

import java.io.InputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.Runnable;
import java.lang.Integer;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;


import android.view.ViewGroup;
import android.view.KeyEvent;
import android.view.Window;
import android.view.ViewGroup.LayoutParams;
import android.view.WindowManager;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.PendingIntent;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ActivityInfo;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.pm.PackageManager;
import android.util.Log;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.PowerManager;
import android.widget.Toast;
import android.widget.ImageView;
import android.widget.AbsoluteLayout;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;

import android.net.Uri;

import androidx.core.view.ViewCompat;
import androidx.core.app.ActivityCompat;

import org.renpy.android.ResourceManager;

import org.kivy.android.launcher.Project;

import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbManager;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbInterface;
import android.hardware.usb.UsbEndpoint;

import org.qtproject.qt.android.bindings.QtActivity;

import org.kivy.android.PythonUsbListener;

public class PythonActivity extends QtActivity implements ActivityCompat.OnRequestPermissionsResultCallback {
    private static final String TAG = "PythonActivity";
    private static String ACTION_USB_PERMISSION = "org.kivy.android.USB_PERMISSION";

    private ResourceManager resourceManager = null;
    public static PythonActivity mActivity = null;
    public static boolean mBrokenLibraries;
    protected static ViewGroup mLayout;

    public static native void nativeSetenv(String name, String value);
    public static native void setNativeDescriptor(int fd);
    public static native void releaseNativeDescriptor();

    public String getAppRoot() {
        return getFilesDir().getAbsolutePath() + "/app";
    }

    public String getEntryPoint(String search_dir) {
        /* Get the main file (.pyc|.py) depending on if we
         * have a compiled version or not.
         */
        File mainFile = new File(search_dir + "/main.pyc");
        if (mainFile.exists()) {
            return "main.pyc";
        }
        return "main.py";
    }

    public static void initialize() {
        // The static nature of the singleton and Android quirkyness force us to initialize everything here
        // Otherwise, when exiting the app and returning to it, these variables *keep* their pre exit values
        mLayout = null;
        mBrokenLibraries = false;
    }

    private void loadNativeLib() {
        Log.v(TAG, "loading native lib");
        String libPath = this.getFilesDir().getParentFile().getAbsolutePath() + "/lib";
        Log.v(TAG, "native lib dir=" + libPath);
        try {
            System.loadLibrary("main");
        } catch (java.lang.UnsatisfiedLinkError e) {
            // alternate library load, some Android 5 devices fail
            // the above loadLibrary call.
            Log.v(TAG, "loading native lib (alt)");
            // String libPath = this.getFilesDir().getParentFile().getAbsolutePath() + "/lib";
            System.load(libPath + "/libmain.so");
        }
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        Log.v(TAG, "My onCreate running");
        resourceManager = new ResourceManager(this);

        this.mActivity = this;

        loadNativeLib();

        super.onCreate(savedInstanceState);

        if (!getPackageManager().hasSystemFeature(PackageManager.FEATURE_USB_HOST)) {
            Log.v(TAG, "No System Feature USB HOST");
            return;
        }

        IntentFilter filter = new IntentFilter();
        filter.addAction(ACTION_USB_PERMISSION);
        if (android.os.Build.VERSION.SDK_INT >= 26) {
            registerReceiver(usbPermissionReceiver, filter, 4);
            // RECEIVER_EXPORTED = 2
            // RECEIVER_NOT_EXPORTED = 4
        } else {
            registerReceiver(usbPermissionReceiver, filter);
        }
    }

    public void setSecureWindow(boolean secure) {
        runOnUiThread(new Runnable() {
            private Activity mActivity;
            private boolean mEnable;

            public Runnable _initialize(Activity activity, boolean enable) {
                this.mActivity = activity;
                this.mEnable = enable;
                return this;
            }

            @Override
            public void run() {
                Window window = this.mActivity.getWindow();

                if ( !((window.getAttributes().flags & WindowManager.LayoutParams.FLAG_SECURE) != 0) ^ mEnable)
                    return; // no change needed

                if (mEnable) {
                    Log.v(TAG, "Setting Secure Window");
                    window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE);
                } else {
                    Log.v(TAG, "UnSetting Secure Window");
                    window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE);
                    // The below forces a redraw of the window/view, which is needed on some phones
                    // to actually clear the flag. However on some other phones, it crashes the app...
                    // see https://github.com/spesmilo/electrum/issues/8522
                    /*if (ViewCompat.isAttachedToWindow(window.getDecorView())) {
                        WindowManager wm = this.mActivity.getWindowManager();
                        wm.removeViewImmediate(window.getDecorView());
                        wm.addView(window.getDecorView(), window.getAttributes());
                    }*/
                }
            }
        }._initialize(this, secure));
    }

    public List<UsbDevice> enumerateUsb() {
        UsbManager usbManager = (UsbManager) getSystemService(Context.USB_SERVICE);
        HashMap<String, UsbDevice> deviceList = usbManager.getDeviceList();
        for (UsbDevice usbDevice : deviceList.values()) {
            Log.v(TAG, String.format("0x%04X", usbDevice.getVendorId()) + ":" +
            String.format("0x%04X", usbDevice.getProductId()) + " " +
            usbDevice.getDeviceName() + "/" + usbDevice.getProductName());
        }

        Iterator<UsbDevice> deviceIterator = deviceList.values().iterator();

        while (deviceIterator.hasNext()) {
            UsbDevice device = deviceIterator.next();
            Log.i(TAG,"Model: " + device.getDeviceName());
            Log.i(TAG,"Manufacturer: " + device.getManufacturerName());
            Log.i(TAG,"Product name: " + device.getProductName());
            Log.i(TAG,"ID: " + device.getDeviceId());
            try {
                Log.i(TAG,"Serial number: " + device.getSerialNumber());
            } catch (SecurityException e) {
            }
            Log.i(TAG,"Version: " + device.getVersion());
            Log.i(TAG,"Class: " + device.getDeviceClass()); // USB_CLASS_HID=3
            Log.i(TAG,"  Subclass: " + device.getDeviceSubclass());
            Log.i(TAG,"Protocol: " + device.getDeviceProtocol());
            Log.i(TAG,"Vendor ID " + device.getVendorId());
            Log.i(TAG,"Product ID: " + device.getProductId());
            Log.i(TAG,"Interface count: " + device.getInterfaceCount());
            Log.i(TAG,"---------------------------------------");
            // Get interface details
            for (int index = 0; index < device.getInterfaceCount(); index++) {
                UsbInterface mUsbInterface = device.getInterface(index);
                Log.i(TAG,"  *****     *****");
                Log.i(TAG,"  Interface index: " + index);
                Log.i(TAG,"  Interface ID: " + mUsbInterface.getId());
                Log.i(TAG,"  Interface name: " + mUsbInterface.getName());
                Log.i(TAG,"  Interface class: " + mUsbInterface.getInterfaceClass());
                Log.i(TAG,"    Interface subclass: " + mUsbInterface.getInterfaceSubclass());
                Log.i(TAG,"  Interface protocol: " + mUsbInterface.getInterfaceProtocol());
                Log.i(TAG,"  Endpoint count: " + mUsbInterface.getEndpointCount());
                // Get endpoint details
                for (int epi = 0; epi < mUsbInterface.getEndpointCount(); epi++) {
                    UsbEndpoint mEndpoint = mUsbInterface.getEndpoint(epi);
                    Log.i(TAG,"    ++++   ++++   ++++");
                    Log.i(TAG,"    Endpoint index: " + epi);
                    Log.i(TAG,"    Attributes: " + mEndpoint.getAttributes());
                    Log.i(TAG,"    Direction: " + mEndpoint.getDirection());
                    Log.i(TAG,"    Number: " + mEndpoint.getEndpointNumber());
                    Log.i(TAG,"    Interval: " + mEndpoint.getInterval());
                    Log.i(TAG,"    Packet size: " + mEndpoint.getMaxPacketSize());
                    Log.i(TAG,"    Type: " + mEndpoint.getType());
                }
            }
        }

        return new ArrayList<UsbDevice>(deviceList.values());
    }

    public void openUsbDevice(int id) {
        UsbManager usbManager = (UsbManager) getSystemService(Context.USB_SERVICE);
        HashMap<String, UsbDevice> deviceList = usbManager.getDeviceList();
        for (UsbDevice usbDevice : deviceList.values()) {
            if (usbDevice.getDeviceId() == id) {
                if (usbManager.hasPermission(usbDevice)) {
                    Log.v(TAG, "USB DEVICE HAS PERMISSION");
                    doOpenUsbDevice(usbDevice);
                } else {
                    Intent intent = new Intent(ACTION_USB_PERMISSION);
                    intent.setPackage(getPackageName()); // !
                    PendingIntent pendingIntent = PendingIntent.getBroadcast(this, 0, intent, PendingIntent.FLAG_MUTABLE);
                    Log.v(TAG, "USB DEVICE REQUESTING PERMISSION");
                    usbManager.requestPermission(usbDevice, pendingIntent);
                }
                return;
            }
        }
    }

    private final BroadcastReceiver usbPermissionReceiver = new BroadcastReceiver() {

        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            Log.v(TAG, "UsbPermissionReceiver.onReceive("+action+")");

            if (ACTION_USB_PERMISSION.equals(action)) {
                synchronized(this) {
                    boolean granted = intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false);
                    UsbDevice device = (UsbDevice)intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);

                    if (granted) {
                        // Permission granted, you can now interact with the USB device
                        Log.v(TAG, "UsbPermissionReceiver.onReceive("+action+") granted");
                        if (device != null) {
                            Log.v(TAG, "UsbPermissionReceiver.onReceive("+action+") device=" + device.getProductName());
                            doOpenUsbDevice(device);
                        } else {
                            Log.v(TAG, "UsbPermissionReceiver.onReceive("+action+") no device?");
                        }
                    } else {
                        // Permission rejected, handle the case appropriately
                        Log.v(TAG, "UsbPermissionReceiver.onReceive("+action+") declined");
                        onUsbNotOpened(device.getDeviceId());
                    }
                }
            }
        }
    };

    private void doOpenUsbDevice(UsbDevice device) {
        Log.v(TAG, "doOpenUsbDevice device=" + device.getProductName());
        UsbManager usbManager = (UsbManager) getSystemService(Context.USB_SERVICE);
        UsbDeviceConnection conn = usbManager.openDevice(device);
        Log.v(TAG, "device serial=" + conn.getSerial());
        int fd = conn.getFileDescriptor();
        Log.v(TAG, "connection fd=" + fd);
        this.onUsbOpened(device.getDeviceId(), fd);
    }

    /**
     * Used by android.permissions p4a module to register a call back after
     * requesting runtime permissions
     **/
    public interface PermissionsCallback {
        void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults);
    }

    private PermissionsCallback permissionCallback;
    private boolean havePermissionsCallback = false;

    public void addPermissionsCallback(PermissionsCallback callback) {
        permissionCallback = callback;
        havePermissionsCallback = true;
        Log.v(TAG, "addPermissionsCallback(): Added callback for onRequestPermissionsResult");
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        Log.v(TAG, "onRequestPermissionsResult()");
        if (havePermissionsCallback) {
            Log.v(TAG, "onRequestPermissionsResult passed to callback");
            permissionCallback.onRequestPermissionsResult(requestCode, permissions, grantResults);
        }
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    }

    /**
     * Used by android.permissions p4a module to check a permission
     **/
    public boolean checkCurrentPermission(String permission) {
        if (android.os.Build.VERSION.SDK_INT < 23)
            return true;

        try {
            java.lang.reflect.Method methodCheckPermission =
                Activity.class.getMethod("checkSelfPermission", String.class);
            Object resultObj = methodCheckPermission.invoke(this, permission);
            int result = Integer.parseInt(resultObj.toString());
            if (result == PackageManager.PERMISSION_GRANTED)
                return true;
        } catch (IllegalAccessException | NoSuchMethodException |
                 InvocationTargetException e) {
        }
        return false;
    }

    /**
     * Used by android.permissions p4a module to request runtime permissions
     **/
    public void requestPermissionsWithRequestCode(String[] permissions, int requestCode) {
        if (android.os.Build.VERSION.SDK_INT < 23)
            return;
        try {
            java.lang.reflect.Method methodRequestPermission =
                Activity.class.getMethod("requestPermissions",
                String[].class, int.class);
            methodRequestPermission.invoke(this, permissions, requestCode);
        } catch (IllegalAccessException | NoSuchMethodException |
                 InvocationTargetException e) {
        }
    }

    public void requestPermissions(String[] permissions) {
        requestPermissionsWithRequestCode(permissions, 1);
    }

    private List<PythonUsbListener> pythonUsbListeners = null;

    public void registerPythonUsbListener(PythonUsbListener listener) {
        if (this.pythonUsbListeners == null)
            this.pythonUsbListeners = new ArrayList<PythonUsbListener>();
        synchronized (this.pythonUsbListeners) {
            this.pythonUsbListeners.add(listener);
        }
    }

    public void unregisterPythonUsbListener(PythonUsbListener listener) {
        if (this.pythonUsbListeners == null)
            return;
        synchronized (this.pythonUsbListeners) {
            this.pythonUsbListeners.remove(listener);
        }
    }

    protected void onUsbOpened(int device_id, int fd) {
        if (this.pythonUsbListeners == null)
            return;
        synchronized (this.pythonUsbListeners) {
            Iterator<PythonUsbListener> iterator = this.pythonUsbListeners.iterator();
            while (iterator.hasNext()) {
                (iterator.next()).onUsbOpened(device_id, fd);
            }
        }
    }

    protected void onUsbNotOpened(int device_id) {
        if (this.pythonUsbListeners == null)
            return;
        synchronized (this.pythonUsbListeners) {
            Iterator<PythonUsbListener> iterator = this.pythonUsbListeners.iterator();
            while (iterator.hasNext()) {
                (iterator.next()).onUsbNotOpened(device_id);
            }
        }
    }

    //----------------------------------------------------------------------------
    // Listener interface for onNewIntent
    //

    public interface NewIntentListener {
        void onNewIntent(Intent intent);
    }

    private List<NewIntentListener> newIntentListeners = null;

    public void registerNewIntentListener(NewIntentListener listener) {
        if (this.newIntentListeners == null)
            this.newIntentListeners = new ArrayList<NewIntentListener>();
        synchronized (this.newIntentListeners) {
            this.newIntentListeners.add(listener);
        }
    }

    public void unregisterNewIntentListener(NewIntentListener listener) {
        if (this.newIntentListeners == null)
            return;
        synchronized (this.newIntentListeners) {
            this.newIntentListeners.remove(listener);
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        if (this.newIntentListeners == null)
            return;
        synchronized (this.newIntentListeners) {
            Iterator<NewIntentListener> iterator = this.newIntentListeners.iterator();
            while (iterator.hasNext()) {
                (iterator.next()).onNewIntent(intent);
            }
        }
    }

    //----------------------------------------------------------------------------
    // Listener interface for onActivityResult
    //

    public interface ActivityResultListener {
        void onActivityResult(int requestCode, int resultCode, Intent data);
    }

    private List<ActivityResultListener> activityResultListeners = null;

    public void registerActivityResultListener(ActivityResultListener listener) {
        if (this.activityResultListeners == null)
            this.activityResultListeners = new ArrayList<ActivityResultListener>();
        synchronized (this.activityResultListeners) {
            this.activityResultListeners.add(listener);
        }
    }

    public void unregisterActivityResultListener(ActivityResultListener listener) {
        if (this.activityResultListeners == null)
            return;
        synchronized (this.activityResultListeners) {
            this.activityResultListeners.remove(listener);
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent intent) {
        if (this.activityResultListeners == null)
            return;
        // this.onResume();
        synchronized (this.activityResultListeners) {
            Iterator<ActivityResultListener> iterator = this.activityResultListeners.iterator();
            while (iterator.hasNext())
                (iterator.next()).onActivityResult(requestCode, resultCode, intent);
        }
    }

}
