package org.kivy.android;

public interface PythonUsbListener {
    void onUsbOpened(int device_id, int fd);
    void onUsbNotOpened(int device_id);
}
