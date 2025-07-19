```bash
git clone https://github.com/bugrakaann/instacomment
docker build -t instagram_comment_bot .
docker run -d --name <CONTAINERNAME> -v /usr/local/instacomment/sessionlast2.json:/app/sessionlast2.json -e COOKIE_FILE=sessionlast2.json -e PROXY_URL=<PROXYURL> instabot

```
