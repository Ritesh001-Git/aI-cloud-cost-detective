export type Provider = "aws" | "azure" | "gcp";

export interface Scope {
  id: string;
  name: string;
  location?: string;
}

export interface Issue {
  resource_id: string;
  resource_name: string;
  issue_type: string;
  severity: "High" | "Medium" | "Low";
  description: string;
  estimated_savings: number;
  fix_command: string;
}

export interface AnalysisReport {
  summary: string;
  total_estimated_monthly_savings: number;
  issues: Issue[];
  resources_scanned?: number;
  provider?: Provider;
  target_scope?: string;
}

export interface ProgressEvent {
  analysis_id: string;
  status: "running" | "completed" | "failed";
  progress: number;
  provider: Provider;
  target_scope: string;
  message: string;
  result: AnalysisReport | null;
}

export interface HistoryItem {
  id: string;
  provider: Provider;
  target_scope: string;
  resources_scanned: number;
  issues_found: number;
  estimated_savings: number;
  analysis_result: AnalysisReport;
  status: string;
  created_at: string;
}
