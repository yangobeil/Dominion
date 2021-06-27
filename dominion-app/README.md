The code in this folder is deployed in the heroku app Dominion-frontend. To deploy, add the app to the remote and rename it:
```
heroku login -i
heroku git:remote --app dominion-frontend
git remote rename heroku heroku-frontend
```
Then you just have to go the root of the repo and use the following command to deploy:
```
git subtree push --prefix dominion-app heroku-frontend master
```

Details about how to deploy: https://medium.com/netscape/deploying-a-vue-js-2-x-app-to-heroku-in-5-steps-tutorial-a69845ace489

Project setup
```
npm install
```

Compiles and hot-reloads for development
```
npm run serve
```

Compiles and minifies for production
```
npm run build
```

