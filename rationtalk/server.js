// server.js
import express from "express";
import cors from "cors";
import fetch from "node-fetch";

const app = express();
// Change this if you want a different port:
const PORT = process.env.PORT || 4000;

// 1) Enable CORS so that your React app (e.g. http://localhost:3000) can request images
app.use(
  cors({
    origin: "http://localhost:3000", // <-- adjust if your React runs somewhere else
  })
);

// 2) The proxy endpoint:
//    GET /api/proxy-image?url=<encoded-Google-News-URL>
app.get("/api/proxy-image", async (req, res) => {
  const { url } = req.query;
  // a) Validate that a URL was provided
  if (!url || typeof url !== "string") {
    return res.status(400).send("Missing or invalid 'url' parameter");
  }

  try {
    // b) Fetch the Google News image server-side, sending a Referer so Google lets us through:
    const response = await fetch(url, {
      headers: {
        Referer: "https://news.google.com/",
      },
    });

    // c) If Google News returns an error (403/404), forward it:
    if (!response.ok) {
      return res
        .status(response.status)
        .send(`Failed to fetch image: ${response.statusText}`);
    }

    // d) Grab the image’s Content-Type (e.g. "image/jpeg")
    const contentType = response.headers.get("content-type") || "application/octet-stream";
    res.setHeader("Content-Type", contentType);

    // e) Stream the image bytes directly to the browser:
    response.body.pipe(res);
  } catch (err) {
    console.error("Error in proxy:", err);
    res.status(500).send("Server error while proxying image");
  }
});

// (Optional) If you later want to serve your React build from the same server, add:
// app.use(express.static("build"));
// app.get("*", (req, res) => res.sendFile(path.resolve(__dirname, "build", "index.html")));

app.listen(PORT, () => {
  console.log(`Proxy server listening on http://localhost:${PORT}`);
});
