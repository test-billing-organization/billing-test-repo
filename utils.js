const express = require("express");
const path = require("path");
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

// Path traversal protection
app.get("/file", (req, res) => {
  const filename = req.query.name;
  if (!filename) {
    return res.status(400).send("Missing filename");
  }
  const baseDir = "/var/data";
  const resolvedPath = path.resolve(baseDir, filename);
  if (!resolvedPath.startsWith(baseDir + path.sep)) {
    return res.status(403).send("Access denied");
  }
  res.sendFile(resolvedPath);
});

module.exports = { merge, validateEmail };
