PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  node_type TEXT NOT NULL,
  title TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  evidence_status TEXT NOT NULL DEFAULT 'REPORTED',
  canonical INTEGER NOT NULL DEFAULT 0,
  source_ref TEXT,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS edges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL,
  relation TEXT NOT NULL,
  target_id TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  evidence_status TEXT NOT NULL DEFAULT 'REPORTED',
  updated_at TEXT NOT NULL,
  UNIQUE(source_id, relation, target_id),
  FOREIGN KEY(source_id) REFERENCES nodes(id) ON DELETE CASCADE,
  FOREIGN KEY(target_id) REFERENCES nodes(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS memories (
  scope TEXT NOT NULL,
  key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  evidence_status TEXT NOT NULL,
  provenance TEXT,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(scope,key)
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  evidence_status TEXT NOT NULL,
  provenance TEXT,
  ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_title ON nodes(title);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_mem_scope ON memories(scope);
