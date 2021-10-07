# BriansSpareTime blog

An experiment in learning NuxtJS and also in trying to document some of the stuff I do.

See the deployed site here: http://www.brianssparetime.com

Copyright reserved on all photos, videos, prose, and other non-code content included in this repository; no reproduction of such content without written consent in advance.


## The Plan / TODO:
 - [fix] investigate eliminating dirp thing again.
 - [FEATURE] pagination of all posts

 - [FIX, WIP] abstract post list into a vue component
   - use this on main page, all posts
   - consider adding filter / sort functionality there and using it with topic pages

 - [FEATURE] set up search
    - https://nuxtjs.org/blog/creating-blog-with-nuxt-content/#add-a-search-field
 - [EVENTUALLY] password protected photos section
 - [EVENTUALLY] eliminate more redundant data (date, title maybe) by parsing file structure
   - https://content.nuxtjs.org/advanced#hooks
 - [EVENTUALLY] considering using git submodule to contain /content or use netlify LargeMedia
   - https://docs.netlify.com/large-media/overview/
   - https://mayashavin.com/articles/git-submodule-nuxt
 - [EVENTUALLY] move to configuration via build file 
   - https://docs.netlify.com/configure-builds/file-based-configuration/
   - https://serverless-stack.com/chapters/create-a-netlify-build-script.html
 - [EVENTUALLY] speed up deploy
   - https://serverless-stack.com/chapters/create-a-netlify-build-script.html
  - also consider making the side bar more like this guy's
    - https://derkinzi.de/optimized-responsive-lazyloading-images-with-nuxt/



 ## Accomplished:
 - support for automatically generating thumbnails for images, as part of deploy, and serving those instead of full size where it makes sense.
 - added og:image support for proper thumbnails in shares
 - interest pages also built using md files in separate content directory
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


#### built with significant help from:
https://github.com/regenrek/nuxt-blog-frontmatter-markdown-loader 
https://regenrek.com/posts/create-a-frontmatter-markdown-powered-blog-with-nuxt.js/
https://github.com/regenrek/vue-sidebar-menu-example/tree/master/src
https://regenrek.com/posts/how-to-create-an-animated-vue-sidebar-menu-with-vue-observable/
https://github.com/nuxt/content/issues/106
https://nuxtjs.org/blog/creating-blog-with-nuxt-content/#displaying-your-content
https://medium.com/@wearethreebears/handle-api-driven-content-links-in-nuxt-js-fe2e31ecbeeb
