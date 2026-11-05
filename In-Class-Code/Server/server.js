import express from "express";

let server = express();
let location = {};

server.use(express.json());

server.get("/", (req, res) => {
    console.log("Request received!");
    res.send("Hello World!");
});

server.get("/about", (req, res) => {
    console.log("Request received from about page");
    res.send("About Page");
});

server.get("/api/read_gps", (req, res) => {
    res.json(location);
});

server.post("/api/write_gps", (req, res) => {
    location = req.body;

    console.log("Location received:", location);

    res.send("Location successfully received!");
});


server.listen(3000);