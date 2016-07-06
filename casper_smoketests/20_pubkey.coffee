phantom.clearCookies()

casper.start 'http://localhost:8000/', ->
   @.download "http://localhost:8000/download/pubkey/pubtkt", "pubtkt-key"
   @.then ->
    @.test.assertHttpStatus 200, "Download pubtkt key"

   @.download "http://localhost:8000/download/pubkey/saml", "saml-key"
   @.wait(250)
   @.then ->
    @.test.assertHttpStatus 200, "Download SAML key"
casper.run ->
  @.test.done()
