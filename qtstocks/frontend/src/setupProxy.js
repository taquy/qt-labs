const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5555',
      changeOrigin: true,
      secure: false,
      ws: true,
    })
  );
}; 