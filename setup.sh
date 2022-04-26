mkdir -p ~/.streamlit/
echo "[general]
email = \"diana.jimenez@xpecta.co\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
[theme]
primaryColor='#028f42'
backgroundColor='#000000'
secondaryBackgroundColor='#00272d'
textColor='#fafafa'
font='sans serif'
" > ~/.streamlit/config.toml
