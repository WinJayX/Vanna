# Vanna 系统Docker启动脚本



## 参考链接：

- https://vanna.ai/docs/base/
- https://blog.csdn.net/weixin_58107261/article/details/148080936
- https://blog.csdn.net/Asta__/article/details/148169063



## 停止服务

> `docker-compose down -v`

![image-20250612163730878](https://img.winjay.cn/md/image-20250612163730878.webp)



## 启动服务

> `docker-compose up -d --build`

![image-20250612163803314](https://img.winjay.cn/md/image-20250612163803314.webp)



## 目录结构

```bash
root@lit:/mnt/Vanna# tree .
.
├── chroma_data
├── docker-compose.yaml
├── vanna
│   ├── app.py
│   ├── app-v1.py
│   ├── Dockerfile
│   ├── Qwen
│   │   ├── app.py
│   │   └── app.py-Origin
│   └── requirements.txt
└── vanna_cache
    └── chroma
        └── onnx_models
            └── all-MiniLM-L6-v2
                ├── onnx
                │   └── model.onnx
                └── onnx.tar.gz

9 directories, 9 files
```



## 系统截图

![image-20250612164037307](https://img.winjay.cn/md/image-20250612164037307.webp)

![image-20250612164108041](https://img.winjay.cn/md/image-20250612164108041.webp)





## 生产环境建议

#### 1. 安全加固

```yaml
# 在 compose 文件中添加
environment:
  - AUTH_ENABLED=true
  - JWT_SECRET=your_jwt_secret
```

#### 2. HTTPS 配置

- 使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl;
    server_name vanna.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
    }
}
```


