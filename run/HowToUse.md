# Interpark Ticket Booking Macro User Guide

This file explains how to use the program.

## 1. Download Executable File
First, download the `Interpark_Debug_v2.exe` executable file.

## 2. Run the Executable and Enter Required Information
When you run the executable, you will be prompted to enter the following information:

- **Kakao Email**
- **Kakao Password**  
- **Performance UUID**
- **Target Month**
- **Target Day**

Each variable meaning:
- **KAKAO_EMAIL**: KakaoTalk login email   
- **KAKAO_PASSWORD**: KakaoTalk login password  
- **PERFORMANCE_UUID**: Unique ID of the performance to book
- **TARGET_MONTH**: Month to book (1-12)
- **TARGET_DAY**: Day to book (1-31)

### 2-1. If you don't have a KakaoTalk account
Create a KakaoTalk account at the link below. (It's a famous Korean service company, so don't worry.)
https://accounts.kakao.com/weblogin/create_account/?continue=https%3A%2F%2Faccounts.kakao.com%2Fweblogin%2Faccount&lang=ko&showHeader=false#selectVerifyMethod

![Kakao Login Screen](images/kakao_signup.png)

### 2-2. How to find Performance UUID
You can find the performance UUID on the ticketing website. First, go to the link below and select the performance you want. Then check the numbers at the end of the address bar.
https://nol.interpark.com/ticket

![Interpark Main Screen](images/example_1.png)
![Interpark Performance Booking Page](images/example_2.png)
![UUID](images/performance_uuid.png)

## 3. Captcha Handling
When the month and date are properly selected and the ticket purchase detail popup appears, the captcha will be checked.
Here, the macro cannot automatically detect the captcha input, so the user needs to click the captcha input field once.

## 4. Seat Selection
Seat selection functionality has been excluded because it may not work depending on the computer environment. 
After captcha resolution, the browser will remain open so you can manually select seats.
