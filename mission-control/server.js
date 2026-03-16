/**
 * Custom Next.js server with WebSocket proxy for gateway connections.
 *
 * When Mission Control is accessed through a reverse proxy or tunnel (e.g. ngrok)
 * that only forwards a single port, the browser cannot directly reach the local
 * OpenClaw gateway on its separate port. This server proxies WebSocket connections
 * on the /gw path to the local gateway, so all traffic goes through one port.
 *
 * Usage:
 *   node server.js          # production
 *   node server.js --dev    # development (replaces `next dev`)
 */
const { createServer } = require('http')
const net = require('net')
const { parse } = require('url')
const next = require('next')

const dev = process.argv.includes('--dev')
const hostname = process.env.HOSTNAME || (dev ? '127.0.0.1' : '0.0.0.0')
const port = parseInt(process.env.PORT || '3000', 10)
const gatewayHost = process.env.OPENCLAW_GATEWAY_HOST || '127.0.0.1'
const gatewayPort = parseInt(process.env.OPENCLAW_GATEWAY_PORT || '18789', 10)

const app = next({ dev, hostname, port })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  const server = createServer(async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true)
      await handle(req, res, parsedUrl)
    } catch (err) {
      console.error('Error handling request:', err)
      res.statusCode = 500
      res.end('Internal Server Error')
    }
  })

  // WebSocket proxy: forward /gw upgrade requests to the local gateway
  server.on('upgrade', (req, socket, head) => {
    const { pathname } = parse(req.url || '', true)

    if (pathname === '/gw') {
      const proxySocket = net.connect(gatewayPort, gatewayHost, () => {
        // Rebuild the HTTP upgrade request for the gateway
        const headers = []
        headers.push(`GET / HTTP/1.1`)
        headers.push(`Host: ${gatewayHost}:${gatewayPort}`)

        // Forward all original headers except Host
        const rawHeaders = req.rawHeaders || []
        for (let i = 0; i < rawHeaders.length; i += 2) {
          const key = rawHeaders[i]
          const val = rawHeaders[i + 1]
          if (key.toLowerCase() === 'host') continue
          headers.push(`${key}: ${val}`)
        }

        proxySocket.write(headers.join('\r\n') + '\r\n\r\n')
        if (head.length > 0) proxySocket.write(head)

        // Bi-directional pipe
        proxySocket.pipe(socket)
        socket.pipe(proxySocket)
      })

      proxySocket.on('error', (err) => {
        console.error('[gw-proxy] Gateway connection failed:', err.message)
        socket.end()
      })

      socket.on('error', (err) => {
        if (err.code !== 'ECONNRESET') {
          console.error('[gw-proxy] Client socket error:', err.message)
        }
        proxySocket.end()
      })

      return
    }

    // Let Next.js handle other upgrade requests (HMR, etc.)
    // In dev mode, Next.js internally handles its own WebSocket upgrades
  })

  server.listen(port, hostname, () => {
    console.log(`> Mission Control ready on http://${hostname}:${port}`)
    console.log(`> Gateway proxy: /gw -> ${gatewayHost}:${gatewayPort}`)
    if (dev) console.log(`> Mode: development`)
  })
})
