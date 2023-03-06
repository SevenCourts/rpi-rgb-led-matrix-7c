@echo off
SET TIMEOUT_SECONDS=2

:::: 7c-m1-r1
:: SET HURL_7c_target_panel=N0MtTTEtUjE=
:: SET HURL_tableau_server_url=<YOUR_TABLEAU_SERVER_URL>

:::: shinych's thinkstation1 (old)
:: SET HURL_7c_target_panel=dGhpbmtzdGF0aW9uMQ==
:: SET HURL_tableau_server_url=http://192.168.114.30:5000

for %%i in (*.hurl) do (
    echo %%i
    hurl %%i
    timeout %TIMEOUT_SECONDS%
)