import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { PrismaClient } from "@prisma/client";
import multer from "multer";

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "../api");
  },
  filename: (req, file, cb) => {
    cb(null, "pdf-file.pdf");
  },
});

const upload = multer({ storage: storage });

const app = express();
dotenv.config();
const prisma = new PrismaClient();

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post("/upload", upload.single("file"), function (req, res) {
  res.json({});
});

app.get("/item", async (req, res) => {
  const items = await prisma.item.findMany();
  res.json(items);
});

if (import.meta.env.PROD) app.listen(3000);

export const viteExpressApp = app;
