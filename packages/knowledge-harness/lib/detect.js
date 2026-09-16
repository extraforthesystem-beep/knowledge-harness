import { AGENTS, detectAgents, listAgentIds } from "./agents.js";

export function printDetect(log = console.log) {
  const detected = detectAgents();
  log("Detected agents:");
  for (const id of listAgentIds()) {
    const on = detected.includes(id);
    log(`  ${on ? "✓" : "·"} ${id} — ${AGENTS[id].label}`);
  }
  if (!detected.length) {
    log("\nNo agents detected yet. Install anyway with:");
    log("  npx knowledge-harness install -g -y -a claude-code -a cursor -a opencode -a antigravity");
  } else {
    log(`\nInstall: npx knowledge-harness install -g -y`);
  }
}
