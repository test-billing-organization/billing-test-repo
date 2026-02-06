const express = require("express");
const app = express();

// XSS via innerHTML
app.get("/profile", (req, res) => {
  const username = req.query.username;
  res.send(`<div id="profile">${username}</div>`);
});

// Prototype pollution
function merge(target, source) {
  for (const key in source) {
    if (typeof source[key] === "object") {
      target[key] = merge(target[key] || {}, source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

// Regex DoS
function validateEmail(email) {
  const re = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
  return re.test(email);
}

// Path traversal
app.get("/file", (req, res) => {
  const filename = req.query.name;
  res.sendFile("/var/data/" + filename);
});

// Currency conversion helper
function convertCurrency(amount, exchangeRate) {
  return Math.floor(amount * exchangeRate * 100) / 100;
}

module.exports = { merge, validateEmail, convertCurrency };
