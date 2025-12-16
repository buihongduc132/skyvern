import { createServer } from "http";
import handler from "serve-handler";
import open from "open";

const port = Number(process.env.SKYVERN_UI_PORT || 28742);
const host = process.env.SKYVERN_UI_HOST || "0.0.0.0";
const publicHost = process.env.SKYVERN_UI_PUBLIC_HOST || "localhost";
const url = `http://${publicHost}:${port}`;

const server = createServer((request, response) => {
  // You pass two more arguments for config and middleware
  // More details here: https://github.com/vercel/serve-handler#options
  return handler(request, response, {
    public: "dist",
    rewrites: [
      {
        source: "**",
        destination: "/index.html",
      },
    ],
  });
});

server.listen(port, host, async () => {
  console.log(`Running at ${url}`);
  if (process.env.SKYVERN_OPEN_BROWSER === "1") {
    await open(url);
  }
});
