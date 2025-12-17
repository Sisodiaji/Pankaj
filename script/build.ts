import { build } from "esbuild";
import { mkdirSync } from "fs";

mkdirSync("dist", { recursive: true });

build({
  entryPoints: ["server/index.ts"],
  outfile: "dist/index.cjs",
  bundle: true,
  platform: "node",
  target: "node20",
  format: "cjs",
  sourcemap: false
})
  .then(() => {
    console.log("✅ Build success: dist/index.cjs created");
  })
  .catch((err) => {
    console.error("❌ Build failed", err);
    process.exit(1);
  });
