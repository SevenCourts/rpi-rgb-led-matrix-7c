mkdir .runtime
SET PANEL_CONFIG=.runtime/panel.config

SET USE_RGB_MATRIX_EMULATOR=True
SET TABLEAU_SERVER_BASE_URL=http://127.0.0.1:5005
:: SET TABLEAU_SERVER_BASE_URL=https://staging.server.sevencourts.com

SET TABLEAU_DEBUG=True

m1.bat %*
