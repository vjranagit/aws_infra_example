const http = require('http')
const port = 80

// HTML Template

const htmlTemplateCreate = `<!DOCTYPE html>
<html>
<head>
  <title>Hellow World</title>
</head>
<body>
  <div>
    <h2>Hellow World</h2>
  </div>
</body>
</html>`

// Server

const server = http.createServer((req, res) => {
  console.log('request: ' + req)
  res.writeHead(200, { 'Content-Type': 'text/html' })
  res.write(htmlTemplateCreate)
  res.end()
})

server.listen(port)
console.log('Server running at http://localhost:' + port + '/')

