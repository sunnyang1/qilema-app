import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
const port = process.env.PORT || 5000;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// Health check
app.get('/api/v1/health', (req, res) => {
  res.status(200).json({ 
    status: 'ok',
    message: '起了吗 App 前端服务器运行正常'
  });
});

// Serve static files from client (Expo web build)
// 注意：这需要先构建 Expo web 版本
const clientDistPath = path.join(__dirname, '../../client');
app.use(express.static(clientDistPath));

// SPA fallback - for Expo Router
app.get('*', (req, res) => {
  res.sendFile(path.join(clientDistPath, 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`起了吗 App 前端服务器运行在 http://0.0.0.0:${port}/`);
  console.log(`健康检查: http://localhost:${port}/api/v1/health`);
});
