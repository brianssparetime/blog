# BriansSpareTime blog

An experiment in learning NuxtJS and also in trying to document some of the stuff I do.

See the deployed site here: http://www.brianssparetime.com


## The Plan / TODO:
 - main interest static pages
 - [FEATURE] add other interest pages
 - [FEATURE] figure out how to auto generate thumbnails or handle different image sizes
  - https://stackoverflow.com/questions/48606325/how-to-resize-images-for-different-responsive-views
 - [FIX] still can't figure out wrong border sizing on postcard vimgpc
 - [FEATURE] eliminate redundant data (date, dirp, title maybe) by parsing file structure
   - https://content.nuxtjs.org/advanced#hooks
 - [FIX] abstract post list into a vue component
   - use this on main page, all posts
   - consider adding filter / sort functionality there and using it with topic pages
 - [FIX] fix ugly css everywhere
 - [FEATURE] set up search
 - [EVENTUALLY] pagination of all posts
 - [EVENTUALLY] password protected photos section

 ## Accomplished:
 - images link to full size image provided by API
 - interest pages that show only posts related to certain tags
 - multiple images in a markdown post
 - sidebar nav that toggles open and closed
 - embedding YT videos in markdown posts
 - use postcard at top of post
 - make images in posts show up with correct border size and aspect ratio
 - added ignore-loader to suppress webpack warnings 
 - limit size of images in posts
 - eliminated need for img folder within each post
 - deploy site to netlify
 - make debug work in VSCode





### Build Setup
## installation:

Download and install yarn from 
https://classic.yarnpkg.com/en/docs/install/
or with 


``` bash

# install yarn
curl -o- -L https://yarnpkg.com/install.sh | bash

# install dependencies
$ yarn install

# serve with hot reload at localhost:3000
$ yarn run dev

# build for production and launch server
$ yarn run build
$ yarn start

# generate static project
$ yarn run generate
```


### built with significant help from:
https://github.com/regenrek/nuxt-blog-frontmatter-markdown-loader 
https://regenrek.com/posts/create-a-frontmatter-markdown-powered-blog-with-nuxt.js/
https://github.com/regenrek/vue-sidebar-menu-example/tree/master/src
https://regenrek.com/posts/how-to-create-an-animated-vue-sidebar-menu-with-vue-observable/
https://github.com/nuxt/content/issues/106
https://nuxtjs.org/blog/creating-blog-with-nuxt-content/#displaying-your-content
https://medium.com/@wearethreebears/handle-api-driven-content-links-in-nuxt-js-fe2e31ecbeeb