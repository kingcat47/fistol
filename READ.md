# Interpark Ticket Auto-Booking Bot

This project is a **Python + Selenium automation script** for logging into **Yanolja & Interpark Ticket** and booking tickets automatically.  
It supports **captcha recognition (OCR)** and seat selection.

---

## Features

1. **Yanolja Login (Kakao Account)**
   - Clicks Kakao login button and handles authentication in a new tab
   - Automatically switches back to the main tab after login

2. **Interpark Ticket Login**
   - Clicks the login button and handles account authentication

3. **Ticket Booking Page Navigation & Date Selection**
   - Selects the desired year, month, and day
   - Automatically closes the booking popup

4. **Captcha Automation (OCR)**
   - Detects captcha images inside iframes
   - Sends images to a backend OCR server for recognition
   - Automatically inputs and submits the captcha text

5. **Seat Selection Automation**
   - Specify layer, row, and seat number
   - Clicks image map (`area`) and selects the seat

---

## Installation

1. **Install Python 3.10 or above**

2. **Install required libraries**
```bash
pip install undetected-chromedriver selenium selenium-stealth requests easyocr google-cloud-vision
