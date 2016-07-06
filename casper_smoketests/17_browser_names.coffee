phantom.clearCookies()

casper.userAgent('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
casper.start 'http://localhost:8000', ->
   @.then ->
    @.test.assertHttpStatus 200
   @.viewport(1200, 1200)   
   @.then ->
    @.fill("form[name='loginform']", {
     "username": "test_valid",
     "password": "testpassword"
    }, true);
    @.wait(250)
   @.then ->
    @.clickLabel("Authenticate with SMS")
   @.then ->
    @.fill("form[name='loginform']", {
     "otp": "12345"
    }, true);
    @.wait(250)
   @.then ->
    @.capture("screenshots_browser_name.png")
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/name_your_browser?_sso=internal&_sc=on&next=/index", "Asking for browser name"
   @.then ->
    @.fill("form[name='loginform']", {
    })
    @.clickLabel("Skip this time")
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/index", "Redirected to front page (skip)"

   @.then ->
    phantom.clearCookies()
   @.thenOpen("http://localhost:8000")
   @.then ->
    @.test.assertUrlMatch 'http://localhost:8000/first/password?_sso=internal&next=/index', "Redirected to password authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "username": "test_valid",
     "password": "testpassword"
    }, true)
    @.wait(250)
   @.then ->
    @.clickLabel("Authenticate with SMS")
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch 'http://localhost:8000/second/sms?_sso=internal&next=/index', "Redirected to SMS authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "otp": "12345"
    }, true)
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/name_your_browser?_sso=internal&_sc=on&next=/index", "Asking for browser name"
   @.then ->
    @.fill("form[name='loginform']", {
    })
    @.clickLabel("Save and continue")
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/index", "Redirected to front page after entering empty name"

   @.then ->
    phantom.clearCookies()
   @.thenOpen("http://localhost:8000")
   @.then ->
    @.test.assertUrlMatch 'http://localhost:8000/first/password?_sso=internal&next=/index', "Redirected to password authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "username": "test_valid",
     "password": "testpassword"
    }, true)
    @.wait(250)
   @.then ->
    @.clickLabel("Authenticate with SMS")
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch 'http://localhost:8000/second/sms?_sso=internal&next=/index', "Redirected to SMS authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "otp": "12345"
    }, true)
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/name_your_browser?_sso=internal&_sc=on&next=/index", "Asking for browser name"
   @.then ->
    @.fill("form[name='loginform']", {
     "name": "testname"
    })
    @.clickLabel("Save and continue")
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/index", "Redirected to front page after saving the name"
   @.then ->
    @.clickLabel("Sign out")
   @.thenOpen("http://localhost:8000")
   @.then ->
    @.test.assertUrlMatch 'http://localhost:8000/first/password?_sso=internal&next=/index', "Redirected to password authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "username": "test_valid",
     "password": "testpassword"
    }, true)
    @.wait(250)
   @.then ->
    @.clickLabel("Authenticate with SMS")
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch 'http://localhost:8000/second/sms?_sso=internal&next=/index', "Redirected to SMS authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "otp": "12345"
    }, true)
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/index", "Redirected to front page, as browser was already saved"
   @.thenOpen("http://localhost:8000/sessions")
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertSelectorHasText "a", "testname"
   @.then -> 
    @.clickLabel "Sign out"
   @.thenOpen("http://localhost:8000")
   @.then ->
    @.test.assertUrlMatch 'http://localhost:8000/first/password?_sso=internal&next=/index', "Redirected to password authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "username": "test_admin",
     "password": "testpassword"
    }, true)
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch 'http://localhost:8000/second/sms?_sso=internal&next=/index', "Redirected to SMS authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "otp": "12345"
    }, true)
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/configure?_sso=internal&next=/index", "Configuration view (admin)"
   @.thenOpen("http://localhost:8000/sessions")
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertSelectorHasText "button", "Name this browser"
   @.then ->
    @.clickLabel("Sign out")
   @.thenOpen("http://localhost:8000")
   @.then ->
    @.fill("form[name='loginform']", {
     "username": "test_valid",
     "password": "testpassword"
    }, true);
    @.wait(250)
   @.then ->
    @.clickLabel("Authenticate with SMS")
   @.then ->
    @.test.assertUrlMatch 'http://localhost:8000/second/sms?_sso=internal&next=/index', "Redirected to SMS authentication"
   @.then ->
    @.fill("form[name='loginform']", {
     "otp": "12345"
    }, true);
    @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200
    @.test.assertUrlMatch "http://localhost:8000/index", "Redirected to front page (test_valid)"


casper.run ->
  @.test.done()
