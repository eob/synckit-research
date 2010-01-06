The pages

- blog.php
- blog-flying.php
- wiki.php
- wiki-flying.php

Are the files to be maintained for the blog and wiki tests. These contain the
test code and links to include the synckit files. When you are ready to test, 
just run:

php blog.php > blog.html

Or the equivalent for each file. The resulting HTML file is the one that should
be used during testing.  

blog-traditional.html
======================

I can't remember what this file is trying to test. It is loaded out of the static directory, so it shouldn't really be a test
for a "traditional" blog, which should have dynamic behavior on the server-side. 

Maybe we were using this file to "pretend" to download the template in some of our batch tests. Then for future requests we would just hit the data endpoint.

Delete this file?

test_dom_load.html
==================

