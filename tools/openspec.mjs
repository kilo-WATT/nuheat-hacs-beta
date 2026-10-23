// Keep specification tooling and its configuration local to this checkout.
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const result = spawnSync(
  process.execPath,
  [join(root, "node_modules/@fission-ai/openspec/bin/openspec.js"), ...process.argv.slice(2)],
  {
    cwd: root,
    stdio: "inherit",
    env: {
      ...process.env,
      OPENSPEC_TELEMETRY: "0",
      DO_NOT_TRACK: "1",
      OPENSPEC_NO_UPDATE_CHECK: "1",
      XDG_CONFIG_HOME: join(root, "node_modules/.cache/nuheat-openspec"),
    },
  },
);
if (result.error) {
  console.error(result.error.message);
  process.exit(1);
}
process.exit(result.status ?? 1);
