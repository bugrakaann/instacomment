git clone https://github.com/bugrakaann/instacomment
docker build -t instagram_comment_bot
docker run -d --name <CONTAINERNAME> -e USERNAME=<USERNAME> -e PASSWORD=<PASSWORD> instagram_comment_bot
