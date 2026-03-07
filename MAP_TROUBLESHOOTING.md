# Map Not Showing - Troubleshooting Guide

## Problem
HTML file opens but map doesn't display - just seeing a blank page or the HTML source code.

## Quick Diagnostic

I've created a simple test file. Please open it and tell me what you see:

```bash
# Open in browser
firefox /tmp/simple_test_map.html
# OR
google-chrome /tmp/simple_test_map.html
# OR
python3 -c "import webbrowser; webbrowser.open('file:///tmp/simple_test_map.html')"
```

## What Should You See?

### ✅ SUCCESS - Map is working:
- OpenStreetMap tiles loading
- Map centered on coordinates
- Red marker visible
- Can zoom and pan
- Status message: "✅ Map loaded successfully!"

### ❌ PROBLEM - Not working:
Tell me which of these you see:

**Option A: Blank/White Page**
- HTML is opening but JavaScript not running
- Possible causes: JavaScript disabled, network issue, browser security

**Option B: HTML Source Code**
- Browser is showing the HTML as text
- File is being opened as text, not rendered as HTML

**Option C: "Loading..." Never Finishes**
- Leaflet.js library not loading
- Network/firewall blocking CDN
- Check browser console (F12) for errors

**Option D: Error Message**
- JavaScript error occurred
- Check browser console (F12) for details

## Browser Console Check

Press **F12** in your browser, then click **Console** tab.

### What errors do you see?

Common errors and solutions:

```
"Failed to load resource: net::ERR_INTERNET_DISCONNECTED"
→ No internet connection - Leaflet needs to download from CDN

"Refused to load stylesheet from 'https://unpkg.com/...'"
→ Content Security Policy or firewall blocking

"L is not defined"
→ Leaflet.js didn't load - check Network tab (F12 → Network)

"Cannot read property 'map' of undefined"
→ Leaflet library loaded but failed to initialize
```

## Manual Test Steps

### Step 1: Check Internet
```bash
curl -I https://unpkg.com/leaflet@1.9.4/dist/leaflet.js
# Should return: HTTP/2 200
```

### Step 2: Check Browser
```bash
# Try opening the file in different browsers
firefox /tmp/simple_test_map.html
google-chrome /tmp/simple_test_map.html
chromium-browser /tmp/simple_test_map.html
```

### Step 3: Check File Content
```bash
head -20 /tmp/simple_test_map.html
# Should show HTML <!DOCTYPE html> not binary/corrupted
```

### Step 4: Try Alternative - Google Maps Link
If Leaflet doesn't work, you can always view in Google Maps directly:

```bash
# For Desert Square example
firefox "https://www.google.com/maps?q=-35.36309804,149.16348567"
```

## Alternative Solutions

### Option 1: Use Google Maps URL (Always Works)
Instead of HTML file, directly open Google Maps:

```python
import webbrowser
lat = -35.36309804
lon = 149.16348567
url = f"https://www.google.com/maps?q={lat},{lon}"
webbrowser.open(url)
```

### Option 2: Use System Map Application
If you have GNOME Maps or similar:

```bash
gnome-maps "geo:-35.36309804,149.16348567"
```

### Option 3: Download Leaflet Locally
If CDN is blocked, download Leaflet locally:

```bash
cd /tmp
wget https://unpkg.com/leaflet@1.9.4/dist/leaflet.css
wget https://unpkg.com/leaflet@1.9.4/dist/leaflet.js
wget -r -np -nH --cut-dirs=4 https://unpkg.com/leaflet@1.9.4/dist/images/
```

Then modify HTML to use local files.

## What I Need From You

Please tell me:

1. **What do you see when the file opens?**
   - Blank page?
   - HTML source code?
   - "Loading..." text?
   - Error message?

2. **What browser are you using?**
   - Firefox?
   - Chrome/Chromium?
   - Other?

3. **What's in the browser console? (F12 → Console)**
   - Any red error messages?
   - Copy and paste the errors

4. **What's in the Network tab? (F12 → Network, then reload)**
   - Do you see requests to `unpkg.com`?
   - Are they showing 200 (green) or red errors?

## Quick Fix: Use Google Maps Instead

If OpenStreetMap continues not working, I can switch the visualizer to open Google Maps directly in the web (no HTML file, no API key needed):

```python
# This always works - opens Google Maps website
import webbrowser
webbrowser.open(f"https://www.google.com/maps?q={lat},{lon}")
```

Would you like me to implement this as a fallback?

---

**Please provide the information above so I can diagnose the issue!**
