## RTC set-up (w-i-p)

[Guide](https://microdigisoft.com/interfacing-rtc-ds1307-module-with-raspberry-pi-using-python/)
[RTC DS1307 open source library from SwitchdocLABS](https://codeload.github.com/switchdoclabs/RTC_SDL_DS1307/zip/master)

```
sudo apt-get install i2c-tools
i2cdetect -y 1
sudo apt install python3-smbus

python3 test.py
```