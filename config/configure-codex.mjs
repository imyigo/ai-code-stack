import fs from 'node:fs';

const [configPath, graphifyCommand] = process.argv.slice(2);
if (!configPath || !graphifyCommand) {
  throw new Error('usage: node config/configure-codex.mjs <config.toml> <graphify-mcp-command>');
}

let text = fs.readFileSync(configPath, 'utf8');
const escaped = graphifyCommand.replaceAll("'", "''");
const section = `[mcp_servers.graphify]
command = '${escaped}'
args = []
startup_timeout_sec = 120
`;

const pattern = /\n?\[mcp_servers\.graphify\][\s\S]*?(?=\n\[[^\]]+\]|\s*$)/m;
if (pattern.test(text)) {
  text = text.replace(pattern, `\n${section}`);
} else {
  text = `${text.trimEnd()}\n\n${section}`;
}
fs.writeFileSync(configPath, text, 'utf8');

