import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.png':'image/png','.svg':'image/svg+xml','.md':'text/plain; charset=utf-8'};
const server = http.createServer((req,res)=>{
  try {
    const pathname = decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const target = path.resolve(root,'.'+pathname+(pathname.endsWith('/')?'index.html':''));
    if (!target.startsWith(root+path.sep)) {res.writeHead(403);res.end();return;}
    if (!fs.existsSync(target)||!fs.statSync(target).isFile()) {res.writeHead(404);res.end('Not found');return;}
    res.writeHead(200,{'Content-Type':types[path.extname(target)]||'application/octet-stream'});
    fs.createReadStream(target).pipe(res);
  } catch {res.writeHead(400);res.end('Bad request');}
});
server.listen(4177,'127.0.0.1',()=>console.log('Local: http://127.0.0.1:4177'));
