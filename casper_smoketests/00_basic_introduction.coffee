phantom.clearCookies()

casper.start 'http://localhost:8000/', ->
   @.viewport(1200, 1200)
   @.viewport(1200, 1200);
   @.thenClick "#introduction_link"
   @.then ->
    @.capture("screenshots_introduction.png")
    @.test.assertUrlMatch 'http://localhost:8000/introduction', "URL matches to basic instructions"
    @.test.assertHttpStatus 200
   @.then ->
    @.clickLabel "separate instructions page for developers"
   @.then ->
    @.capture("screenshots_developer_introduction.png")
    @.test.assertUrlMatch 'http://localhost:8000/developer_introduction', "URL matches to developer instructions"
    @.test.assertHttpStatus 200

casper.run ->
  @.test.done()
