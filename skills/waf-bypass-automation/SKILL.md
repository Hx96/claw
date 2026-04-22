---
name: waf-bypass-automation
description: Web automation with anti-WAF techniques for bypassing cloud protections and downloading protected content. Use when standard browser automation fails due to WAF/anti-bot protection.
on_trigger:
  - "bypass WAF"
  - "绕过防护"
  - "anti-bot"
  - "cloud protection"
  - "aliyun waf"
metadata: {"requires": ["node", "npm"]}
---

# WAF Bypass Automation

## Overview

Advanced browser automation techniques for bypassing Web Application Firewalls (WAF) and anti-bot protections, specifically designed for downloading protected content from sites with Aliyun WAF, Cloudflare, and similar protections.

## Installation

```bash
npm install -g claw-browser-automation
npm install -g playwright-core
```

## Core Techniques

### 1. Browser Fingerprint Spoofing

```bash
# Launch with realistic browser fingerprint
agent-browser set viewport 1920 1080
agent-browser set device "Desktop"
agent-browser set geo "40.7128,-74.0060"  # New York
agent-browser set headers '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}'
```

### 2. JavaScript Execution Simulation

```bash
# Wait for JavaScript to execute
agent-browser wait --load networkidle
agent-browser eval "window.acw_sc__v2 = 'bypass_token'"
```

### 3. Human-like Behavior

```bash
# Simulate human scrolling
agent-browser scroll down 300
agent-browser wait 2000
agent-browser scroll down 500
agent-browser wait 1500
```

### 4. Cookie Handling

```bash
# Extract and replay cookies
agent-browser cookies > cookies.json
agent-browser cookies set acw_sc__v2 "your_token"
```

## Anti-Detection Strategies

### 1. Timing Randomization

```bash
# Add random delays between actions
agent-browser wait $((1000 + RANDOM % 3000))
```

### 2. Mouse Movement

```bash
# Simulate natural mouse movements
agent-browser mouse move 100 200
agent-browser wait 500
agent-browser mouse move 150 250
```

### 3. Request Headers

```bash
# Set realistic headers
agent-browser set headers '{
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.9",
  "Accept-Encoding": "gzip, deflate, br",
  "Connection": "keep-alive",
  "Upgrade-Insecure-Requests": "1"
}'
```

## Download Workflow

### Step 1: Initial Access

```bash
# Navigate to target page
agent-browser open "https://www.1ppt.com/article/76644.html"
agent-browser wait --load networkidle
```

### Step 2: Bypass WAF

```bash
# Wait for WAF JavaScript execution
agent-browser wait 3000
agent-browser eval "
  // Override WAF detection
  Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
  });
  // Set required cookies
  document.cookie = 'acw_sc__v2=bypass; path=/';
"
```

### Step 3: Extract Download Links

```bash
# Get download button
agent-browser snapshot -i
# Look for download links in page source
agent-browser eval "
  const downloadLinks = Array.from(document.querySelectorAll('a[href*=\"download\"]'))
    .map(a => a.href);
  downloadLinks.forEach(link => console.log(link));
"
```

### Step 4: Execute Download

```bash
# Click download button
agent-browser click @download_button
agent-browser wait 2000
```

## Advanced Techniques

### Headless vs Headed

```bash
# Use headed mode to bypass headless detection
agent-browser open https://example.com --headed
```

### CDP (Chrome DevTools Protocol)

```bash
# Connect via CDP for advanced control
agent-browser --cdp 9222 snapshot
```

### Session Persistence

```bash
# Save session state
agent-browser state save session.json
# Load session later
agent-browser state load session.json
```

## Troubleshooting

### Common WAF Challenges

1. **JavaScript Challenges**
   - Solution: Use headed mode or evaluate JS

2. **Cookie Requirements**
   - Solution: Extract cookies from browser session

3. **Timing Issues**
   - Solution: Add explicit waits for JS execution

4. **User-Agent Detection**
   - Solution: Set realistic User-Agent strings

### Debug Mode

```bash
# Enable verbose logging
agent-browser --debug open https://example.com
# View console messages
agent-browser console
# Check for errors
agent-browser errors
```

## Ethical Usage

⚠️ **Important**: Only use these techniques for:
- Educational purposes
- Legitimate content access
- Personal use with permission
- Testing your own systems

Do not use for:
- Scraping protected content without permission
- Bypassing paywalls or access controls
- DDOS or attacks
- Commercial exploitation

## Examples

### Download from Protected PPT Site

```bash
# Navigate to page
agent-browser open "https://www.1ppt.com/article/76644.html"
agent-browser wait --load networkidle

# Bypass WAF
agent-browser eval "
  Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
  window.scrollTo(0, document.body.scrollHeight);
"
agent-browser wait 2000

# Find and click download
agent-browser snapshot -i
agent-browser click @download_link
agent-browser wait 3000
```

### Handle Cloudflare Protection

```bash
# Wait for challenge
agent-browser wait --text "Checking your browser"
agent-browser wait --text "Access granted"
agent-browser wait 5000
```

## Resources

- Playwright Docs: https://playwright.dev/
- Puppeteer Docs: https://pptr.dev/
- Anti-Detection Techniques: https://bot.sannysoft.com/

## Limitations

- Some WAFs require CAPTCHA solving (not automated)
- Advanced behavioral analysis may still detect automation
- Legal and ethical considerations apply
- May violate Terms of Service on some sites
