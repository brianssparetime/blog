# nuxtblog

derived from https://github.com/regenrek/nuxt-blog-frontmatter-markdown-loader and https://regenrek.com/posts/create-a-frontmatter-markdown-powered-blog-with-nuxt.js/


## installation:

1) Download and install yarn from 
https://classic.yarnpkg.com/en/docs/install/
or with 

```curl -o- -L https://yarnpkg.com/install.sh | bash```

2) `yarn install`

3) clone repo

4) `yarn dev`

## The Plan:

 - want each posts bundled with images and other static content in a folder per post
 - want list of main topics of interest in a left side nav bar (e.g. vintage computers, brewing, photog, BGF, EE...)
 - want tagging of posts
    - perhaps use some subset of tags as main topics?  Or have a static page per topic, with a list of tagged posts?
    - inference of additional tags?
    - search by tag in sidebar
 - search by date in sidebar (or possibly at bottom of main page)
 



## old readme


### Build Setup

``` bash
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

For detailed explanation on how things work, checkout [Nuxt.js docs](https://nuxtjs.org).
