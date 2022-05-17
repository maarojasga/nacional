mkdir -p ~/.streamlit/
echo "[general]
email = \"diana.jimenez@xpecta.co\"
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
[theme]\n\
primaryColor='#028f42'\n\
backgroundColor='#000000'\n\
secondaryBackgroundColor='#00272d'\n\
textColor='#fafafa'\n\
font='sans serif'\n\
" > ~/.streamlit/config.toml
