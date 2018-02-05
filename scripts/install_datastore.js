"use strict";
var sys = require("system"),
    page = require("webpage").create(),
    MIQ_URL = "https://localhost:8443/";

// page settings
page.viewportSize = { width: 1920, height: 1080 };
page.settings.userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36';
page.settings.javascriptEnabled = true;

// phantomjs settings
phantom.cookiesEnabled = true;
phantom.javascriptEnabled = true;

// load login page
setTimeout(function() {
  console.log("");
  console.log("### STEP 1: Load '" + MIQ_URL + "'");
  page.open(MIQ_URL);
}, 5000);

// input credentials
setTimeout(function() {
  console.log("");
  console.log("### STEP 2: Login into the ManageIQ instance");
  page.evaluate(function() {
    document.querySelector("input[name='user_name']").value = "admin";
    document.querySelector("input[name='user_password']").value = "smartvm";
    $("#login").click();
  });
}, 10000);

// go to the import/export automation page
setTimeout(function() {
  console.log("");
  console.log("### STEP 3: Load 'https://localhost:8443/miq_ae_tools/import_export'");
  page.open("https://localhost:8443/miq_ae_tools/import_export");
}, 15000);

// fill in the ManageIQ_CLI github project address and submit
setTimeout(function() {
  console.log("");
  console.log("### STEP 4: Fill in manageiq_cli repository");
  page.evaluate(function() {
    document.querySelector("input[name='git_url']").value = "https://github.com/rhpit/manageiq-cli.git";
    $("#git-url-import").click();
  });
}, 20000);

// select default options for the github project branch
setTimeout(function() {
  console.log("");
  console.log("### STEP 5: Submit branch (default for master)");
  page.evaluate(function() {
    $(".git-import-submit").click();
  });
}, 35000);

// done
setTimeout(function() {
  console.log("");
  console.log("### STEP 6: Close page and shutdown");
  page.close();
  setTimeout(function(){
      phantom.exit();
  }, 100);
}, 42000);