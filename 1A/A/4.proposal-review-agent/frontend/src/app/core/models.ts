// Wire types. Mirror backend/app/domain/*.py and the chat wire format in app/services/chat.py.

export type Severity = 'hard' | 'flexible';
export type RuleStatus = 'draft' | 'active' | 'retired';
export type VerdictLabel = 'COMPLIANT' | 'CONDITIONALLY_COMPLIANT' | 'NON_COMPLIANT' | 'NEEDS_MORE_INFO';
export type FindingStatus = 'satisfied' | 'violated' | 'unclear' | 'not_applicable';

export interface Me {
  user_id: string;
  role: 'admin' | 'user';
  kind: 'human' | 'service';
  adk_web: boolean;
  auth_mode: 'dev' | 'iap';
}

export interface RuleIn {
  code?: string | null;
  title: string;
  statement: string;
  severity: Severity;
  category: string;
  rationale?: string;
  exception_process?: string;
  source_document_id?: string;
  source_ref?: string;
  status?: RuleStatus;
}

export interface Rule extends RuleIn {
  id: string;
  code: string;
  version: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface RuleVersion {
  version: number;
  changed_by: string;
  change_note: string;
  changed_at: string;
}

export interface DocumentRecord {
  id: string;
  title: string;
  filename: string;
  format: string;
  size_bytes: number;
  category: string;
  tags: string[];
  status: 'processing' | 'ready' | 'failed';
  error: string | null;
  summary: string;
  key_points: string[];
  outline: string[];
  page_count: number | null;
  chunk_count: number;
  extracted_rule_codes: string[];
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface Evidence {
  source: string;
  quote: string;
}

export interface Finding {
  rule_code: string;
  rule_title: string;
  severity: Severity;
  status: FindingStatus;
  reasoning: string;
  evidence: Evidence[];
  remediation: string;
  exception_process: string;
}

export interface Verdict {
  assessment_id: string;
  verdict: VerdictLabel;
  summary: string;
  blocking: string[];
  conditions: string[];
  missing_information: string[];
  findings: Finding[];
  rules_considered: number;
  disclaimer: string;
}

export interface Conversation {
  id: string;
  title: string;
  updated_at: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  verdicts: Verdict[];
  trace?: TraceEvent[];
  attachments?: string[];
}

export interface TraceEvent {
  type: 'tool_call' | 'tool_result';
  author: string;
  name: string;
  args?: Record<string, unknown>;
  result?: unknown;
}

export interface Attachment {
  filename: string;
  mime_type: string;
  data_base64: string;
}

export type StreamEvent =
  | { type: 'session'; session_id: string }
  | TraceEvent
  | { type: 'verdict'; verdict: Verdict }
  | { type: 'delta'; text: string }
  | { type: 'done'; session_id: string; reply: string }
  | { type: 'error'; message: string };
