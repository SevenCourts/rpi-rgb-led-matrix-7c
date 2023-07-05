## RTC DS1307 set-up

### Links

- [Guide](https://microdigisoft.com/interfacing-rtc-ds1307-module-with-raspberry-pi-using-python/)
- [RTC DS1307 open source library from SwitchdocLABS](https://codeload.github.com/switchdoclabs/RTC_SDL_DS1307/zip/master)


### Detect RTC on i2c

```
sudo apt-get install i2c-tools
i2cdetect -y 1
```
Should be `0x68`


### Run script

```
python3 test.py
```