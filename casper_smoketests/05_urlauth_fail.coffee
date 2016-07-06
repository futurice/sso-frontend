phantom.clearCookies()

casper.userAgent('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
casper.start 'http://localhost:8000/urlauth/asdf', ->
   @.test.assertHttpStatus 200
   @.then ->
    @.capture("screenshots_urlauth_invalid.png")
    @.test.assertSelectorHasText(".alert-danger", "Invalid request. Did you open this page on the same browser you started the authentication process", "Wrong browser warning")
   @.thenOpen("http://localhost:8000")
   @.then ->
    @.fill("form", {
     "username": "test_valid",
     "password": "testpassword"
    }, true)
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
   @.thenOpen("http://localhost:8000/urlauth/asdf")
   @.then ->
    @.capture("screenshots_urlauth_expired.png")
    @.test.assertSelectorHasText(".alert-danger", "Unique code for this URL expired already.", "Code expiration warning")

casper.run ->
  @.test.done()
