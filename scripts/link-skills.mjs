#!/usr/bin/env node

import { lstatSync, mkdirSync, realpathSync, statSync, symlinkSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = dirname(dirname(fileURLToPath(import.meta.url)));
const sourceDir = join(rootDir, ".agents", "skills");
const linkPath = join(rootDir, ".claude", "skills");

try {
  let sourceStats;
  try {
    sourceStats = statSync(sourceDir);
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
    throw new Error("Missing .agents/skills. Install the agent skills before linking them.");
  }
  if (!sourceStats.isDirectory()) {
    throw new Error(".agents/skills must be a directory.");
  }

  let existing;
  try {
    existing = lstatSync(linkPath);
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }

  if (existing) {
    let correctLink = false;
    if (existing.isSymbolicLink()) {
      try {
        correctLink = realpathSync(linkPath) === realpathSync(sourceDir);
      } catch (error) {
        if (error.code !== "ENOENT") throw error;
      }
    }
    if (!correctLink) {
      throw new Error("Refusing to replace existing .claude/skills. Move it aside before retrying.");
    }
    console.log(".claude/skills already links to .agents/skills.");
  } else {
    mkdirSync(dirname(linkPath), { recursive: true });
    const windows = process.platform === "win32";
    const target = windows ? sourceDir : relative(dirname(linkPath), sourceDir);
    symlinkSync(target, linkPath, windows ? "junction" : "dir");
    console.log("Linked .claude/skills -> .agents/skills.");
  }
} catch (error) {
  console.error(`Cannot link skills: ${error.message}`);
  process.exitCode = 1;
}
