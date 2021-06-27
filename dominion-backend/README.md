The code in this folder is deployed in the heroku app Dominion-server. To deploy, add the app to the remote and rename it:
```
heroku login -i
heroku git:remote --app dominion-server
git remote rename heroku heroku-server
```
Then you just have to go the root of the repo and use the following command to deploy:
```
git subtree push --prefix dominion-backend heroku-server master
```