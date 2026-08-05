package com.trojans.aerofleetx.mobileapp;

import android.Manifest;
import android.content.ActivityNotFoundException;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.MimeTypeMap;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.activity.ComponentActivity;
import androidx.activity.OnBackPressedCallback;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class AeroInspectActivity extends ComponentActivity {
    private static final String APP_ORIGIN = "https://app.local";
    private static final String START_URL = APP_ORIGIN + "/index.html";
    private static final int REQUEST_WEB_PERMISSIONS = 5101;
    private static final int REQUEST_FILE_CHOOSER = 5102;
    private static final long MAX_EXPORT_BYTES = 10L * 1024L * 1024L;

    private final ExecutorService ioExecutor = Executors.newSingleThreadExecutor();
    private WebView webView;
    private PermissionRequest pendingPermissionRequest;
    private String[] pendingWebResources = new String[0];
    private ValueCallback<Uri[]> fileChooserCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(7, 27, 43));
        getWindow().setNavigationBarColor(Color.WHITE);

        webView = new WebView(this);
        webView.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(webView);
        configureWebView();
        configureBackNavigation();

        if (savedInstanceState == null || webView.restoreState(savedInstanceState) == null) {
            webView.loadUrl(START_URL);
        }
    }

    private void configureBackNavigation() {
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack();
                    return;
                }
                setEnabled(false);
                getOnBackPressedDispatcher().onBackPressed();
            }
        });
    }

    private void configureWebView() {
        final WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setSupportMultipleWindows(false);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSaveFormData(false);

        CookieManager.getInstance().setAcceptCookie(false);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            CookieManager.getInstance().setAcceptThirdPartyCookies(webView, false);
        }
        WebView.setWebContentsDebuggingEnabled(
                (getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
    WebView.startSafeBrowsing(this, null);
}

        webView.setWebViewClient(new LocalAssetWebViewClient());
        webView.setWebChromeClient(new SecureChromeClient());
        webView.addJavascriptInterface(new AeroNativeBridge(), "AeroNative");
    }

    private final class LocalAssetWebViewClient extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
            return serveLocalAsset(request.getUrl());
        }

        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
            return serveLocalAsset(Uri.parse(url));
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            return handleNavigation(request.getUrl());
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, String url) {
            return handleNavigation(Uri.parse(url));
        }

    }

    private boolean handleNavigation(Uri uri) {
        if (uri != null && "https".equalsIgnoreCase(uri.getScheme())
                && "app.local".equalsIgnoreCase(uri.getHost())) {
            return false;
        }
        Toast.makeText(this, "External navigation is disabled in Research Edition.", Toast.LENGTH_SHORT).show();
        return true;
    }

    private WebResourceResponse serveLocalAsset(Uri uri) {
        if (uri == null || !"https".equalsIgnoreCase(uri.getScheme())
                || !"app.local".equalsIgnoreCase(uri.getHost())) {
            return null;
        }
        String path = uri.getPath();
        if (path == null || path.equals("/") || path.isEmpty()) path = "/index.html";
        path = path.startsWith("/") ? path.substring(1) : path;
        if (path.contains("..") || path.contains("\\") || path.indexOf('\0') >= 0) {
            return response(403, "Forbidden", "text/plain", "Blocked path");
        }
        final String assetPath = "web/" + path;
        try {
            InputStream input = getAssets().open(assetPath);
            WebResourceResponse result = new WebResourceResponse(mimeFor(path), "UTF-8", input);
            HashMap<String, String> headers = new HashMap<>();
            headers.put("Content-Security-Policy", "default-src 'self' data: blob:; img-src 'self' data: blob:; media-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'");
            headers.put("X-Content-Type-Options", "nosniff");
            headers.put("Referrer-Policy", "no-referrer");
            headers.put("Permissions-Policy", "camera=(self), microphone=(self), geolocation=()");
            result.setResponseHeaders(headers);
            return result;
        } catch (IOException notFound) {
            return response(404, "Not Found", "text/plain", "Asset not found");
        }
    }

    private WebResourceResponse response(int code, String reason, String mime, String body) {
        HashMap<String, String> headers = new HashMap<>();
        headers.put("Cache-Control", "no-store");
        return new WebResourceResponse(mime, "UTF-8", code, reason, headers,
                new java.io.ByteArrayInputStream(body.getBytes(StandardCharsets.UTF_8)));
    }

    private String mimeFor(String path) {
        String extension = MimeTypeMap.getFileExtensionFromUrl(path);
        String mime = MimeTypeMap.getSingleton().getMimeTypeFromExtension(
                extension == null ? "" : extension.toLowerCase(Locale.ROOT));
        if (mime != null) return mime;
        if (path.endsWith(".webmanifest")) return "application/manifest+json";
        if (path.endsWith(".js")) return "application/javascript";
        if (path.endsWith(".css")) return "text/css";
        return "application/octet-stream";
    }

    private final class SecureChromeClient extends WebChromeClient {
        @Override
        public void onPermissionRequest(PermissionRequest request) {
            runOnUiThread(() -> requestWebPermissions(request));
        }

        @Override
        public void onPermissionRequestCanceled(PermissionRequest request) {
            if (request == pendingPermissionRequest) clearPendingPermission();
        }

        @Override
        public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> callback,
                                         FileChooserParams params) {
            if (fileChooserCallback != null) fileChooserCallback.onReceiveValue(null);
            fileChooserCallback = callback;
            Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT)
                    .addCategory(Intent.CATEGORY_OPENABLE)
                    .setType("image/*");
            try {
                startActivityForResult(intent, REQUEST_FILE_CHOOSER);
                return true;
            } catch (ActivityNotFoundException error) {
                fileChooserCallback.onReceiveValue(null);
                fileChooserCallback = null;
                Toast.makeText(AeroInspectActivity.this, "No image picker is available.", Toast.LENGTH_SHORT).show();
                return false;
            }
        }
    }

    private void requestWebPermissions(PermissionRequest request) {
        Uri origin = request.getOrigin();
        if (origin == null || !"https".equalsIgnoreCase(origin.getScheme())
                || !"app.local".equalsIgnoreCase(origin.getHost())) {
            request.deny();
            return;
        }
        Set<String> requested = new HashSet<>(Arrays.asList(request.getResources()));
        ArrayList<String> androidPermissions = new ArrayList<>();
        ArrayList<String> webResources = new ArrayList<>();

        if (requested.contains(PermissionRequest.RESOURCE_VIDEO_CAPTURE)) {
            webResources.add(PermissionRequest.RESOURCE_VIDEO_CAPTURE);
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
                androidPermissions.add(Manifest.permission.CAMERA);
            }
        }
        if (requested.contains(PermissionRequest.RESOURCE_AUDIO_CAPTURE)) {
            webResources.add(PermissionRequest.RESOURCE_AUDIO_CAPTURE);
            if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                androidPermissions.add(Manifest.permission.RECORD_AUDIO);
            }
        }
        if (webResources.isEmpty()) {
            request.deny();
            return;
        }
        pendingPermissionRequest = request;
        pendingWebResources = webResources.toArray(new String[0]);
        if (androidPermissions.isEmpty()) {
            request.grant(pendingWebResources);
            clearPendingPermission();
        } else {
            requestPermissions(androidPermissions.toArray(new String[0]), REQUEST_WEB_PERMISSIONS);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQUEST_WEB_PERMISSIONS || pendingPermissionRequest == null) return;
        ArrayList<String> granted = new ArrayList<>();
        for (String resource : pendingWebResources) {
            if (PermissionRequest.RESOURCE_VIDEO_CAPTURE.equals(resource)
                    && checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                granted.add(resource);
            }
            if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(resource)
                    && checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                granted.add(resource);
            }
        }
        if (granted.isEmpty()) pendingPermissionRequest.deny();
        else pendingPermissionRequest.grant(granted.toArray(new String[0]));
        clearPendingPermission();
    }

    private void clearPendingPermission() {
        pendingPermissionRequest = null;
        pendingWebResources = new String[0];
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQUEST_FILE_CHOOSER || fileChooserCallback == null) return;
        Uri[] result = null;
        if (resultCode == RESULT_OK && data != null && data.getData() != null) {
            result = new Uri[]{data.getData()};
        }
        fileChooserCallback.onReceiveValue(result);
        fileChooserCallback = null;
    }

    public final class AeroNativeBridge {
        @JavascriptInterface
        public void saveTextFile(String requestedName, String text, String requestedMime) {
            final String name = sanitizeFilename(requestedName);
            final String mime = sanitizeMime(requestedMime);
            final byte[] bytes = (text == null ? "" : text).getBytes(StandardCharsets.UTF_8);
            if (bytes.length > MAX_EXPORT_BYTES) {
                runOnUiThread(() -> Toast.makeText(AeroInspectActivity.this,
                        "Export is too large.", Toast.LENGTH_LONG).show());
                return;
            }
            ioExecutor.execute(() -> {
                try {
                    String location = writeExport(name, mime, bytes);
                    runOnUiThread(() -> Toast.makeText(AeroInspectActivity.this,
                            "Saved: " + location, Toast.LENGTH_LONG).show());
                } catch (Exception error) {
                    runOnUiThread(() -> Toast.makeText(AeroInspectActivity.this,
                            "Export failed. Check available storage.", Toast.LENGTH_LONG).show());
                }
            });
        }
    }

    private String writeExport(String name, String mime, byte[] bytes) throws IOException {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME, name);
            values.put(MediaStore.Downloads.MIME_TYPE, mime);
            values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/AeroFleetX");
            values.put(MediaStore.Downloads.IS_PENDING, 1);
            Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (uri == null) throw new IOException("Could not create export");
            try (OutputStream output = getContentResolver().openOutputStream(uri, "w")) {
                if (output == null) throw new IOException("Could not open export");
                output.write(bytes);
            } catch (IOException error) {
                getContentResolver().delete(uri, null, null);
                throw error;
            } catch (RuntimeException error) {
                getContentResolver().delete(uri, null, null);
                throw error;
            }
            values.clear();
            values.put(MediaStore.Downloads.IS_PENDING, 0);
            getContentResolver().update(uri, values, null, null);
            return "Downloads/AeroFleetX/" + name;
        }
        File externalDownloads = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (externalDownloads == null) throw new IOException("External storage is unavailable");
        File directory = new File(externalDownloads, "AeroFleetX");
        if (!directory.exists() && !directory.mkdirs()) throw new IOException("Could not create directory");
        File target = new File(directory, name);
        try (OutputStream output = new FileOutputStream(target)) { output.write(bytes); }
        return target.getAbsolutePath();
    }

    private String sanitizeFilename(String value) {
        String safe = value == null ? "AeroFleetX_Export.txt" : value;
        safe = safe.replaceAll("[^A-Za-z0-9._-]", "_");
        if (safe.trim().isEmpty()) safe = "AeroFleetX_Export.txt";
        return safe.length() > 96 ? safe.substring(safe.length() - 96) : safe;
    }

    private String sanitizeMime(String value) {
        Set<String> allowed = new HashSet<>(Arrays.asList(
                "application/json", "text/calendar", "text/plain", "text/csv"));
        return allowed.contains(value) ? value : "text/plain";
    }

    @Override protected void onSaveInstanceState(Bundle outState) { webView.saveState(outState); super.onSaveInstanceState(outState); }
    @Override protected void onPause() { webView.onPause(); super.onPause(); }
    @Override protected void onResume() { super.onResume(); webView.onResume(); }


    @Override
    protected void onDestroy() {
        clearPendingPermission();
        if (fileChooserCallback != null) fileChooserCallback.onReceiveValue(null);
        fileChooserCallback = null;
        webView.removeJavascriptInterface("AeroNative");
        webView.stopLoading();
        webView.destroy();
        ioExecutor.shutdownNow();
        super.onDestroy();
    }

}
