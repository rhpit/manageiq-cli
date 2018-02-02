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

page.onConsoleMessage = function(msg) {
  system.stderr.writeLine('console: ' + msg);
};

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

// go to the configuration page
setTimeout(function() {
  console.log("");
  console.log("### STEP 3: Load 'https://localhost:8443/ops/explorer'");
  page.open("https://localhost:8443/ops/explorer");
}, 15000);

// change settings
setTimeout(function() {
  console.log("");
  console.log("### STEP 4: Click server_role_git_owner switch");
  
  // We want server roles git owner to be swtiched on.
  var switch_value = page.evaluate(function() {
    return $("input[name='server_roles_git_owner']").bootstrapSwitch('state');
  });
  if (switch_value == false) {
    console.log("    Git owner switch is OFF. Setting to ON.")
    page.evaluate(function() {
      $("input[name='server_roles_git_owner']").bootstrapSwitch('toggleState');
    });
  } else {
    console.log("    Git owner switch is ON. Nothing to do.")
  }

  // we can set more stuff here later...

}, 20000);

// save the changes. If nothing changes, it won't hurt clicking on save anyway
setTimeout(function() {
  console.log("");
  console.log("### STEP 5: Save configuration changes");
  page.evaluate(function() {
    $('button[alt="Save Changes"]').click();
  });
}, 20000);

// done
setTimeout(function() {
  console.log("");
  console.log("### STEP 6: Close page and shutdown");
  page.close();
  setTimeout(function(){
      phantom.exit();
  }, 100);
}, 28000);