#!/usr/bin/env node
const { Stagehand } = require("@browserbasehq/stagehand");
const dotenv = require("dotenv");

dotenv.config();

async function main() {
  const task = process.argv.slice(2).join(" ") || "Hello from Stagehand";
  try {
    const stagehand = new Stagehand();
    const result = await stagehand.act({ action: task });
    const payload = {
      success: true,
      result,
      error: null,
    };
    console.log(JSON.stringify(payload));
    process.exit(0);
  } catch (err) {
    const payload = {
      success: false,
      result: null,
      error: err && err.message ? err.message : String(err),
    };
    console.log(JSON.stringify(payload));
    process.exit(1);
  }
}

main();
